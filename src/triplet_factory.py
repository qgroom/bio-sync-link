import csv
import requests

sah_endpoint = "https://www.ebi.ac.uk/ena/sah/api/validate"
ena_endpoint = 'https://www.ebi.ac.uk/ena/portal/api/search?result=sequence&fields=all&limit=10&format=json&query=specimen_voucher='


def search_triplet(row):
    col_triplet, space_triplet = build_triplet(row)
    if col_triplet:
        result = requests.get(ena_endpoint+col_triplet).json()
        print(result)


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


def build_triplet(row):
    institution = row[20].replace('"', '')
    collection = row[21].replace('"', '')
    unit = row[22].replace('"', '')
    return assemble_triplet(translate_institution(institution), collection, unit, ":"), assemble_triplet(institution,
                                                                                                         collection,
                                                                                                         unit, " ")


def assemble_triplet(institution, collection, unit, delimiter):
    institution = translate_institution(institution.replace('\\N', ''))
    collection = collection.replace('\\N', '')
    unit = unit.replace('\\N', '')

    if not institution or not unit:
        return ''

    if collection:
        return institution + delimiter + collection + delimiter + unit
    return institution + delimiter + unit


def translate_institution(institution):
    with open("../institutions.csv", 'r') as file:
        reader = csv.reader(file)
        institution_dict = {}
        for row in reader:
            institution_dict[row[0]] = row[4]
    translated = institution_dict.get(institution)
    if institution not in institution_dict or translated == '#N/A':
        return ''
    if institution != translated:
        print(institution, " -> ", translated)
    return institution_dict.get(institution)
