from flask import Flask, request, render_template, send_file
import requests
import csv
# import os
import logging
import json
# import pandas as pd
# from io import BytesIO
# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


# Функция для поиска вакансий
def search_vacancies(keyword):
    BASE_URL = "https://api.hh.ru/vacancies"
    vacancies_found = []  # Список для хранения найденных вакансий
    per_page = 100
    page = 0

    while True:
        params = {
            'text': keyword,
            'page': page,
            'per_page': per_page,
            'only_with_salary': True  # Только вакансии с зарплатой
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            print("Ошибка при обращении к API")
            break

        lan = response.json()

        if not lan['items']:
            break

        for item in lan['items']:
            # vacancy_name = item['name']
            vacancy_name = item['name'].lower()  # Приводим название вакансии к нижнему регистру для сравнения
            # Проверяем, содержит ли название вакансии ключевое слово
            if keyword in vacancy_name:
                salary_from = item['salary']['from'] if item['salary'] else None
                salary_to = item['salary']['to'] if item['salary'] else None
                currency = item['salary']['currency'] if item['salary'] else None
                city = item['area']['name'] if 'area' in item else None
                link = item['alternate_url'] if 'alternate_url' in item else None
                discription = item['snippet']['responsibility'] if 'snippet' in item else None

                vacancies_found.append({
                    'name': vacancy_name,
                    'salary_from': salary_from,
                    'salary_to': salary_to,
                    'currency': currency,
                    'city': city,
                    'link': link,
                    'discription': discription
                })

        page += 1

    return vacancies_found


# # Функция для сохранения вакансий в CSV
# def save_to_csv(vacancies, filename='vacancies.csv'):
#     # Если имя файла не передано, создаем его на основе ключевого слова
#     keys = vacancies[0].keys()
#     with open(filename, 'w', newline='', encoding='utf-16') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=keys)
#         writer.writeheader()
#         writer.writerows(vacancies)
#     return filename  # Возвращаем имя файла


def save_to_json(vacancies):
    # Если имя файла не передано, создаем его на основе ключевого слова
    with open('vacancies.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(vacancies, jsonfile, ensure_ascii=False, indent=2)
    return 'vacancies.json' # Возвращаем имя файла


# @app.route('/download')
# def download_file():
#     return send_file('vacancies.csv', as_attachment=True)

@app.route('/download')
def download_file():
    return send_file('vacancies.json', as_attachment=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        vacancies = search_vacancies(keyword)
        print(len(vacancies))
        all_vacancies = (len(vacancies))
        if vacancies:
            filename = save_to_json(vacancies)
            return render_template('index.html', vacancies=vacancies, filename=filename, download=True, all_vacancies=all_vacancies)
        else:
            return render_template('index.html', all_vacancies=0)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5555)
