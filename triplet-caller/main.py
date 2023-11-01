import csv
import requests

sah_endpoint = 'https://www.ebi.ac.uk/ena/sah/api/validate'
ena_endpoint = 'https://www.ebi.ac.uk/ena/portal/api/search?result=sequence&fields=all&limit=10&format=json&query=specimen_voucher='


def search_triplet(row, writer):
    col_triplet, space_triplet = build_triplet(row, True)
    if col_triplet:
        if validate_triplet(col_triplet, row[22]):
            print("Valid triplet built")
            results = requests.get(ena_endpoint + '"' + col_triplet + '"').json()
            if len(results) == 1:
                write_positive_match(results[0], row, writer)
                return
            for result in results:
                if result.get('specimen_voucher') == col_triplet or result.get('specimen_voucher') == space_triplet:
                    write_positive_match(result, row, writer)
                    return
        else:
            col_doublet, space_doublet = build_triplet(row, False)
            if validate_triplet(col_doublet, row[22]):
                results = requests.get(ena_endpoint + '"' + col_doublet + '"').json()
                if len(results) == 1:
                    write_positive_match(results[0], row, writer)
                    return
                for result in results:
                    if result.get('specimen_voucher') == col_doublet or result.get('specimen_voucher') == space_doublet:
                        write_positive_match(result, row, writer)
                        return

def write_positive_match(result, row, writer):
    if row[23] == result.get('scientific_name'):
        write_row = {
            'ggbn_unitid': row[22],
            'ena_specimen_voucher': result.get('specimen_voucher'),
            'ggbn_scietific_name': row[23],
            'ena_scientific_name': result.get('scientific_name'),
            'ggbn_country': row[8],
            'ena_country': result.get('country'),
            'ggbn_collection_date': row[4],
            'ena_collection_date': result.get('collection_date'),
            'ggbn_collector': row[6],
            'ena_collector': result.get('collected_by')
        }
        print("result found: ", write_row)
        writer.writerow(write_row)


def validate_triplet(triplet, ggbn_id):
    params = {
        "value": triplet,
        "qualifier_type": "specimen_voucher"
    }
    r = requests.get(sah_endpoint, params).json()
    return r["success"]


def build_triplet(row, include_collection):
    institution = row[20].replace('"', '')
    collection = row[21].replace('"', '')
    unit = row[22].replace('"', '')
    return (assemble_triplet(translate_institution(institution), collection, unit, ":", include_collection),
            assemble_triplet(translate_institution(institution), collection, unit, " ", include_collection))


def assemble_triplet(institution, collection, unit, delimiter, include_collection):
    institution = translate_institution(institution.replace('\\N', ''))
    collection = collection.replace('\\N', '')
    unit = unit.replace('\\N', '')

    if not institution or not unit:
        return ''

    if collection and include_collection:
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


def read_csv():
    with open('dump_100k.csv', 'r', encoding='ISO-8859-1') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            yield row


def main():
    with open('triplet_matches.csv', 'w', newline='') as outputfile:
        writer = csv.DictWriter(outputfile, delimiter=',', quotechar='"',
                                fieldnames=['ggbn_unitid', 'ena_specimen_voucher', 'ggbn_scietific_name',
                                            'ena_scientific_name', 'ggbn_country', 'ena_country',
                                            'ggbn_collection_date', 'ena_collection_date', 'ggbn_collector',
                                            'ena_collector'])

        i = 1
        for row in read_csv():
            if i > 1:
                search_triplet(row, writer)
            i = i + 1
            if i > 10000:
                break


if __name__ == '__main__':
    main()
