from pathlib import Path

# Пути к директориям
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = 'downloads'
LOGS_DIR = 'logs'
RESULTS_DIR = 'results'

# URL-адреса
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
WHATS_NEW_URL = 'https://docs.python.org/3/whatsnew/'

# Форматы даты и времени
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
READABLE_DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

# Формат логов
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

# Типы вывода
PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

# Ожидаемые статусы PEP
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
