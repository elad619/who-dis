import json
import math
import pprint
from typing import Dict

import pandas as pd
import numpy as np

json_path = r"C:\Users\adirdayan\PycharmProjects\who-dis\vt-metadata\conti_vt_metadata.jsonl"
# json_path = r"C:\Users\adirdayan\PycharmProjects\who-dis\vt-metadata\7ev3n_vt_metadata.json"

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


if __name__ == '__main__':
    df = pd.read_json(json_path, lines=True)
    df.set_index("_id")
    df = df.apply(lambda row: pd.Series(extract_features_from_vt_json(row.to_dict()), dtype=float).append(row["_id"]), axis=1)
    print(df)

    # dct = df.iloc[0].to_dict()
    # print(dct)

    # print(retrieve_value_of_nested_key("pe_info.overlay.size", dct))
    # pprint.pprint(extract_features_from_vt_json(dct))
