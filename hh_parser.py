import re
import json
import requests
import statistics as stat
from collections import Counter, namedtuple

BASE_URL = 'http://api.hh.ru/' #Базовый url запроса

#Запрашиваем словарь валют с коэффициентами пересчета на рубли
currencies = requests.get(url=BASE_URL+'dictionaries/').json()['currency']

def append_boundary_salary_range(salary_range: list[float], boundary)-> list[float]:
    """Функция добавления границ диапазона зарплат по текущей вакансии

    Args:
        salary_range (list[float]): список границ диапазона зарплаты
        boundary (str): добавляемая граница диапазона

    Returns:
        list[float]: результат добавления
    """
    if boundary is not None:
        salary_range.append(float(boundary))
    return salary_range

def get_RUR_salary(currency: str, salary_value: float, currencies: dict = currencies)->float:
    """Функция пересчета значения зарплаты в рубли

    Args:
        currency (str): обозначение валюты
        salary_value (float): значение зарплаты
        currencies (dict, optional): Словарь валют. По умолчанию словарь валют hh.ru

    Returns:
        float: Пересчитанное в рубли значение зарплаты. None, если валюта не найдена.
    """
    for dict_currency in currencies:
        if dict_currency['code'] == currency:
            return salary_value/dict_currency['rate']
    return None

def find_vacancies_data(query_string: str, stat_count: int, top_count: int):
    text = query_string # 'python developer'# 'Программист Python' #запрос вакансии

    print(f'\nТекст запроса на hh.ru: "{text}"')

    params = {'text': text}

    salaries = list() #Список средних, приведенных к рублям зарплат по каждой вакансии (если не None)
    # skills: dict[str, int] = {} #Словарь скилов с количеством по наличию в просматриваемых вакансиях
    skills_ar = list() #Временный список всех скилов
    areas: dict[str, int] = {} #Словарь городов, где размещены просматриваемые вакансии
    areas_ar = list() #Временный список всех городов
    vacancies_count: int = 0 #Количество найденных вакансий

    count = 0 #счетчик просмотренных вакансий
    page_num = 0 #номер текущей страницы
    page_count = 1 #Количество страниц по запросу (перед первым запросом ставим 1, уточняем при первом запросе)

    while page_num < page_count: #Цикл по страницам
        page_num+=1
        params['page'] = page_num-1 #Задаем индекс страницы
        #Запрашиваем вакансии текущей страницы
        vacancies = requests.get(url=BASE_URL+'vacancies/', params=params).json()
        if page_num==1:
            page_count = vacancies['pages'] #Определяем количество страниц
            vacancies_count = vacancies["found"] 
            print((f'\nНайдено вакансий: {vacancies_count}') +
                (f', обрабатываем первые {stat_count}' if stat_count < vacancies_count else '')
                )

        for item in vacancies['items']: #Цикл по вакансиям на странице
            count+=1
            if count > stat_count:
                break #прерываем цикл по вакансиям, если достигнуто заданное количество просматриваемых вакансий

            #Определяем, пересчитываем в рубли и добавляем уровень зарплаты по текущей вакансии
            salary = item['salary']
            if salary is not None:
                s_ar = append_boundary_salary_range(salary_range=[], boundary=salary['from'])
                s_ar = append_boundary_salary_range(salary_range=s_ar, boundary=salary['to'])
                mean = get_RUR_salary(currency=salary['currency'], salary_value=stat.mean(s_ar))
                if mean is not None:
                    salaries.append(mean)

            #Запрашиваем требования по текущей вакансии
            vacancy = requests.get(item['url']).json()
            #В списке требований текущей вакансии удаляем русские слова и слово framework, собираем уникальные требования, из английских названий и аббревиатур
            vacancy_skills = set(
                # re.sub(r'[ЁёА-я]', '', key_skill['name'].lower().replace(' framework', '')).strip() for key_skill in vacancy['key_skills'] if re.search('[a-zA-Z]', key_skill['name'])
                key_skill['name'].lower().replace(' framework', '').strip() for key_skill in vacancy['key_skills']
                )
            # #Добавляем требования текущей вакансии в общий словарь требований с инкрементом количества уже существующего требования
            # for skill in vacancy_skills:
            #     skills[skill] = skills.setdefault(skill, 0) + 1
            
            #Пополняем списки скилов и городов
            skills_ar.extend(vacancy_skills)
            areas_ar.append(vacancy['area']['name'])
            
            # #Добавляем город в общий словарь с инкрементом количества уже существующего города
            # area = vacancy['area']['name']
            # areas[area]= areas.setdefault(area, 0) + 1
        if count > stat_count:
            break #прерываем цикл по страницам, если достигнуто заданное количество просматриваемых вакансий

    # #Сортируем требования по убыванию их количества в просмотренных вакансиях
    # skills = dict(sorted(skills.items(), key=lambda x: x[1], reverse=True))
    
    # Объявляем именованный tuple
    StatName = namedtuple('StatName', ['num', 'name', 'cnt', 'freq'])
    
    # Считаем частоту, с которой встречаются города (области)
    name_counts = Counter(areas_ar)
    # Выбираем top_count самых частых городов
    areas = [StatName(index+1, name, cnt, round(cnt*100/stat_count, 1)) for index, (name, cnt) in enumerate(name_counts.most_common(top_count))]

    #Считаем частоту, с которой встречаются скилы в списке
    name_counts = Counter(skills_ar)
    # Выбираем top_count самых частых скилов
    skills = [StatName(index+1, name, cnt, round(cnt*100/stat_count, 1)) for index, (name, cnt) in enumerate(name_counts.most_common(top_count))]

    # #Выводим среднюю зарплату
    # print(f'\nСредняя зарплата: {int(round(stat.mean(salaries), 0)) if len(salaries)>0 else "-"} рублей')

    # #Выводим требования, их количество и частоту в % с которой требования встречается в просмотренных вакансиях
    # print('\nСтатистика требований в вакансиях:')
    # for skill, count in skills.items():
    #     print(f'"{skill}" {count} ({round(count*100/all_skills_count, 1) if all_skills_count>0 else "-"}%)')

    # #Выводим города, их количество и частоту в % с которой города встречается в просмотренных вакансиях
    # print('\nСтатистика вакансий по городам (странам):')
    # for area, count in areas.items():
    #     print(f'"{area}" {count} ({round(count*100/all_areas_count, 1) if all_areas_count>0 else "-"}%)')

    # #Готовим json для сохранения в файл словаря требований
    # text = json.dumps(skills, sort_keys=False, indent=4, ensure_ascii=False)
    # #Сохраняем требования и их количество в файл json
    # with open('skills.json', 'w', encoding='utf-8') as file:
    #     file.write(text)

    # #Готовим json для сохранения в файл словаря городов
    # text = json.dumps(areas, sort_keys=False, indent=4, ensure_ascii=False)
    # #Сохраняем города и их количество в файл json
    # with open('areas.json', 'w', encoding='utf-8') as file:
    #     file.write(text)
    return {
        'query_string': query_string,
        'vacancies_count': vacancies_count,
        'average_salary': int(round(stat.mean(salaries), 0)) if len(salaries)>0 else -1,
        'skills': skills,
        'areas': areas,
        'stat_count': stat_count,
        'top_count': top_count
        }