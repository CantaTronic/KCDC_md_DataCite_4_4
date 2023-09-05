
import json
import yaml
from glob import glob
import requests
from bs4 import BeautifulSoup
from KCDC_MD import fill_md

URL = 'https://kcdc.iap.kit.edu'

def download_preselections():
    print('Downloading...')
    with open('preselections.html') as f:
        parsed = BeautifulSoup(f.read(), 'html.parser')
    for tag in parsed.find_all('a'):
        if tag.get_text().strip() != 'details': continue
        print(tag['href'])
        response = requests.get(f"{URL}{tag['href']}", stream=True)
        if response.status_code != 200:
            print(response.status_code)
            continue
        filename = tag['href'].rpartition('/')[2]
        pdf_name = f"preselections/{filename}"
        with open(pdf_name, 'wb') as f:
            for chunk in response:
                f.write(chunk)
        #break

def parse_preselections():
    print('Parsing...')
    for filename in glob('preselections/*.pdf'):
        print(filename)
        md = fill_md(filename)
        print(md['Description'][2]['value'])
        filename = filename.rpartition('/')[2].rpartition('.')[0]
        if 'Samnple' in filename:
            filename = filename.replace('Samnple', 'Sample')
        with open(f'md_json/{filename}.md.json', 'w') as f:
            print(json.dumps(md, indent=4, ensure_ascii=False), file=f)
        with open(f'md_yaml/{filename}.md.yml', 'w') as f:
            yaml.dump(md, f)

def parse_descriptions():
    parsed_descr = {}
    with open('preselections.html') as f:
        parsed = BeautifulSoup(f.read(), 'html.parser')
    for tr in parsed.find_all('tr'):
        descr = tr.td.get_text().strip()
        if descr == 'Data sets': continue
        filename = descr.split('\n')[0].strip()
        if filename == '': continue
        if filename.endswith('x'): filename = filename.rpartition('_')[0]
        descr = '\n'.join(i.strip() for i in descr.split('\n')[1:] if i.strip() != '')
        parsed_descr[filename] = descr
    files = []
    for filename in glob('md_json/*.md.json'):
        filename = filename.rpartition('/')[2]
        descr = None
        for k in parsed_descr:
            if filename.startswith(k):
                descr = parsed_descr[k]
                break
        if descr is None:
            print(filename)
            continue
        file_format = filename.rpartition('_')[2].partition('.')[0]
        descr += f'\nFile format: {file_format}'
        files.append({
            'name': filename,
            'path': f'/experimental/{filename}',
            'description': descr,
        })
        with open('experimental.json', 'w') as f:
            print(json.dumps(files, indent=4, ensure_ascii=False), file=f)

if __name__ == '__main__':
    #download_preselections()
    #parse_preselections()
    parse_descriptions()
