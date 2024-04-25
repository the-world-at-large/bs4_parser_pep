from pathlib import Path

BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = 'downloads'
LOG_DIR = 'logs'
RESULTS_DIR = 'results'

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
WHATS_NEW_URL = 'https://docs.python.org/3/whatsnew/'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

OUTPUT_CHOICES = ('pretty', 'file')

PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
