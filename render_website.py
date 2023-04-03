import json
import pathlib
from pathlib import Path
from pprint import pprint

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from livereload import Server
from pathvalidate import sanitize_filename


def render_html():
    script_path = pathlib.Path.cwd()
    books_path = script_path.joinpath('books')
    book_descriptions_json_path = Path(books_path).joinpath(
        'book_descriptions.json'
        )
    html_templates_path = script_path.joinpath('pages')
    html_templates_path.mkdir(exist_ok=True)
    with open(book_descriptions_json_path,
            "r", encoding='utf8') as json_file:
        books_descriptions = json_file.read()
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    books = json.loads(books_descriptions)
    divided_books_per_page = list(chunked(books, 10, strict=False))
    for page_id, books_per_page in enumerate(divided_books_per_page):
        books_iterable = list(chunked(books_per_page, 2, strict=False))
        template_name = sanitize_filename(f'index{page_id+1}.html')
        page_numbers = range(1, len(divided_books_per_page)+1)
        rendered_page = template.render(
            books_descriptions=books_iterable,
            page_id=page_id+1,
            number_of_pages=page_numbers,
        )
        with open(Path(html_templates_path).joinpath(template_name),
                  'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    render_html()
    server = Server()
    server.watch('template.html', render_html)
    server.serve(root='.')


if __name__ == '__main__':
    main()

