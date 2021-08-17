import base64
import gzip
import io
import json
import os

import boto3

kinesis = boto3.client("kinesis")
firehose = boto3.client("firehose")


def transformLogEvent(log_event, acct, arn, loggrp, logstrm, filterName):
    """Transform each log event.
    The default implementation below just extracts the message and appends a newline to it.

    Args:
        log_event (dict): The original log event. Structure is {"id": str, "timestamp": long, "message": str}
        acct: The aws account from where the Cloudwatch event came from
        arn: The ARN of the Kinesis Stream
        loggrp: The Cloudwatch log group name
        logstrm: The Cloudwatch logStream name (not used below)
        filterName: The Cloudwatch Subscription filter for the Stream

    Returns:
        str: The transformed log event.
            In the case below, Splunk event details are set as:
            time = event time for the Cloudwatch Log
            host = ARN of Firehose
            source = filterName (of cloudwatch Log) contatinated with LogGroup Name
            sourcetype is set as -
                aws:cloudtrail if the Log Group name contains CloudTrail
                aws:cloudwatchlogs:vpcflow if the Log Group name contains VPC
                the environment variable contents of SPLUNK_SOURCETYPE for all other cases
    """

    if "CloudTrail" in loggrp:
        sourcetype = "aws:cloudtrail"
    elif "VPC" in loggrp:
        sourcetype = "aws:cloudwatchlogs:vpcflow"
    else:
        sourcetype = os.environ["SPLUNK_SOURCETYPE"]

    return json.dumps(
        {
            "time": str(log_event["timestamp"]),
            "host": arn,
            "source": f"{filterName}:{loggrp}",
            "sourcetype": sourcetype,
            "event": json.dumps(log_event["message"]),
        }
    )


def processRecords(records, arn):
    for r in records:
        data = base64.b64decode(r["data"])
        striodata = io.BytesIO(data)
        with gzip.GzipFile(fileobj=striodata, mode="r") as f:
            data = json.loads(f.read())

        recId = r["recordId"]
        """
        CONTROL_MESSAGE are sent by CWL to check if the subscription is reachable.
        They do not contain actual data.
        """
        if data["messageType"] == "CONTROL_MESSAGE":
            yield {"result": "Dropped", "recordId": recId}
        elif data["messageType"] == "DATA_MESSAGE":
            data = "".join(
                [
                    transformLogEvent(
                        e,
                        data["owner"],
                        arn,
                        data["logGroup"],
                        data["logStream"],
                        data["subscriptionFilters"][0],
                    )
                    for e in data["logEvents"]
                ]
            )
            data = base64.b64encode(data.encode("utf-8")).decode()
            yield {"data": data, "result": "Ok", "recordId": recId}
        else:
            yield {"result": "ProcessingFailed", "recordId": recId}


def putRecordsToFirehoseStream(streamName, records, client, attemptsMade, maxAttempts):
    failedRecords = []
    codes = []
    errMsg = ""
    # if put_record_batch throws for whatever reason, response['xx'] will error out, adding a check for a valid
    # response will prevent this
    response = None
    try:
        response = client.put_record_batch(DeliveryStreamName=streamName, Records=records)
    except Exception as e:
        failedRecords = records
        errMsg = str(e)

    # if there are no failedRecords (put_record_batch succeeded), iterate over the response to gather results
    if not failedRecords and response and response["FailedPutCount"] > 0:
        for idx, res in enumerate(response["RequestResponses"]):
            # (if the result does not have a key 'ErrorCode' OR if it does and is empty) => we do not need to re-ingest
            if "ErrorCode" not in res or not res["ErrorCode"]:
                continue

            codes.append(res["ErrorCode"])
            failedRecords.append(records[idx])

        errMsg = "Individual error codes: " + ",".join(codes)

    if len(failedRecords) > 0:
        if attemptsMade + 1 < maxAttempts:
            print(
                "Some records failed while calling PutRecordBatch to Firehose stream, retrying. %s"
                % (errMsg)
            )
            putRecordsToFirehoseStream(
                streamName, failedRecords, client, attemptsMade + 1, maxAttempts
            )
        else:
            raise RuntimeError(
                "Could not put records after %s attempts. %s" % (str(maxAttempts), errMsg)
            )


