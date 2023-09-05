
import fitz

def extract_text(filename=None, stream=None):
    try:
        with fitz.open(filename=filename, stream=stream) as pdf:
            return '\n'.join(page.get_text() for page in pdf)
    except fitz.FileDataError:
        raise fitz.FileDataError('Загруженный файл не был распознан как pdf-файл')
