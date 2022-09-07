import json
import math
import pprint
from typing import Dict

import pandas as pd
import numpy as np

json_path = r"/vt_metadata\conti_vt_metadata.jsonl"
# json_path = r"C:\Users\adirdayan\PycharmProjects\who-dis\vt_metadata\7ev3n_vt_metadata.json"

# with open(json_path) as json_file:
#     dct = json.load(json_file)



existing_numerical_features = [
    # 'exiftool.Timestamp',
    "pe_info.timestamp",
    'exiftool.CodeSize',
    'exiftool.LinkerVersion',
    'total_votes.harmless',
    'total_votes.malicious',
    # 'tlsh',
    # 'vhash',
    # 'capabilities_tags',
    # 'ssdeep',
    # 'pe_info.resource_langs',
    # 'pe_info.import_list',
    # 'pe_info.overlay.entropy',
    # 'pe_info.compiler_product_versions',
    # 'pe_info.sections.virtual_size',
    'pe_info.overlay.size',
    'size',
    'times_submitted',
    'reputation',
    'unique_sources',
    'first_submission_date',
    'last_analysis_stats.harmless',
    'last_analysis_stats.type-unsupported',
    'last_analysis_stats.suspicious',
    'last_analysis_stats.confirmed-timeout',
    'last_analysis_stats.timeout',
    'last_analysis_stats.failure',
    'last_analysis_stats.malicious',
    'last_analysis_stats.undetected',
]
def retrieve_value_of_nested_key(nested_key: str, dct: Dict):
    value = dct.copy()
    for key in nested_key.split("."):
        if isinstance(value, list):
            print(value)
            assert key.isdigit(), "invalid nested key"
            if len(value) == 0:
                value = value.get(int(key))
                # value = value[int(key)]
        else:
            value = value.get(key)
            # value = value[key]
        if (value is None) or (type(value) == float and math.isnan(value)):
            return None
    return value


def extract_features_from_vt_json(vt_json: Dict) -> Dict:
    # print(vt_json)
    features_json = {}

    for key in existing_numerical_features:
        # print(key)
        features_json[key] = retrieve_value_of_nested_key(key, vt_json)
    return features_json

def load_family_vt_meta_data(file_path):
    df = pd.read_json(file_path, lines=True)
    ids = df["_id"]
    df = df.apply(lambda row: pd.Series(extract_features_from_vt_json(row.to_dict()), dtype=float), axis=1)
    df = df.set_index(ids)
    return df



if __name__ == '__main__':
    families = [
        "7ev3n_vt_metadata.json",
        "conti_vt_metadata.jsonl",
        "emotet_vt_metadata.jsonl",
        "orcus_vt_metadata.jsonl",
        "sugar_ransomware_vt_metadata.jsonl",
        "cozy_and_veno_vt_metadata.jsonl"
    ]

    df = pd.concat([load_family_vt_meta_data(apt) for apt in families])
    # df = pd.read_json("cozy_and_veno_vt_metadata.jsonl", lines=True)
    print(df)



    # dct = df.iloc[0].to_dict()
    # print(dct)

    # print(retrieve_value_of_nested_key("pe_info.overlay.size", dct))
    # pprint.pprint(extract_features_from_vt_json(dct))
