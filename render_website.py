import json
import pathlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from livereload import Server
from pathvalidate import sanitize_filename

BOOK_DESCRIPTIONS_JSON_PATH = pathlib.Path.cwd().joinpath(
        'book_descriptions.json'
        )

def render_html():
    script_path = pathlib.Path.cwd()
    html_pages_path = script_path.joinpath('pages')
    html_pages_path.mkdir(exist_ok=True)
    with open(BOOK_DESCRIPTIONS_JSON_PATH,
            "r", encoding='utf8') as json_file:
        books_descriptions = json_file.read()
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    books_descriptions = json.loads(books_descriptions)
    splitted_books_descriptions = list(chunked(books_descriptions, 10, strict=False))
    page_numbers = range(1, len(splitted_books_descriptions)+1)
    for page_id, books_descriptions_per_page in enumerate(splitted_books_descriptions):
        books_descriptions_in_row = list(chunked(books_descriptions_per_page, 2, strict=False))
        template_name = sanitize_filename(f'index{page_id+1}.html')
        rendered_page = template.render(
            books_descriptions=books_descriptions_in_row,
            page_id=page_id+1,
            number_of_pages=page_numbers,
        )
        with open(Path(html_pages_path).joinpath(template_name),
                  'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    render_html()
    server = Server()
    server.watch('template.html', render_html)
    server.serve(root='.')


if __name__ == '__main__':
    main()

