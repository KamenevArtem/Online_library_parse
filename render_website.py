import json
import pathlib
from pathlib import Path
from pprint import pprint

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from livereload import Server


def render_html():
    script_path = pathlib.Path.cwd()
    books_path = script_path.joinpath('books')
    book_descriptions_json_path = Path(books_path).joinpath(
        'book_descriptions.json'
        )
    with open(book_descriptions_json_path,
            "r", encoding='utf8') as json_file:
        books_descriptions = json_file.read()
    books = json.loads(books_descriptions)
    books_iterable = list(chunked(books, 2, strict=False))
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    rendered_page = template.render(
        books_descriptions=books_iterable,
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    render_html()
    server = Server()
    server.watch('template.html', render_html)
    server.serve(root='.')


if __name__ == '__main__':
    main()

