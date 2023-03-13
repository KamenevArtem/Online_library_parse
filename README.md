# Online_library_parse

Программа предназначена для сохранения книг и соответствующих им обложек с сайта [tululu.org](https://tululu.org/). 

## Как установить:

 Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:

```
pip install -r requirements.txt
```

## Как запустить

Скрипт, обеспечивающий скачивание изображений, запускается через командную строку командой:
```
python download_books_from_tululu.py
```

Данный скрип имеет два аргумента, которые позволяют задавать диапазон скачивания книг. По умолчанию, программа скачивает первые 10 книг с сайта. Для того, чтобы задать диапазон, необходимо ввести следующую команду:

```
python download_books_from_tululu.py -fst [Значение] -lst [Значение]
```

Аргумент `fst` определяет первую книгу, которую пользователь хочет скачать, `lst` - последнюю

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [devman](https://devman.org/)