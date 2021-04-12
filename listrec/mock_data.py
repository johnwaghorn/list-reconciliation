import requests
import sys
import csv
import json
import random
import os


def header(url):
    return json.loads(requests.get(url).content)[0].keys()


def split_header(header):
    """Split header from mock data into PDS and non-PDS columns."""
    gp, pds = [], []

    for col in header:
        if col.startswith("PDS_"):
            pds.append(col.replace("PDS_", ""))
        else:
            gp.append(col)

    return gp, pds


def random_reduce(inlist, pct):
    """Remove items from a list `inlist`, so that `pct`% items remain."""
    k = int(len(inlist) * pct / 100)
    out = random.sample(inlist, k)

    return out


def split_data(data):
    """Split columns from csv into PDS and non-PDS data."""
    pds, gp = [], []
    for d in data:

        gp_dict = {k: v for k, v in d.items() if not k.startswith("PDS_")}

        pds_dict = {}
        for k, v in d.items():
            if k.startswith("PDS_"):
                k = k.replace("PDS_", "")
                if k in ("name", "address", "gender"):
                    v = json.dumps(v)

                pds_dict[k] = v

        gp.append(gp_dict)
        pds.append(pds_dict)

    return gp, pds


def main():
    try:
        url = sys.argv[1]
        num_iter = int(sys.argv[2])
        same_pct = int(sys.argv[3])
        outfile = sys.argv[4]
    except:
        usage = """Hits a mock data `url` multiple `num_times` and outputs two files,
suffixed with gp or pds. The rows in both are sampled so that `same_pct` records
are the same, and the rest are missing from the other file.

Usage:
    mock_data url num_times same_pct outfile

e.g.:
    python mock_data.py https://my.api.mockaroo.com/mock-contact-data?key=7ed6bdb0 10 98 outfile.csv
    """
        print(usage)
        sys.exit()

    outfile_name, ext = os.path.splitext(outfile)

    data = []

    for i in range(num_iter):
        response = requests.get(url)
        data.extend(json.loads(response.content))

    with open(f"{outfile_name}_gp{ext}", "w", newline="\n") as gp, open(
        f"{outfile_name}_pds{ext}", "w", newline="\n"
    ) as pds:

        gp_header, pds_header = split_header(header(url))
        gp_data, pds_data = split_data(data)
        gp_writer = csv.DictWriter(gp, gp_header)
        gp_writer.writeheader()
        gp_writer.writerows(random_reduce(gp_data, same_pct))

        pds_writer = csv.DictWriter(pds, pds_header)
        pds_writer.writeheader()
        pds_writer.writerows(random_reduce(pds_data, same_pct))


if __name__ == "__main__":
    main()
