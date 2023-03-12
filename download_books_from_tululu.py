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


def download_txt(book_name, url, script_path):
    downloading_book_response = requests.get(
        url,
        verify=False
    )
    downloading_book_response.raise_for_status()
    check_for_redirect(downloading_book_response)
    file_path = script_path.joinpath('books')
    file_path.mkdir(exist_ok=True)
    file_name = sanitize_filename(f'{book_name}.txt')
    with open(Path(file_path).joinpath(file_name), 'wb') as book:
            book.write(downloading_book_response.content)


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
    with open(Path(file_path).joinpath(image_name), 'wb') as image:
        image.write(image_response.content)


def download_books(url_template, book_id):
    script_path = pathlib.Path.cwd()
    url_options=f'txt.php?id={book_id}'
    book_url = url_template.format(url_options)
    url_soup_options = f'b{book_id}/'
    url_for_soup = url_template.format(url_soup_options)
    soup_response = requests.get(url_for_soup, verify=False)
    soup_response.raise_for_status()
    soup = BeautifulSoup(soup_response.text, 'lxml')
    book_description = soup.find('table').find('h1')
    print(book_description)
    book_description = book_description.text.split(' \xa0 :: \xa0 ')
    book_title = book_description[0]
    download_txt(book_title, book_url, script_path)
    book_image = soup.find('div', class_='bookimage').find('img')['src']
    book_image_url = urljoin(url_template, book_image)
    download_images(book_image_url, script_path)
    comments = soup.find_all('div', class_='texts')
    for comment in comments:
        if comments:
            comment = comment.find('span')
            # print(comment.text)
    book_genre = soup.find('span', class_='d_book').find('a')
    print(book_genre.text)

def main():
    script_path = pathlib.Path.cwd()
    books_path = script_path.joinpath('books')
    books_path.mkdir(exist_ok=True)
    images_path = script_path.joinpath('images')
    images_path.mkdir(exist_ok=True)
    url_template = 'https://tululu.org/{}'
    book_quantity = 10
    for book_id in range(1, book_quantity+1):
        try:
            download_books(url_template, book_id)
        except HTTPError:
            pass


if __name__ == '__main__':
    main()