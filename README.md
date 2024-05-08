## Для запуска необходимо:
Установить python-библиотеки: fastapi, plotly, pandas.

Запуск сервера производится командой (находясь в основной папке проекта) '''uvicorn server:app --reload'''

Для веб-части необходимо открыть файл "home.html"

## Краткое описание функционала файлов
server.py - API-сервер и весь его функционал, включающий в себя endpoint-ы:
    -'/upload' -  POST запрос, отправляющий на сервер файлы, которые сохраняются в папке "uploads"
    -'/files' - GET запрос, возвращаюший список всех загруженных на сервер файлов
    -'/files/{file_name}' - GET запрос, возвращаюший пример данных загруженного файла {file_name} (поддерживает форматы .txt, .xlsx) 
    -'/graph' - GET запрос, возвращаюший сгенерированный график в json-формате
    -'/files/all' - DELETE запрос, удаляющий все файлы

home.html - Стартовая веб-старница с выбором дальнейших действий;
upload.html, upload.js - загрузка файлов на сервер;
graph.html - отображение графика по данным от сервера (с помощью библиотеки plotly);
fileList.html - список загруженых файлов с возможностью очистить папку.
