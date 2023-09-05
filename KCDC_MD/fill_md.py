
from datetime import datetime
from .dummy_schema import md
from .extract_text import extract_text

def _iter_text(txt: str):
    for ln in txt.split('\n'):
        yield ln.strip()

def _get_toc(txt: str):
    is_started = False
    rec = ''
    for ln in _iter_text(txt):
        if 'Data file names / sizes' in ln:
            is_started = True
        if not is_started: continue
        if ln == '': continue
        if 'Creation date' in ln: break
        if not ln.startswith('/'):
            rec = ln
        else:
            ln = ln[1:].strip()
            rec = f'{rec} / {ln}'
            yield rec

def _get_setup_md(txt, start_ln):
    row = []
    empty_lines = 0
    started = False
    for ln in _iter_text(txt):
        if ln == start_ln:
            started = True
            continue
        if not started:
            continue
        if 'quantities selected' in ln \
        or ln == 'remark':
            if len(row) != 0:
                yield '\t'.join(row)
            break
        if ln == '':
            empty_lines += 1
        else:
            empty_lines = 0
        if empty_lines == 2:
            if len(row) != 0:
                yield '\t'.join(row)
            break
        row.append(ln)
        if len(row) == 4:
            yield '\t'.join(row)
            row = []

def _get_remark(txt):
    started = False
    for ln in _iter_text(txt):
        if ln == 'remark':
            started = True
        if not started:
            continue
        if ln != '':
            yield ln

def _get_technical_info(txt):
    is_started = False
    for ln in _iter_text(txt):
        if 'quantities selected' in ln:
            yield ln + '\n' + '\n'.join(_get_setup_md(txt, ln))
        if ln == 'remark':
            yield '\n'.join(_get_remark(txt))

def fill_md(filename: str):
    txt = extract_text(filename=filename)
    lines = _iter_text(txt)
    md['Title']['value'] = next(lines)
    for ln in lines:
        if 'Creation date' in ln:
            date = next(lines)
            try:
                date = datetime.strptime(date, '%d.%m.%Y').date()
            except ValueError:
                date = date.replace('..', '.')
                date = datetime.strptime(date, '%d.%m.%Y').date()
            md['Date']['value'] = date.isoformat()
            md['PublicationYear'] = date.year
        if 'Data selection' in ln:
            version = next(lines)
            md['Version'] = version
            md['Date']['dateInformation'] = f'Data selection {version}'
        if 'Data format' in ln:
            md['Format'] = next(lines)
        if 'Application' in ln:
            md['Description'][0]['value'] = next(lines)
        if 'Data file names / sizes' in ln:
            md['Description'][1]['value'] = '\n'.join(_get_toc(txt))
    md['Description'][2]['value'] = '\n\n'.join(_get_technical_info(txt))
    return md
