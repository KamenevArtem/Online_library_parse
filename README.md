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

Данный скрип имеет набор аргументов, позволяющий пользователю настроить под себя сценарий выполнения программы:

1. `-stp "Целое число"` - первая страница, с которой необходимо скачать книги. По умолчанию, первая страница равно 1;
2. `-enp "Целое число"` - последняя страница с которой необходимо скачать книги. Это значение должно быть больше `stp`. В случае когда переменная `enp` не указана, просиходит скачивание десяти страниц, начиная с `stp`;
3. `-df` - сообщает программе, что пользователю нужен путь к директории, где хранятся скачанные данное по книгам;
4. `si` - сообщает программе, что скачивание картинок к книгам не необходимо;
5. `st` - сообщает программе, что скачивание текста книг не необходимо;
6. `jp` - сообщает программе, что пользователю нужен полный путь к файлу парсинга книг;
7. `-h` - выводит описание прогрммы и всех переменных

Вызываются переменные следующим образом:

```
python download_books_from_tululu.py -stp [Значение] -enp [Значение]
```

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [devman](https://devman.org/)