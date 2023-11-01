import requests
import csv

sah_endpoint = "https://www.ebi.ac.uk/ena/sah/api/validate"


def validate_triplet(triplet, ggbn_id):
    params = {
        "value": triplet,
        "qualifier_type": "specimen_voucher"
    }
    r = requests.get(sah_endpoint, params).json()
    return capture_errors(r, triplet, ggbn_id)


def capture_errors(results, triplet, ggbn_id):
    if not results["success"]:
        with open("tripletErrors.csv", 'a+') as error_file:
            writer = csv.writer(error_file)
            writer.writerow([triplet, ggbn_id])
        return False
    return True
