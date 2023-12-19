
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
        if 'Data file names /' in ln:
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

def _format_setup_md(md):
    md = list(list(cell.strip() for cell in ln.split('\t')) for ln in md)
    n_cols = max(len(row) for row in md)
    col_widths = list(0 for _ in range(n_cols))
    for row in md:
        if len(row) < n_cols:
            row.extend('' for _ in range(n_cols-len(row)))
        for i_col, cell in enumerate(row):
            if len(cell) > col_widths[i_col]:
                col_widths[i_col] = len(cell)
    hdr = ' | '.join(
        f'{cell: ^{col_widths[i_col]}}' for i_col, cell in enumerate(md[0])
    ) + '\n'
    sep = '-+-'.join(
        '-'*col_w for col_w in col_widths
    ) + '\n'
    txt = hdr + sep + '\n'.join(
        ' | '.join(
            f'{cell: ^{col_widths[i_col]}}' for i_col, cell in enumerate(row)
        ) for row in md[1:]
    )
    return txt

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
            setup_md = list(_get_setup_md(txt, ln))
            yield ln + '\n' + _format_setup_md(setup_md)
        if ln == 'remark':
            yield '\n'.join(_get_remark(txt))

def _get_size(txt: str):
    is_started = False
    rec = ''
    for ln in _iter_text(txt):
        if 'Zip-file' in ln:
            is_started = True
            continue
        if not is_started: continue
        if ln == '': continue
        if 'Data file names / sizes' in ln: break
        if not '/' in ln: continue
        return ln.rpartition('/')[2].strip().replace(',', '.')
    print(txt)
    raise RuntimeError('Can\'t extract file size')

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
        if 'Data file names /' in ln:
            md['Description'][1]['value'] = '\n'.join(_get_toc(txt))
    md['Size'] = _get_size(txt)
    md['Description'][2]['value'] = '\n\n'.join(_get_technical_info(txt))
    return md
