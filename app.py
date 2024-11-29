from flask import Flask, request, render_template, send_file, redirect, url_for
import requests
# import csv
import pandas as pd
from io import BytesIO
import logging
import json
# import pandas as pd
# from io import BytesIO
from functools import lru_cache
import sys

sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


@lru_cache(maxsize=1)     # хранить в кеше только результат крайнего запроса
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


@app.route('/download', methods=['POST'])
def download():
    keyword = request.form.get('work_name', '').strip()
    if keyword == '':
        return redirect('/')  # ничего не делать если keyword не задан
    vacancies = search_vacancies(keyword)

    df = pd.DataFrame(vacancies)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='vacancies.xlsx')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        if request.method == 'POST' and keyword:  # обновлять страницу только если задано ключевое слово
            vacancies = search_vacancies(keyword)
        print(len(vacancies))
        all_vacancies = (len(vacancies))
        if vacancies:
            return render_template('index.html',
                                   vacancies=vacancies,
                                   download=True,
                                   all_vacancies=all_vacancies,
                                   keyword=keyword)  # сохранить keyword на html-странице
        else:
            return render_template('index.html',
                                   all_vacancies=0,  # даже если по запросу ничего нет
                                   keyword=keyword)  # сохранить keyword на html-странице
    return render_template('index.html')  # пустой keyword приемлем для стартовой страницы без каких-либо данных


if __name__ == '__main__':
    app.run(debug=True)
