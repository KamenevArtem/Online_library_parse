import argparse
import json
import logging
import os
import sys
import time
import urllib
from urllib.parse import urljoin
from urllib.parse import urlparse


import requests
import pathlib
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from requests import HTTPError
from retry import retry


def parse_arg_main():
    parser = argparse.ArgumentParser(
        description='Download books from tululu.org'
        )
    parser.add_argument(
        '-stp', '--start_page', nargs='?',
        help='First page to download',
        default=1,
        type=int
        )
    parser.add_argument(
        '-enp', '--end_page', nargs='?',
        help='Last page to download',
        type=int
        )
    parser.add_argument(
        '-df', '--dest_folder',
        help='Путь к каталогу с результатами парсинга',
        action='store_true',
        )
    parser.add_argument(
        '-si', '--skip_imgs',
        help='Не скачивать обложки книг',
        action='store_true',
        )
    parser.add_argument(
        '-st', '--skip_txts',
        help='Не скачивать тексты книг',
        action='store_true',
        )
    parser.add_argument(
        '-jp', '--json_path',
        help='Полный путь к json файлу,'
        'содержащему данные по всем скачанным книгам',
        action='store_true',
        )
    arg = parser.parse_args()
    return arg


def check_for_redirect(response):
    if response.is_redirect:
        raise HTTPError(response.status_code, 'Переадресация')


def parse_book_ids(page_html):
    url = 'https://tululu.org/'
    books = page_html.select('table.d_book')
    book_urls = [urljoin(url, book.select_one('td a')['href'])
                 for book in books]
    book_ids = [book_url.split('b')[1] for book_url in book_urls]
    return book_ids


def checking_parameters(start_page, end_page):
    if end_page and end_page > start_page:
        return end_page
    else:
        end_page = start_page + 1
        return end_page


def parse_pages(start_page, end_page):
    page_url_template = 'https://tululu.org/l55/{}'
    book_ids = []
    for page_number in range(start_page, end_page):
        page_url = page_url_template.format(page_number)
        try:
            parsing_response = requests.get(page_url, verify=False)
            check_for_redirect(parsing_response)
            parsing_response.raise_for_status()
            page_html = BeautifulSoup(parsing_response.text, 'lxml')
            book_ids.extend(parse_book_ids(page_html))
        except HTTPError as error:
            sys.stderr.write(f'{error}')
            continue
        except ConnectionError as error:
            time.sleep(2)
            sys.stderr.write(f'{error}')
    return book_ids


def define_extension(file_url):
    parsed_url = urlparse(file_url)
    parsed_path = parsed_url.path
    parsed_path = urllib.parse.unquote(parsed_path)
    file_path, file_extension = os.path.splitext(parsed_path)
    file_name = file_path.split('/')[2]
    return file_extension, file_name


@retry(TimeoutError, ConnectionError,
       delay=1, backoff=4, max_delay=4)
def download_txt(book_text, books_path, book_name):
    file_path = books_path.joinpath('books_txts')
    file_path.mkdir(exist_ok=True)
    file_name = sanitize_filename(f'{book_name}.txt')
    with open(Path(file_path).joinpath(file_name),
              'wb') as book:
        book.write(book_text)


@retry(TimeoutError, ConnectionError,
       delay=1, backoff=4, max_delay=4)
def download_image(url, books_path):
    image_response = requests.get(
        url,
        verify=False
    )
    image_response.raise_for_status()
    file_path = books_path.joinpath('images')
    file_path.mkdir(exist_ok=True)
    file_extension, image_name = define_extension(url)
    image_name = (f'{image_name}{file_extension}')
    with open(Path(file_path).joinpath(image_name),
              'wb') as image:
        image.write(image_response.content)


def parse_book_page(page_html, book_url):
    book_description = page_html.select_one('table h1')
    book_description = book_description.text.split(' \xa0 :: \xa0 ')
    book_title, book_author = book_description
    book_image = page_html.select_one('div.bookimage img')['src']
    image_name = book_image.split('/')[2]
    book_image_url = urljoin(book_url, book_image)
    parsed_comments = page_html.select('div.texts')
    comments = [comment.select_one('span').text
                for comment in parsed_comments]
    book_genres = page_html.select('span.d_book a')
    genres = []
    for book_genre in book_genres:
        genres.append(book_genre.text)
    parsed_book_description = {
        'title': book_title,
        'author': book_author,
        'image_url': book_image_url,
        'genre': genres,
        'comments': comments,
        'image_name': image_name,
    }
    return parsed_book_description


@retry(TimeoutError, ConnectionError,
       delay=1, backoff=4, max_delay=4)
def download_book_descriptions(url_template, book_id,
                               script_path, skip_txts, skip_imgs):
    book_url = url_template.format('txt.php')
    param = {
        'id': book_id,
    }
    downloading_book_response = requests.get(
        book_url,
        verify=False,
        params=param,
        allow_redirects=False
    )
    check_for_redirect(downloading_book_response)
    downloading_book_response.raise_for_status()
    book_text = downloading_book_response.content
    parsing_url = url_template.format(f'b{book_id}/')
    parsing_response = requests.get(parsing_url, verify=False)
    check_for_redirect(parsing_response)
    parsing_response.raise_for_status()
    page_html = BeautifulSoup(parsing_response.text, 'lxml')
    parsed_book_description = parse_book_page(
        page_html,
        parsing_url
        )
    if not skip_txts:
        download_txt(book_text, script_path,
                     parsed_book_description['title'])
    if not skip_imgs:
        download_image(parsed_book_description['image_url'],
                       script_path)
    return parsed_book_description


def main():
    script_path = pathlib.Path.cwd()
    books_path = script_path.joinpath('media')
    books_path.mkdir(exist_ok=True)
    book_descriptions_json_path = Path(books_path).joinpath(
        'book_descriptions.json'
        )
    url_template = 'https://tululu.org/{}'
    args = parse_arg_main()
    start_page = args.start_page
    end_page = args.end_page
    end_page = checking_parameters(start_page, end_page)
    skip_txts = args.skip_txts
    skip_imgs = args.skip_imgs
    end_page = checking_parameters(start_page, end_page)
    logging.getLogger().setLevel(logging.INFO)
    if args.json_path:
        logging.info(f'Путь к json файлу:'
                     f'{book_descriptions_json_path}')
    if args.dest_folder:
        logging.info(f'Путь к скаченным книгам {books_path}')
    book_ids = parse_pages(start_page, end_page)
    book_descriptions = []
    for book_id in book_ids:
        try:
            parsed_book_description = download_book_descriptions(
                url_template,
                book_id,
                books_path,
                skip_txts,
                skip_imgs
                )
            book_descriptions.append(parsed_book_description)
        except HTTPError as error:
            logging.error(msg=f'Была обнаружена ошибка {error}')
    with open(book_descriptions_json_path,
              'w', encoding='utf8') as json_file:
        json.dump(book_descriptions, json_file,
                  ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
