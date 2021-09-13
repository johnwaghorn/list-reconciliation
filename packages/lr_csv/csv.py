import csv
import io


def write_to_mem_csv(rows: list[dict], header: list[str]) -> io.StringIO:
    """Writes a list of rows and header to an in-memory CSV string.

    Args:
        rows (List[Dict]): List of records to add to the CSV.
        header (List[str]): Header to add to the CSV.

    Returns:
        io.StringIO(): CSV string
    """
    stream = io.StringIO(newline=None)
    writer = csv.DictWriter(stream, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)

    return stream
