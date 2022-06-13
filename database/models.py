from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, Time
import json


db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

# Models

class Employee(db.Model):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), nullable=False)

    logs = db.relationship('Log', backref='employee')

    def __repr__(self) -> str:
        return f'Employee email: {self.email}'
    

class Attendence(db.Model):
    __tablename__ = 'attendences'

    id = Column(Integer, primary_key=True)
    checkin = Column(Time)
    checkout = Column(Time)
    date = Column(Date)

    logs = db.relationship('Log', backref='attendence')

    def __repr__(self) -> str:
        return f'Attendence Record, checkin: {self.checkin}, checkout: {self.checkout}, date: {self.date}'


class Log(db.Model):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, db.ForeignKey('employees.id', ondelete='cascade'), nullable=False)
    attendence_id = Column(Integer, db.ForeignKey('attendences.id', ondelete='cascade'), nullable=False)

    employee_log = db.relationship('Employee', backref='log')
    attendence_log = db.relationship('Attendence', backref='log')
