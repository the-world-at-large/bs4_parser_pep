import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (DATETIME_FORMAT, FILE_OUTPUT,
                       BASE_DIR, PRETTY_OUTPUT)


def default_output(results, cli_args=None):
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name

    if results:
        with open(file_path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, dialect='unix')
            writer.writerows(results)
        logging.info(f'Файл с результатами был сохранён: {file_path}')
    else:
        logging.warning('Нет результатов для сохранения в файл.')


OUTPUT_FUNCTIONS = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
}


def control_output(results, cli_args):
    output = cli_args.output
    output_function = OUTPUT_FUNCTIONS.get(output, default_output)
    output_function(results, cli_args)
