import requests
import pathlib
import urllib
import os
import logging
import json
from pprint import pprint
from pathlib import Path
from requests import HTTPError
from bs4 import BeautifulSoup
from retry import retry
from urllib.parse import urljoin
from urllib.parse import urlparse
from pathvalidate import sanitize_filename


def parse_book_ids(page_html):
    url = 'https://tululu.org/'
    books = page_html.select('table.d_book')
    book_urls = [urljoin(url, book.select_one('td a')['href'])
                for book in books
                ]
    book_ids = [book_url.split('b')[1] for book_url in book_urls]
    return book_ids


def parse_pages(pages_quantity):
    page_url_template = 'https://tululu.org/l55/{}'

    book_ids = []
    for page_number in range(1, pages_quantity+1):
        page_url = page_url_template.format(page_number)
        parsing_response = requests.get(page_url, verify=False)
        parsing_response.raise_for_status()
        page_html = BeautifulSoup(parsing_response.text, 'lxml')
        book_ids.append(parse_book_ids(page_html))
    flat_list_of_ids = [book_id for page_ids in book_ids for book_id in page_ids]
    return flat_list_of_ids


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


@retry(TimeoutError, ConnectionError,
       delay=1, backoff=4, max_delay=4)
def download_txt(book_text, script_path, book_name):
    file_path = script_path.joinpath('books')
    file_path.mkdir(exist_ok=True)
    file_name = sanitize_filename(f'{book_name}.txt')
    with open(Path(file_path).joinpath(file_name),
              'wb') as book:
        book.write(book_text)


@retry(TimeoutError, ConnectionError,
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


def parse_book_page(page_html, book_url, book_descriptions):
    book_description = page_html.select_one('table h1')
    book_description = book_description.text.split(' \xa0 :: \xa0 ')
    book_title, book_author = book_description
    book_image = page_html.select_one('div.bookimage img')['src']
    book_image_url = urljoin(book_url, book_image)
    parsed_comments = page_html.select('div.texts')
    comments = [comment.select_one('span').text
                for comment in parsed_comments]
    book_genres = page_html.select_one('span.d_book a')
    parsed_book_description = {
        'title': book_title,
        'author': book_author,
        'image_url': book_image_url,
        'genre': book_genres.text,
        'comments': comments,
    }    
    book_descriptions.append(parsed_book_description)
    return parsed_book_description, book_descriptions


@retry(TimeoutError, ConnectionError,
       delay=1, backoff=4, max_delay=4)
def download_book_descriptions(url_template, book_id, script_path, book_descriptions):
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
    parsed_book_description, book_descriptions = parse_book_page(
        page_html,
        parsing_url,
        book_descriptions
        )
    download_txt(book_text, script_path,
                parsed_book_description['title'])
    download_image(parsed_book_description['image_url'],
                script_path)
    return(book_descriptions)


def main():
    script_path = pathlib.Path.cwd()
    books_path = script_path.joinpath('books')
    books_path.mkdir(exist_ok=True)
    images_path = script_path.joinpath('images')
    images_path.mkdir(exist_ok=True)
    url_template = 'https://tululu.org/{}'
    pages_quantity = 1
    book_ids = parse_pages(pages_quantity)
    book_descriptions = []
    for book_id in book_ids:
        try:
            book_descriptions = download_book_descriptions(
                url_template,
                book_id,
                script_path,
                book_descriptions
                )
            if book_id == book_ids[-1]:
                book_descriptions_json = json.dumps(
                    book_descriptions,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                    )
                with open('book_descriptions.json', 'w', encoding='utf8') as json_file:
                    json_file.write(book_descriptions_json)
        except HTTPError as error:
            logging.error(msg=f'Была обнаружена ошибка {error}')


if __name__ == '__main__':
    main()