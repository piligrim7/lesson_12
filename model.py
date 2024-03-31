from sqlalchemy import Column, Integer, Float, String, ForeignKey, create_engine
from sqlalchemy.orm.decl_api import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///hh.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Area(Base):
    __tablename__ = 'areas'
    area_id = Column(Integer, primary_key=True)
    name = Column(String(24), unique=True)
    
    def __init__(self, name: str):
        self.name = name

    def get_area(name: str):
        result = session.query(Area).filter(Area.name == name).first()
        if result is None:
            result = Area(name=name)
            session.add(result)
            session.commit()
        return result

class Skill(Base):
    __tablename__ = 'skills'
    skill_id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    
    def __init__(self, name: str):
        self.name = name

    def get_skill(name: str):
        result = session.query(Skill).filter(Skill.name == name).first()
        if result is None:
            result = Skill(name=name)
            session.add(result)
            session.commit()
        return result
    
class Vacancy(Base):
    __tablename__ = 'vacancies'
    vacancy_id = Column(Integer, primary_key=True)
    hh_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(64))
    salary = Column(Float)
    area_id = Column(Integer, ForeignKey('areas.area_id'))
    area = relationship('Area')
    
    def __init__(self, hh_id: int, name: str, salary: float, area_name: str):
        self.hh_id = hh_id
        self.name = name
        self.salary = salary
        self.area_id = Area.get_area(name=area_name).area_id

    def get_vacancy(hh_id: int):
        result = session.query(Vacancy).filter(Vacancy.hh_id == hh_id).first()
        return result

    def set_vacancy(hh_id: int, name: str, salary: float, area_name: str, skills: list[str]):
        vacancy = Vacancy.get_vacancy(hh_id = hh_id)
        if vacancy is None:
            vacancy = Vacancy(hh_id=hh_id, name=name, salary=salary, area_name=area_name)
            session.add(vacancy)
            session.commit()
            for skill_name in skills:
                skill = Skill.get_skill(name=skill_name)
                Vacancy_Skill.set_vacancy_skill(vacancy_id=vacancy.vacancy_id,
                                                 skill_id=skill.skill_id
                                                 )
        else:
            return vacancy

class Vacancy_Skill(Base):
    __tablename__ = 'vacancies_skills'
    vacancy_skill_id = Column(Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey('vacancies.vacancy_id'))
    skill_id = Column(Integer, ForeignKey('skills.skill_id'))
    skill = relationship('Skill')

    def __init__(self, vacancy_id: Integer, skill_id: Integer):
        self.vacancy_id = vacancy_id
        self.skill_id = skill_id

    def set_vacancy_skill(vacancy_id: Integer, skill_id: Integer):
        result = Vacancy_Skill(vacancy_id = vacancy_id, skill_id = skill_id)
        session.add(result)
        session.commit()
        return result

    def get_skills_by_vacancy_id(vacancy_id=vacancy_id):
        result = session.query(Skill.name).\
            join(Vacancy_Skill, Vacancy_Skill.skill_id == Skill.skill_id).\
                filter(Vacancy_Skill.vacancy_id == vacancy_id 
            ).all()
        return [r[0] for r in result]

Base.metadata.create_all(engine)