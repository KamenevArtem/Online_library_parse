import json
import pathlib
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape


script_path = pathlib.Path.cwd()
books_path = script_path.joinpath('books')
books_path.mkdir(exist_ok=True)
book_descriptions_json_path = Path(books_path).joinpath(
    'book_descriptions.json'
    )


with open(book_descriptions_json_path,
          "r", encoding='utf8') as json_file:
    books_descriptions = json_file.read()

books = json.loads(books_descriptions)

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

rendered_page = template.render(
    books_descriptions=books,
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()