def putRecordsToKinesisStream(streamName, records, client, attemptsMade, maxAttempts):
    failedRecords = []
    codes = []
    errMsg = ""
    # if put_records throws for whatever reason, response['xx'] will error out, adding a check for a valid
    # response will prevent this
    response = None
    try:
        response = client.put_records(StreamName=streamName, Records=records)
    except Exception as e:
        failedRecords = records
        errMsg = str(e)

    # if there are no failedRecords (put_record_batch succeeded), iterate over the response to gather results
    if not failedRecords and response and response["FailedRecordCount"] > 0:
        for idx, res in enumerate(response["Records"]):
            # (if the result does not have a key 'ErrorCode' OR if it does and is empty) => we do not need to re-ingest
            if "ErrorCode" not in res or not res["ErrorCode"]:
                continue

            codes.append(res["ErrorCode"])
            failedRecords.append(records[idx])

        errMsg = "Individual error codes: " + ",".join(codes)

    if len(failedRecords) > 0:
        if attemptsMade + 1 < maxAttempts:
            print(
                "Some records failed while calling PutRecords to Kinesis stream, retrying. %s"
                % (errMsg)
            )
            putRecordsToKinesisStream(
                streamName, failedRecords, client, attemptsMade + 1, maxAttempts
            )
        else:
            raise RuntimeError(
                "Could not put records after %s attempts. %s" % (str(maxAttempts), errMsg)
            )


def createReingestionRecord(isSas, originalRecord):
    if isSas:
        return {
            "data": base64.b64decode(originalRecord["data"]),
            "partitionKey": originalRecord["kinesisRecordMetadata"]["partitionKey"],
        }
    else:
        return {"data": base64.b64decode(originalRecord["data"])}


def getReingestionRecord(isSas, reIngestionRecord):
    if isSas:
        return {
            "Data": reIngestionRecord["data"],
            "PartitionKey": reIngestionRecord["partitionKey"],
        }
    else:
        return {"Data": reIngestionRecord["data"]}


def handler(event, context):
    isSas = "sourceKinesisStreamArn" in event
    streamARN = event["sourceKinesisStreamArn"] if isSas else event["deliveryStreamArn"]
    streamName = streamARN.split("/")[1]

    records = list(processRecords(event["records"], streamARN))
    projectedSize = 0
    dataByRecordId = {
        rec["recordId"]: createReingestionRecord(isSas, rec) for rec in event["records"]
    }
    putRecordBatches = []
    recordsToReingest = []
    totalRecordsToBeReingested = 0

    for idx, rec in enumerate(records):
        if rec["result"] != "Ok":
            continue
        projectedSize += len(rec["data"]) + len(rec["recordId"])
        # 6000000 instead of 6291456 to leave ample headroom for the stuff we didn't account for
        if projectedSize > 6000000:
            totalRecordsToBeReingested += 1
            recordsToReingest.append(getReingestionRecord(isSas, dataByRecordId[rec["recordId"]]))
            records[idx]["result"] = "Dropped"
            del records[idx]["data"]

        # split out the record batches into multiple groups, 500 records at max per group
        if len(recordsToReingest) == 500:
            putRecordBatches.append(recordsToReingest)
            recordsToReingest = []

    if len(recordsToReingest) > 0:
        # add the last batch
        putRecordBatches.append(recordsToReingest)

    # iterate and call putRecordBatch for each group
    recordsReingestedSoFar = 0
    if len(putRecordBatches) > 0:
        for recordBatch in putRecordBatches:
            if isSas:
                putRecordsToKinesisStream(
                    streamName, recordBatch, kinesis, attemptsMade=0, maxAttempts=20
                )
            else:
                putRecordsToFirehoseStream(
                    streamName, recordBatch, firehose, attemptsMade=0, maxAttempts=20
                )
            recordsReingestedSoFar += len(recordBatch)
            print(
                "Reingested %d/%d records out of %d"
                % (recordsReingestedSoFar, totalRecordsToBeReingested, len(event["records"]))
            )
    else:
        print("No records to be reingested")

    return {"records": records}
