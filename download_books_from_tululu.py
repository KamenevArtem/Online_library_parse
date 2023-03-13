import argparse
import requests
import pathlib
import urllib
import os
from pathlib import Path
from requests import HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from pathvalidate import sanitize_filename


def parse_arg_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fst', '--first', nargs='?',
                        help='Whitch book is the first',
                        default="1")
    parser.add_argument('-lst', '--last', nargs='?',
                        help='Whitch book is the last',
                        default='10')
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
    response_url = response.url
    response_history = response.history
    if response_history and response_url == 'https://tululu.org/':
        raise HTTPError(response_history)


def download_txt(book_text, script_path, book_name):
    file_path = script_path.joinpath('books')
    file_path.mkdir(exist_ok=True)
    file_name = sanitize_filename(f'{book_name}.txt')
    with open(Path(file_path).joinpath(file_name),
              'wb') as book:
            book.write(book_text)


def download_images(url, script_path):
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


def parse_book_page(page_html, url_template):
    book_description = page_html.find('table').find('h1')
    book_description = book_description.text.split(' \xa0 :: \xa0 ')
    book_title = book_description[0]
    book_author = book_description[1]
    book_image = page_html.find('div',
                                class_='bookimage').find('img')['src']
    book_image_url = urljoin(url_template, book_image)
    parsed_comments = page_html.find_all('div', class_='texts')
    comments = []
    for comment in parsed_comments:
        if parsed_comments:
            comment = comment.find('span').text
            comments.append(comment)
    book_genre = page_html.find('span', class_='d_book').find('a')
    parsed_book_description = {
        'title': book_title,
        'author': book_author,
        'image_url': book_image_url,
        'genre': book_genre.text,
        'comments': comments        
    }
    return parsed_book_description


def download_books(url_template, book_id, script_path):
    book_url = url_template.format(f'txt.php?id={book_id}')
    downloading_book_response = requests.get(
        book_url,
        verify=False
    )
    downloading_book_response.raise_for_status()
    check_for_redirect(downloading_book_response)
    book_text = downloading_book_response.content
    parse_url = url_template.format(f'b{book_id}/')
    parse_response = requests.get(parse_url, verify=False)
    parse_response.raise_for_status()
    page_html = BeautifulSoup(parse_response.text, 'lxml')
    parsed_book_description = parse_book_page(page_html,
                                              url_template)
    download_txt(book_text, script_path,
                 parsed_book_description['title'])
    download_images(parsed_book_description['image_url'],
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
    for book_id in range(int(first_book), int(last_book)+1):
        try:
            download_books(url_template, book_id, script_path)
        except HTTPError:
            pass


if __name__ == '__main__':
    main()