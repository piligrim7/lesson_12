from flask import Flask, render_template, request
import hh_parser as hh

app = Flask(__name__)

@app.route('/')
def index():
    context={
        'title': 'Главная страница'
    }
    return render_template('index.html', **context)

@app.route('/contacts/')
def contacts():
    context={
        'title': 'Контакты',
        'dev_name': 'Some name',
        'phone': '+70123456789',
        'email': 'some-address@some_domain.ru'
    }
    return render_template('contacts.html', **context)

@app.route('/form/')
def form():
    context={
        'title': 'Страница запроса информации по вакансиям'
    }
    return render_template('form.html', **context)

@app.route('/results/', methods=['POST'])
def results():
    context={
        'title': 'Страница аналитики по запрошенным вакансиям'
    }
    query_string = request.form['query_string']
    vacancies_data = hh.find_vacancies_data(query_string=query_string)
    #data = [query_string, 'python', 'js']

    return render_template('results.html', vacancies = vacancies_data['vacancies'].keys(), **context)

if __name__ == '__main__':
    app.run(debug=True)