from flask import Flask, render_template, request
import hh_parser as hh

app = Flask(__name__)
STAT_COUNT = 35 #Количество вакансий, которые будем просматривать для сбора статистики
TOP_COUNT = 7 #Количество записей для вывода TOPа

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
        'title': 'Страница запроса информации по вакансиям',
        'stat_count': STAT_COUNT,
        'top_count': TOP_COUNT
    }
    return render_template('form.html', **context)

@app.route('/results/', methods=['POST'])
def results():
    query_string = request.form['query_string']
    try:
        stat_count = int( request.form['stat_count'])
    except:
        stat_count = STAT_COUNT
    try:
        top_count = int(request.form['top_count'])
    except:
        top_count = TOP_COUNT
    context=hh.find_vacancies_data(query_string=query_string, stat_count=stat_count, top_count=top_count)
    context['title']='Страница аналитики по запрошенным вакансиям'
    context['stat_count']= stat_count
    context['top_count']= top_count
    return render_template('results.html', **context)

if __name__ == '__main__':
    app.run(debug=True)