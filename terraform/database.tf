variable "default_read_capacity" {
    type = string
    default = "5"
}

variable "default_write_capacity" {
    type = string
    default = "5"
}


resource "aws_dynamodb_table" "Jobs_Table" {
    name = "Jobs"
    hash_key = "Id"
    range_key = "PracticeCode"

    attribute {
        name = "Id"
        type = "S"
    }

    attribute {
        name = "PracticeCode"
        type = "S"
    }

    billing_mode = "PROVISIONED"
    read_capacity = var.default_read_capacity
    write_capacity = var.default_write_capacity
    stream_enabled = false
}


resource "aws_dynamodb_table" "Jobs_Stats_Table" {
    name = "JobStats"
    hash_key = "JobId"

    attribute {
        name = "JobId"
        type = "S"
    }

    billing_mode = "PROVISIONED"
    read_capacity = var.default_read_capacity
    write_capacity = var.default_write_capacity
    stream_enabled = false
}


resource "aws_dynamodb_table" "In_Flight_Table" {
    name = "InFlight"
    hash_key = "JobId"

    attribute {
        name = "JobId"
        type = "S"
    }

    billing_mode = "PROVISIONED"
    read_capacity = var.default_read_capacity
    write_capacity = var.default_write_capacity
    stream_enabled = false
}


resource "aws_dynamodb_table" "Demographics_Table" {
    name = "Demographics"
    hash_key = "Id"
    range_key = "JobId"

    attribute {
        name = "Id"
        type = "S"
    }

    attribute {
        name = "JobId"
        type = "S"
    }

    billing_mode = "PROVISIONED"
    read_capacity = var.default_read_capacity
    write_capacity = var.default_write_capacity
    stream_enabled = false
}


resource "aws_dynamodb_table" "Demographics_Differences_Table" {
    name = "DemographicsDifferences"
    hash_key = "Id"
    range_key = "JobId"

    attribute {
        name = "Id"
        type = "S"
    }

    attribute {
        name = "JobId"
        type = "S"
    }

    billing_mode = "PROVISIONED"
    read_capacity = var.default_read_capacity
    write_capacity = var.default_write_capacity
    stream_enabled = false
}


resource "aws_dynamodb_table" "Errors_Table" {
    name = "Errors"
    hash_key = "Id"
    range_key = "JobId"

    attribute {
        name = "Id"
        type = "S"
    }
    
    attribute {
        name = "JobId"
        type = "S"
    }

    billing_mode = "PROVISIONED"
    read_capacity = var.default_read_capacity
    write_capacity = var.default_write_capacity
    stream_enabled = false
}


resource "aws_dynamodb_table" "Statuses_Table" {
    name = "Statuses"
    hash_key = "Id"

    attribute {
        name = "Id"
        type = "S"
    }

    billing_mode = "PROVISIONED"
    read_capacity = var.default_read_capacity
    write_capacity = var.default_write_capacity
    stream_enabled = false
}