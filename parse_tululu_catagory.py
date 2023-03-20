import requests
import bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse


def create_book_links(page_html, url_template):
    books = page_html.find_all('table', class_='d_book')
    book_url = [urljoin(url_template, book.find('td').find('a')['href'])
                for book in books
                ]
    print(book_url)


def parse_pages(pages_quantity, url_template):
    page_url_template = 'https://tululu.org/l55/{}'
    for page_number in range(1, pages_quantity+1):
        page_url = page_url_template.format(page_number)
        parsing_response = requests.get(page_url, verify=False)
        parsing_response.raise_for_status()
        page_html = BeautifulSoup(parsing_response.text, 'lxml')
        create_book_links(page_html, url_template)


def main():
    url_template = 'https://tululu.org/'
    pages_quantity = 10
    parse_pages(pages_quantity, url_template)


if __name__ == '__main__':
    main()