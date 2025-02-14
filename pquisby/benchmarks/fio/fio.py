import re
import os
import logging
from itertools import groupby

import requests
from bs4 import BeautifulSoup


# TODO: Maybe we can do away with clat, lat, slat
HEADER_TO_EXTRACT = [
    "iops_sec:client_hostname:all",
    "lat:client_hostname:all",
]


def extract_csv_data(csv_data, path):
    indexof_all = []
    results = []
    logging.info(f"extract csv data: {path}")
    header_row = csv_data.pop(0).split(",")

    io_depth = re.findall(r"iod.*?_(\d+)", path)[0]
    ndisks = re.findall(r"ndisks_(\d+)", path)[0]
    njobs = re.findall(r"njobs_(\d+)", path)[0]

    try:
        for header in HEADER_TO_EXTRACT:
            indexof_all.append(header_row.index(header))

        for row in csv_data:
            run_data = []
            if row:
                csv_row = row.split(",")
                for index in indexof_all:
                    run_data.append(csv_row[index])
                results.append([csv_row[1], ndisks, njobs, io_depth, *run_data])
    except ValueError:
        logging.error("Data format incorrect. Skipping data") 
    
    return results


def group_data(run_data, system_name,OS_RELEASE):

    run_metric = {"1024KiB": "iops", "4KiB": "lat", "2300KiB": "iops"}

    grouped_data = []
    for key, items in groupby(sorted(run_data), key=lambda x: x[0].split("-")):

        grouped_data.append([""])
        grouped_data.append(
            [system_name, key[0], f"{key[1]}-{run_metric[key[1]]}"])
        grouped_data.append(
            ["iteration_name", f"{run_metric[key[1]]}-{OS_RELEASE}"])
        for item in items:
            
            row_hash = f"{item[1]}_d-{item[2]}_j-{item[3]}_iod"
            if "1024KiB" in key[1] or "2300KiB" in key[1]:
                grouped_data.append([row_hash, item[4]])
            elif "4KiB" in key[1]:
                grouped_data.append([row_hash, item[5]])
    
    return grouped_data


# TODO: parellelize work
def retreive_data_from_url(URL, page_content):
    results = []

    if page_content:

        for link in page_content[3:]:

            path = link.text.split("/")[0]

            if path:
                csv_data = requests.get(URL + path + "/result.csv")

                results += extract_csv_data(csv_data.text.split("\n"), path)

    return results


def scrape_page(URL):

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    page_content = soup.table.find_all("tr")

    return page_content


def get_system_name_from_url(URL):
    return re.findall(r"instance_(\w+.\w+)_numb", URL)[0]


def process_fio_run_result(URL, system_name):
    # system_name = get_system_name_from_url(URL)
    page_content = scrape_page(URL)
    results = retreive_data_from_url(URL, page_content)

    return group_data(results, system_name)


def extract_fio_run_data(path, system_name,OS_RELEASE):
    results = []

    ls_dir = os.listdir(path)

    with open(path + "/result.csv") as csv_file:
        csv_data = csv_file.readlines()
        csv_data[-1] = csv_data[-1].strip()

        results += extract_csv_data(csv_data, os.path.basename(path))

    return group_data(results, system_name,OS_RELEASE)
