import json
import pandas as pd

json_path = r"C:\Users\yaara\OneDrive\Desktop\sugar_ransomware_vt_metadata.jsonl"

# with open(json_path) as json_file:
#     data = json.loads(json_file)

df = pd.read_json(json_path, lines=True)
df.head()

