import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from constants import PEP_URL
from exceptions import ParserFindTagException


def extract_pep_link(row):
    link_tag = find_tag(row, 'a')
    return urljoin(PEP_URL, link_tag['href'])


def extract_pep_status(soup):
    pep_tag = find_tag(soup, 'dl',
                       attrs={'class': 'rfc2822 field-list simple'})
    full_status_pep = (pep_tag.text).split()
    return full_status_pep[full_status_pep.index('Status:') + 1]


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_response(session, url, encoding='utf-8'):
    response = session.get(url)
    response.encoding = encoding
    response.raise_for_status()
    return response


def get_soup(session, url):
    response = get_response(session, url)
    return BeautifulSoup(response.text, features='lxml')
