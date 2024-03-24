import sqlite3

class VacancyDB:
    """Класс работы с БД вакансий
    """
    def __init__(self, db_file_name: str):
        self.conn = sqlite3.connect(db_file_name)
        self.cursor = self.conn.cursor()
        # self.cursor.execute('select area_id from areas where name = ?', ('Москва',))
        # hh_id = 1
        # self.cursor.execute('select vacancy_id from vacancies where hh_id = ?', (hh_id,))#95276743
        # t=self.cursor.fetchone()[0]
        # hh_id = 95276743
        # self.cursor.execute('select vacancy_id from vacancies where hh_id = ?', (hh_id,))
        # t=self.cursor.fetchone()[0]
        # print(t)

    def __p_set_area(self, name: str) -> bool :
        try:
            self.cursor.execute('insert into areas (area_id, name) values (?, ?)', (None, name))
            self.conn.commit()
            return True
        except:
            return False

    def __p_get_area_id(self, name: str) -> int:
        try:
            self.cursor.execute('select area_id from areas where name = ?', (name,))
            result = self.cursor.fetchone()[0]
            return result
        except:
            return 0

    def __p_get_set_area_id(self, name: str) -> int:
        """Получение area id по названию города (территории).
        Если указанного названия нет в БД, будет заведена новая запись и получен ее id

        Args:
            name (str): название города (территории)

        Returns:
            int: id города (территории) в БД
        """
        result = self.__p_get_area_id (name=name)
        if result == 0:
            if self.__p_set_area(name=name):
                result = self.__p_get_area_id (name=name)
        return result

    #____________________________________________________________________

    def __p_set_skill(self, name: str) -> bool:
        try:
            self.cursor.execute('insert into skills (skill_id, name) values (?, ?)', (None, name))
            self.conn.commit()
            return True
        except:
            return False

    def __p_get_skill_id(self, name: str) -> int:
        try:
            self.cursor.execute('select skill_id from skills where name = ?', (name,))
            result = self.cursor.fetchone()[0]
            return result
        except:
            return 0

    def __p_get_set_skill_id(self, name: str) -> int:
        """Получение skill_id по имени навыка. Если указанного навыка нет в БД,
        будет заведена новая запись и получен ее if

        Args:
            name (str): название навыка

        Returns:
            int: id навыка в БД
        """
        result = self.__p_get_skill_id (name=name)
        if result == 0:
            if self.__p_set_skill(name=name):
                result = self.__p_get_skill_id (name=name)
        return result

    #____________________________________________________________________

    def __p_set_vacancy(self, hh_id: int, name: str, salary: float, area_id) -> bool:
        try:
            self.cursor.execute('insert into vacancies (vacancy_id, hh_id, name, salary, area_id) values (?, ?, ?, ?, ?)', (None, hh_id, name, salary, area_id))
            self.conn.commit()
            return True
        except:
            return False

    def get_vacancy_id(self, hh_id: int) -> int:
        try:
            self.cursor.execute('select vacancy_id from vacancies where hh_id = ?', (hh_id,))
            result = self.cursor.fetchone()[0]
            return result
        except:
            return 0

    def __p_get_set_vacancy_id(self, hh_id: int, name: str, salary: float, area_id) -> int:
        result = self.get_vacancy_id (hh_id=hh_id)
        if result == 0:
            if self.__p_set_vacancy(hh_id=hh_id, name=name, salary=salary, area_id=area_id):
                result = self.get_vacancy_id (hh_id=hh_id)
        return result

    def __p_is_vacancy_exists(self, hh_id: int) -> bool:
        result = self.get_vacancy_id (hh_id=hh_id) > 0
        return result

    def set_vacancy(self, hh_id: int, name: str, salary: float, area_name: str, skills: list[str]) -> bool:
        if not self.__p_is_vacancy_exists(hh_id=hh_id):
            area_id = self.__p_get_set_area_id(name=area_name)
            vacancy_id = self.__p_get_set_vacancy_id(hh_id=hh_id, name=name, salary=salary, area_id=area_id)
            for skill in skills:
                skill_id = self.__p_get_set_skill_id(name=skill)
                try:
                    self.cursor.execute('insert into vacancies_skills (vacancy_skill_id, vacancy_id, skill_id) values (?, ?, ?)', (None, vacancy_id, skill_id))
                    self.conn.commit()
                except:
                    try:
                        self.cursor.execute('delete from vacancies_skills where vacancy_id = ?', (vacancy_id,))
                        self.conn.commit()
                    except:
                        pass
                    return False
        return True

    def get_vacancy_data_by_vacancy_id(self, vacancy_id: int) -> str:
        try:
            self.cursor.execute('SELECT v.salary, a.name FROM vacancies v join areas a on a.area_id = v.area_id where vacancy_id = ?', (vacancy_id,))
            result = self.cursor.fetchone()
            return result
        except:
            return ''

    def get_skills_by_vacancy_id(self, vacancy_id: int) -> list[str]:
        try:
            self.cursor.execute('SELECT s.name FROM vacancies_skills vs join skills s on s.skill_id = vs.skill_id where vs.vacancy_id = ?', (vacancy_id,))
            result = self.cursor.fetchall()
            return [r[0] for r in result]
        except:
            return []