resource "aws_sqs_queue" "Patient_Records_Queue" {
  name                        = "patient_records-${terraform.workspace}.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  delay_seconds               = 0
  max_message_size            = 262144 # 256kb
  message_retention_seconds   = 345600 # 4 days
  visibility_timeout_seconds  = 300
  receive_wait_time_seconds   = 0
}

resource "aws_sqs_queue_policy" "Patient_Records_Queue_Policy" {
  queue_url = aws_sqs_queue.Patient_Records_Queue.id
  policy    = <<EOF
{
      "Version": "2012-10-17",
      "Id": "sqspolicy",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": "*",
          "Action": "SQS:*",
          "Resource": "${aws_sqs_queue.Patient_Records_Queue.arn}",
          "Condition": {
            "ArnEquals": {
              "aws:SourceArn": "${aws_sqs_queue.Patient_Records_Queue.name}"
            }
          }
        }
      ]
  }
  EOF
}

