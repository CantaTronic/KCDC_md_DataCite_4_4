
import os
import json
from glob import glob

JSON_DIR = 'md_json'
INFO_DIR = 'technical_info'

def process_file(filename):
    with open(filename) as f:
        txt = f.read()
    json_name = os.path.basename(filename)[:-4] + '.md.json'
    json_name = os.path.join(JSON_DIR, json_name)
    with open(json_name) as f:
        md = json.load(f)
    for info in md['Description']:
        if info['descriptionType'] == 'TechnicalInfo':
            break
    else:
        raise ValueError
    if info['value'] != txt:
        print(json_name)
        info['value'] = txt
        with open(json_name, 'w') as f:
            print(json.dumps(md, indent=4, ensure_ascii=False), file=f)

def main():
    for filename in glob(os.path.join(INFO_DIR, '*.txt')):
        try:
            process_file(filename)
        except Exception:
            continue

if __name__ == '__main__':
    main()
