
import os
import json
from glob import glob

JSON_DIR = 'md_json'
INFO_DIR = 'technical_info'

def process_file(filename):
    with open(filename) as f:
        md = json.load(f)
    for info in md['Description']:
        if info['descriptionType'] == 'TechnicalInfo':
            break
    else:
        raise ValueError
    info_name = os.path.basename(filename)[:-8] + '.txt'
    with open(os.path.join(INFO_DIR, info_name), 'w') as f:
        f.write(info['value'])

def main():
    if not os.path.exists(INFO_DIR):
        os.makedirs(INFO_DIR)
    for filename in glob(os.path.join(JSON_DIR, '*.md.json')):
        try:
            process_file(filename)
        except Exception:
            continue

if __name__ == '__main__':
    main()
