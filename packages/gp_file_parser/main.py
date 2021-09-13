import argparse
import datetime
import logging
from datetime import datetime

from gp_file_parser.file_name_parser import InvalidFilename
from gp_file_parser.parser import LOG, InvalidGPExtract, process_gp_extract


def main():
    parser = argparse.ArgumentParser("gpextract")
    parser.add_argument(
        "out_dir",
        type=str,
        help="Output directory, will contain the files 'records.csv' and 'invalid_counts.csv",
    )

    parser.add_argument("files", type=str, help="List of GP extract files to be processed")

    parser.add_argument(
        "-t",
        "--invalid_threshold",
        type=int,
        default=10,
        help="Minimum number of invalid records to cause the program to reject "
        "the GP extract and output only invalid records.",
    )

    parser.add_argument(
        "-r",
        "--include_reason",
        action="store_true",
        help="Outputs a verbose reason for validation failures for each record. "
        "If not set, only the column names failing validation are included.",
    )
    parser.add_argument(
        "--process_date",
        type=lambda x: datetime.strptime(x, "%Y%m%d"),
        default=datetime.now(),
        help="Set the processing datetime. (default: today's date)",
    )

    parser.add_argument("-d", "--debug", action="store_true", help="Set logging level to debug")
    args = parser.parse_args()

    if args.debug:
        LOG.setLevel(logging.DEBUG)
        log_format = (
            "%(asctime)s|%(levelname)s|%(process)d|%(module)s@%(lineno)s:"
            "%(funcName)s %(message)s"
        )
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)
        log_format = "%(message)s"
        logging.basicConfig(format=log_format, level=logging.INFO)

    try:
        process_gp_extract(
            args.files,
            args.out_dir,
            include_reason=args.include_reason,
            invalid_threshold=args.invalid_threshold,
            process_datetime=args.process_date,
        )
    except (InvalidGPExtract, InvalidFilename) as err:
        print(err)
        print("Failed")
    else:
        print("Success")


if __name__ == "__main__":
    main()
