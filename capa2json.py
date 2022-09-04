"""
Description:
    A script to convert an output file of CAPA to a json file
"""
import json
import os
from sys import argv
import re

CAPABILITY_NAMESPACE = "CAPABILITY"
MATCHES_PATTERN = r"\((\d+) matches\)"
FILE_ID = "sha256"
CAPAS_KEY_NAME = "capas"

OUT_FILE_SUFFIX = "json"


def show_usage():
    print(f"Usage: ./{os.path.basename(__file__)} [input_file] [output_file]")


def tuple_dict_get(tuple_dict, key):
    """
    Get the value of a key from a tuple dictionary
    :param tuple_dict: the dictionary of tuples to retrieve the value from
    :param key: the key to retrieve the value of
    :return: the value of the key
    """
    for item in tuple_dict:
        if len(item) == 2 and item[0] == key:
            return item[1]


def get_capabilities(capa_list):
    """
    Get the capabilities from a list of an unparsed capa lines
    :param capa_list: the list of capas
    :return: parsed capabilities lists
    """
    return capa_list[([item[0] for item in capa_list].index(""))+1:]


def main(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist")
        return

    with open(input_file, "r") as capa_file:
        capa_content = capa_file.readlines()

    lines_dict = []
    for line in capa_content:
        line = line.split("|")
        if len(line) == 4:
            key, value = line[1].strip(), line[2].strip()

            if re.match(MATCHES_PATTERN, key):
                matches = re.findall(MATCHES_PATTERN, key)[0]
                key = key[:key.rfind("(")].strip()
            else:
                matches = 1

            lines_dict.append((key, matches, value))

    file_id = tuple_dict_get(lines_dict, FILE_ID)
    capas = get_capabilities(lines_dict)

    capas_json = {FILE_ID: file_id, CAPAS_KEY_NAME: capas}

    with open(f"{output_file}.{OUT_FILE_SUFFIX}", "w") as output_file:
        json.dump(capas_json, output_file, indent=4)


if __name__ == "__main__":
    if len(argv[1:]) == 2:
        main(argv[1], argv[2])
    elif len(argv[1:]) == 1:
        main(argv[1], os.path.basename(argv[0]))
    else:
        show_usage()
