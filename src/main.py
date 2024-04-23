from collections import defaultdict
import logging
import re
from urllib.parse import urljoin

import requests
import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import (extract_pep_link, extract_pep_status,
                   find_tag, get_soup)


def whats_new(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    try:
        soup = get_soup(session, MAIN_DOC_URL)
        main_div = find_tag(soup, 'section',
                            attrs={'id': 'what-s-new-in-python'})

        div_with_ul = find_tag(main_div, 'div',
                               attrs={'class': 'toctree-wrapper'})

        sections_by_python = div_with_ul.find_all(
            'li', attrs={'class': 'toctree-l1'})

        for section in tqdm(sections_by_python):
            version_a_tag = section.find('a')
            version_link = urljoin(MAIN_DOC_URL, version_a_tag['href'])
            soup = get_soup(session, version_link)
            if soup is None:
                continue
            h1 = find_tag(soup, 'h1')
            dl = find_tag(soup, 'dl')
            dl_text = dl.text.replace('\n', ' ')
            results.append(
                (version_link, h1.text, dl_text)
            )
    except Exception as e:
        logging.exception(f'Ошибка при получении информации о новых версиях: '
                          f'{e}')
    return results


def latest_versions(session):
    try:
        soup = get_soup(session, MAIN_DOC_URL)
        if soup is None:
            return None

        sidebar = find_tag(soup, 'div',
                           attrs={'class': 'sphinxsidebarwrapper'})
        ul_tags = sidebar.find_all('ul')
        for ul in ul_tags:
            if 'All versions' in ul.text:
                a_tags = ul.find_all('a')
                break
        else:
            raise ValueError('Ничего не нашлось.')

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
    except Exception as e:
        logging.exception(f'Ошибка при получении последних версий: {e}')
        return None


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    try:
        soup = get_soup(session, downloads_url)
        if soup is None:
            return

        pdf_a4_tag = find_tag(soup, 'a', attrs={
                                    'href': re.compile(r'.+pdf-a4\.zip$')})

        if not pdf_a4_tag:
            raise ValueError("Не удалось найти ссылку на архив pdf-a4.zip")

        pdf_a4_link = urljoin(downloads_url, pdf_a4_tag['href'])

        downloads_dir = BASE_DIR / 'downloads'
        downloads_dir.mkdir(exist_ok=True)

        filename = pdf_a4_link.split('/')[-1]
        archive_path = downloads_dir / filename

        response = session.get(pdf_a4_link)

        with open(archive_path, 'wb') as file:
            file.write(response.content)

        logging.info(f'Архив успешно загружен и сохранен по пути: '
                     f'{archive_path}')

    except requests.RequestException as e:
        logging.error(f'Ошибка при загрузке или сохранении архива: {e}')

    finally:
        session.close()


def pep(session):
    results = [('Статус', 'Количество')]
    sum_status = defaultdict(int)

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
        sum_status[full_status_pep] += 1

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
        try:
            results = MODE_TO_FUNCTION[parser_mode](session)
            if results is not None:
                control_output(results, args)
        except Exception as e:
            logging.error(f'Ошибка при выполнении режима {parser_mode}: {e}')
    else:
        logging.error(f'Недопустимый режим работы парсера: {parser_mode}')

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
