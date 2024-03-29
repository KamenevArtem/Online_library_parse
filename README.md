# Online_library_parse

Программа предназначена для сохранения книг и соответствующих им обложек с сайта [tululu.org](https://tululu.org/) с последующей генерацией html шаблонов для сборки сайта. 

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

1. `-stp "Целое число"` - первая страница, с которой необходимо скачать книги. По умолчанию, первая страница равна 1;
2. `-enp "Целое число"` - последняя страница с которой необходимо скачать книги. Это значение должно быть больше `stp`. В случае когда переменная `enp` не указана, просиходит скачивание одной страницы, начиная с `stp`;
3. `-df` - сообщает программе, что пользователю нужен путь к директории, где хранятся скачанные данное по книгам;
4. `si` - сообщает программе, что скачивание картинок к книгам не необходимо;
5. `st` - сообщает программе, что скачивание текста книг не необходимо;
6. `jp` - сообщает программе, что пользователю нужен полный путь к файлу парсинга книг;
7. `-h` - выводит описание прогрммы и всех переменных

Вызываются переменные следующим образом:

```
python download_books_from_tululu.py -stp [Значение] -enp [Значение]
```

Все загруженные файлы сохраняются в папку `/media`

Для формирования html-шаблонов необходимо запустить команду:

```
python render_website.py
```

Далее в папке `/pages` будут сформированы шаблоны страниц сайта. Каждая страница содержит максимум 10 книг.

Чтобы ознакомиться с работой сайта, необходимо пройти по [ссылке](https://kamenevartem.github.io/Online_library_parse/pages/index1.html)

Сайт имеет следующий вид:

![image](https://i.ibb.co/ftztkQP/image.png)

### Локальный запуск

После ввода команды для запуска скрипта `python render_website.py` будет создан локальный сервер, отвечающий на запросы браузера. Для того, чтобы перейти на страничку сайта, необходимо перейти по адресу http://127.0.0.1:5500/pages/index1.html

### Запуск офлайн:

Для запуска страниц сайта, необходимо открыть любой из html шаблонов, хранящихся в папке `/pages` через браузер. 



## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [devman](https://devman.org/)