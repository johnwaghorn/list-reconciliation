# Firehose Transform

For processing data sent to Firehose by Cloudwatch Logs subscription filters.

Additional processing of message into format for Splunk HTTP Event Collector - Event input (not Raw)

## Cloudwatch

Cloudwatch Logs sends to Firehose records that look like this:

```
{
  "messageType": "DATA_MESSAGE",
  "owner": "123456789012",
  "logGroup": "log_group_name",
  "logStream": "log_stream_name",
  "subscriptionFilters": [
    "subscription_filter_name"
  ],
  "logEvents": [
    {
      "id": "01234567890123456789012345678901234567890123456789012345",
      "timestamp": 1510109208016,
      "message": "log message 1"
    },
    {
      "id": "01234567890123456789012345678901234567890123456789012345",
      "timestamp": 1510109208017,
      "message": "log message 2"
    }
    ...
  ]
}
```

The data is additionally compressed with GZIP.

## This Lambda

1. Gunzip the data
1. Parse the json
1. Set the result to ProcessingFailed for any record whose messageType is not DATA_MESSAGE, thus redirecting them to the processing error output. Such records do not contain any log events. You can modify the code to set the result to Dropped instead to get rid of these records completely.
1. For records whose messageType is DATA_MESSAGE, extract the individual log events from the logEvents field, and pass each one to the transformLogEvent method. You can modify the transformLogEvent method to perform custom transformations on the log events.
1. Concatenate the result from (4) together and set the result as the data of the record returned to Firehose. Note that this step will not add any delimiters. Delimiters should be appended by the logic within the transformLogEvent method.
1. Any additional records which exceed 6MB will be re-ingested back into Firehose.
