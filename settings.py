from chardet import detect
from datetime import datetime as dt
from pathlib import Path


def get_encoding(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    try:
        encoding_type = detect(rawdata)['encoding']
    except KeyError:
        return 'utf-8'
    return encoding_type if not None else 'utf-8'


this_path = Path('settings.py')
MODULE_PATH = this_path.parent
ERRORS = Path.joinpath(MODULE_PATH, 'Errors')
INPUT_FOLDER = Path.joinpath(MODULE_PATH, 'Input')
OUTPUT_FOLDER = Path.joinpath(MODULE_PATH, 'Output')
RAW_OUTPUT_FOLDER = Path.joinpath(MODULE_PATH, 'RawOutput')
TIMESTAMP = dt.now().strftime("%A, %d %b %Y")
MISSING_KWD_FILE = ERRORS / ('missing_kwds-' + TIMESTAMP + '.csv')
