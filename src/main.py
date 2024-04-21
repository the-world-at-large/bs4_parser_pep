import logging
import re
from urllib.parse import urljoin

import requests
import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output, file_output
from utils import (extract_pep_link, extract_pep_status,
                   find_tag, get_response, get_soup)


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})

    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, 'lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось.')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']

        match = re.match(pattern, a_tag.text)
        if match:
            version = match.group('version')
            status = match.group('status')
        else:
            version = a_tag.text.strip()
            status = ''

        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    try:
        response = get_response(session, downloads_url)
        if response is None:
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_a4_tag = find_tag(soup, 'a', attrs={
                                    'href': re.compile(r'.+pdf-a4\.zip$')})

        if pdf_a4_tag:
            pdf_a4_link = urljoin(downloads_url, pdf_a4_tag['href'])

            downloads_dir = BASE_DIR / 'downloads'
            downloads_dir.mkdir(exist_ok=True)

            filename = pdf_a4_link.split('/')[-1]

            archive_path = downloads_dir / filename

            response = session.get(pdf_a4_link)

            with open(archive_path, 'wb') as file:
                file.write(response.content)

            print("Архив успешно загружен и сохранен по пути:", archive_path)
        else:
            print("Не удалось найти ссылку на архив pdf-a4.zip")

    except requests.RequestException as e:
        print("Ошибка при загрузке или сохранении архива:", e)

    finally:
        session.close()

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    results = [('Статус', 'Количество')]
    sum_status = {}
    soup = get_soup(session, PEP_URL)
    if soup is None:
        return results
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    pep_row = tbody_tag.find_all('tr')
    for check_row in tqdm(pep_row):
        status_pep = find_tag(check_row, 'td')
        preview_status = status_pep.text[1:]
        one_pep_link = extract_pep_link(check_row)
        new_pep_soup = get_soup(session, one_pep_link)
        if new_pep_soup is None:
            continue
        full_status_pep = extract_pep_status(new_pep_soup)
        sum_status[full_status_pep] = sum_status.get(full_status_pep, 0) + 1
        try:
            if full_status_pep not in EXPECTED_STATUS[preview_status]:
                message_of_error = (
                    f'Несовпадающие статусы:\n{one_pep_link}\n'
                    f'Статус в карточке {full_status_pep}\n'
                    f'Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}'
                )
                logging.warning(message_of_error)
        except KeyError as error:
            raise error
    results.extend(sum_status.items())
    results.append(('Total', sum(sum_status.values())))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    if parser_mode in MODE_TO_FUNCTION:
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)

            if args.output == 'file':
                file_output(results, args)
    else:
        logging.error(f'Недопустимый режим работы парсера: {parser_mode}')

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
