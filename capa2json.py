"""
Description:
    A script to convert an output file of CAPA to a json file
"""
from dataclasses import dataclass
import dataclasses
import json
import os
from pathlib import Path
from sys import argv
import re
from typing import List
from tqdm import tqdm

CAPABILITY_NAMESPACE = "CAPABILITY"
MATCHES_PATTERN = "\((\d+) matches\)"
FILE_ID = "sha256"
CAPAS_KEY_NAME = "capas"

OUT_FILE_SUFFIX = "json"


def show_usage():
    print(f"Usage: ./{os.path.basename(__file__)} [input_file] [output_file]")

@dataclass
class CapaRule:
    rule:str
    matches:int
    namespace:str
    
    def to_dict(self):
        return dataclasses.asdict(self)

# class CapaRule:
#     def __init__(self, rule, matches, namespace) -> None:
#         self.rule = rule
#         self.matches = matches
#         self.namespace = namespace
    
#     def to_dict(self) -> dict:
#         """
#         Converts the CapaRule into a dictionary
#         """
#         return {
#             "rule" : self.rule,
#             "matches" : self.matches,
#             "namespace" : self.namespace
#         }

def get_rule_by_key(capa_rules: List[CapaRule], key: str):
    """
    Get the value of a key from a list 
    :param capa_rules: the capa rules list
    :param key: the key to retrieve the value of
    :return: the value of the key
    """
    for capa_rule in capa_rules:
        if capa_rule.rule == key:
            return capa_rule.namespace


def get_capabilities(capa_list: List[CapaRule]):
    """
    Get the capabilities from a list of an unparsed capa lines
    :param capa_list: the list of capas
    :return: parsed capabilities lists
    """
    index = 0 
    for i, capa_rule in enumerate(capa_list):
        if capa_rule.rule == CAPABILITY_NAMESPACE:
            index = i
            break
    return capa_list[index+1:]

def capa_to_json(input_file, output_file):
    with open(input_file, "r") as capa_file:
        capa_content = capa_file.readlines()

    lines_dict = []
    for line in capa_content:
        line = line.split("|")
        if len(line) == 4:
            rule, namespace = line[1].strip(), line[2].strip()

            if matches:=re.findall(MATCHES_PATTERN, rule):
                matches = int(matches[0])
                rule = rule[:rule.rfind("(")].strip()
            else:
                matches = 1

            lines_dict.append(CapaRule(rule, matches, namespace))

    file_id = get_rule_by_key(lines_dict, FILE_ID)
    capas = get_capabilities(lines_dict)

    capas_json = {FILE_ID: file_id, CAPAS_KEY_NAME: [capa_rule.to_dict() for capa_rule in capas]}

    with open(f"{output_file}.{OUT_FILE_SUFFIX}", "w") as output_file:
        json.dump(capas_json, output_file, indent=4)


def main(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist")
        return
    
    if os.path.isdir(input_file):
        p=Path(input_file)
        for txt_file in tqdm(p.rglob("*.txt")):
            current_output_file = (Path(output_file)/txt_file.relative_to(p))
            current_output_file.parent.mkdir(parents=True, exist_ok=True)
            current_output_file = str(current_output_file).replace('.txt','.json')
            capa_to_json(txt_file, current_output_file)
    else:
        capa_to_json(input_file, output_file)
    
   


if __name__ == "__main__":
    if len(argv[1:]) == 2:
        main(argv[1], argv[2])
    elif len(argv[1:]) == 1:
            main(argv[1], os.path.abspath(argv[0]))
    else:
        show_usage()
