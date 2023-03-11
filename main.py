import requests
import pathlib
from pathlib import Path


def check_for_redirect(response):
    response_url = response.url
    response_history = response.history
    if response_history == 301:
        print('ошибка')
        
    print(response_url)
    print(response_history)


def download_books():
    script_path = pathlib.Path.cwd()
    file_path = script_path.joinpath('books')
    file_path.mkdir(exist_ok=True)
    url_template = 'https://tululu.org/txt.php?id={}'
    for book_id in range(1, 11):
        url = url_template.format(book_id)
        response = requests.get(
            url,
            verify=False
            )
        response.raise_for_status()
        check_for_redirect(response)
        file_name = f'book_{book_id}'
        with open(Path(file_path).joinpath(file_name), 'wb') as book:
            book.write(response.content)


if __name__ == '__main__':
    download_books()