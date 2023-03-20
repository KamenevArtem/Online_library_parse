import requests
import bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse


def create_book_link(url_template):
    books_url = 'https://tululu.org/l55/'
    parsing_response = requests.get(books_url, verify=False)
    parsing_response.raise_for_status()
    page_html = BeautifulSoup(parsing_response.text, 'lxml')
    books = page_html.find_all('table', class_='d_book')
    for book in books:
        book = book.find('td').find('a')['href']
        book_url = urljoin(url_template, book)
        print(book_url)


def main():
    url_template = 'https://tululu.org/'
    create_book_link(url_template)


if __name__ == '__main__':
    main()