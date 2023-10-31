import requests
import csv

sah_endpoint = "https://www.ebi.ac.uk/ena/sah/api/validate"


def validate_triplet(org, collection, catalog_id, ggbn_id):
    params = {
        "value": encode_triplet(org, collection, catalog_id),
        "qualifier_type": "specimen_voucher"
    }
    r = requests.get(sah_endpoint, params).json()
    return capture_errors(r, org, collection, catalog_id, ggbn_id)


def capture_errors(results, org, collection, catalog_id, ggbn_id):
    if not results["success"]:
        with open("tripletErrors.csv", 'a+') as error_file:
            writer = csv.writer(error_file)
            writer.writerow([org, collection, catalog_id, ggbn_id])
        return False
    return True


def encode_triplet(org, collection, catalog_id):
    if collection:
        return org + ":" + collection + ":" + catalog_id
    return org + ":" + catalog_id
