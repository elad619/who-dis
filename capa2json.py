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
MBC_NAMESPACE = "MBC Objective"
MATCHES_PATTERN = "\((\d+) matches\)"
MBC_TECHNIQUE_PATTERN = "\[(\w\d+)[\.]{0,1}([\d\w]{0,})\]"

FILE_ID = "sha256"
CAPAS_KEY_NAME = "capas"
MBCS_OBJS_KEY_NAME = "mbc"
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

@dataclass
class MBCRule:
    objective:str
    behavior:str
    tehchnique_major:str
    tehchnique_minor:str
    
    def to_dict(self):
        return dataclasses.asdict(self)
    

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

def slice_mbcs(capa_list: List[CapaRule]):
    """
    Get the capabilities from a list of an unparsed capa lines
    :param capa_list: the list of capas
    :return: parsed capabilities lists
    """
    mbcs = []
    current_mbc_name = None
    start_mbc=False
    for i, capa_rule in enumerate(capa_list):
        if capa_rule.rule == CAPABILITY_NAMESPACE:
            start_mbc = False
        if start_mbc:
            if capa_rule.rule:
                current_mbc_name = capa_rule.rule
            techniques = re.findall(MBC_TECHNIQUE_PATTERN, capa_rule.namespace)
            technique_major=techniques[0][0]
            technique_minor=techniques[0][1]
            mbcs.append(MBCRule(current_mbc_name, capa_rule.namespace, technique_major, technique_minor))
        if capa_rule.rule == MBC_NAMESPACE:
            start_mbc = True

            
    return mbcs

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
    mbcs = slice_mbcs(lines_dict)

    capas_json = {FILE_ID: file_id, CAPAS_KEY_NAME: [capa_rule.to_dict() for capa_rule in capas],
                  MBCS_OBJS_KEY_NAME:[mbc.to_dict() for mbc in mbcs]}

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
