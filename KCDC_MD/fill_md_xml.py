
from bs4 import BeautifulSoup

def fill_md_xml(md: dict):
    with open('KCDC_MD/dummy_schema.xml') as f:
        xml = f.read()
    xml = BeautifulSoup(xml, 'xml')
    for tag in xml.find_all('title'):
        if 'titleType' not in tag.attrs:
            tag.string = md['Title']['value']
        else:
            tag.string = f"{md['Title']['value']} XML metadata"
    for tag in xml.find_all('date'):
        tag.string = md['Date']['value']
        tag['dateInformation'] = md['Date']['dateInformation']
    xml.find('publicationYear').string = f"{md['PublicationYear']}"
    xml.find('version').string = md['Version']
    for tag in xml.find_all('format'):
        tag.string = md['Format']
    for tag in xml.find_all('size'):
        tag.string = md['Size']
    xml.find('description', descriptionType='Abstract').string = md['Description'][0]['value'] or ''
    xml.find('description', descriptionType='Table of Contents').string = md['Description'][1]['value'] or ''
    xml.find('description', descriptionType='TechnicalInfo').string = md['Description'][2]['value'] or ''
    return xml.prettify()
