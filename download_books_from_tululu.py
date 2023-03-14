import argparse
import requests
import pathlib
import urllib
import os
import logging
from pathlib import Path
from requests import HTTPError
from bs4 import BeautifulSoup
from retry import retry
from urllib.parse import urljoin
from urllib.parse import urlparse
from pathvalidate import sanitize_filename


def parse_arg_main():
    parser = argparse.ArgumentParser(
        description='Download books from tululu.org'
        )
    parser.add_argument('-fst', '--first', nargs='?',
                        help='Whitch book is the first',
                        default=1,
                        type=int
                        )
    parser.add_argument('-lst', '--last', nargs='?',
                        help='Whitch book is the last',
                        default=10,
                        type=int
                        )
    arg = parser.parse_args()
    return arg


def define_extension(file_url):
    parsed_url = urlparse(file_url)
    parsed_path = parsed_url.path
    parsed_path = urllib.parse.unquote(parsed_path)
    file_path, file_extension = os.path.splitext(parsed_path)
    file_name = file_path.split('/')[2]
    return file_extension, file_name


def check_for_redirect(response):
    if response.is_redirect:
        raise HTTPError(response.status_code, 'Переадресация')


@retry(ConnectionError,
       delay=1, backoff=4, max_delay=4)
def download_txt(book_text, script_path, book_name):
    file_path = script_path.joinpath('books')
    file_path.mkdir(exist_ok=True)
    file_name = sanitize_filename(f'{book_name}.txt')
    with open(Path(file_path).joinpath(file_name),
              'wb') as book:
        book.write(book_text)


@retry(ConnectionError,
       delay=1, backoff=4, max_delay=4)
def download_image(url, script_path):
    image_response = requests.get(
        url,
        verify=False
    )
    image_response.raise_for_status()
    file_path = script_path.joinpath('images')
    file_path.mkdir(exist_ok=True)
    file_extension, image_name = define_extension(url)
    image_name = (f'{image_name}.{file_extension}')
    with open(Path(file_path).joinpath(image_name),
              'wb') as image:
        image.write(image_response.content)


@retry(ConnectionError,
       delay=1, backoff=4, max_delay=4)
def parse_book_page(page_html, book_url):
    book_description = page_html.find('table').find('h1')
    book_description = book_description.text.split(' \xa0 :: \xa0 ')
    book_title, book_author = book_description
    book_image = page_html.find(
        'div', class_='bookimage').find('img')['src']
    book_image_url = urljoin(book_url, book_image)
    parsed_comments = page_html.find_all('div', class_='texts')
    comments = [comment.find('span').text
                for comment in parsed_comments]
    book_genres = page_html.find('span', class_='d_book').find('a')
    parsed_book_description = {
        'title': book_title,
        'author': book_author,
        'image_url': book_image_url,
        'genre': book_genres.text,
        'comments': comments,
    }
    return parsed_book_description


def download_book(url_template, book_id, script_path):
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
    parsing_response.raise_for_status()
    page_html = BeautifulSoup(parsing_response.text, 'lxml')
    parsed_book_description = parse_book_page(page_html,
                                              parsing_url)
    download_txt(book_text, script_path,
                 parsed_book_description['title'])
    download_image(parsed_book_description['image_url'],
                   script_path)


def main():
    script_path = pathlib.Path.cwd()
    books_path = script_path.joinpath('books')
    books_path.mkdir(exist_ok=True)
    images_path = script_path.joinpath('images')
    images_path.mkdir(exist_ok=True)
    url_template = 'https://tululu.org/{}'
    args = parse_arg_main()
    first_book = args.first
    last_book = args.last
    for book_id in range(first_book, last_book+1):
        try:
            download_book(url_template, book_id, script_path)
        except HTTPError as error:
            logging.error(msg=f'Была обнаружена ошибка {error}')


if __name__ == '__main__':
    main()
