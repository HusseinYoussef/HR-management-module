from distutils.command.config import config
from tabnanny import check
from textwrap import wrap
from flask import Flask, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from config import configs
from database.models import Log, db, setup_db, Employee, Log, Attendence 
from functools import wraps
import datetime
import jwt
import redis

# Init

app = Flask(__name__)
cache = redis.Redis(host='localhost', port=6379, db=0)
configs(app)
setup_db(app)

######
#  Endpoints
######

def generate_token(email):
    return jwt.encode({'email': email, 
    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'], algorithm="HS256")

def requires_auth():
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.get_json().get('auth_token', None)

            if not token:
                return jsonify({'message': 'Token is missing!'}), 400
            
            try:
                data = jwt.decode(jwt=token, key=app.config['SECRET_KEY'], algorithms=["HS256"])
            except:
                return jsonify({'message': 'Token is invalid!'}), 401
            return f(data, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/register", methods=['POST'])
def register():
    body = request.get_json()

    # require body
    if body is None:
        abort(400)

    # get body params
    email = body.get('email', None)
    password = body.get('password', None)

    if not email:
        return jsonify({'message': 'email is missing'}), 400
    if not password:
        return jsonify({'message': 'password is missing'}), 400
    if len(password) < 5:
        return jsonify({'message': 'password length should be greater than 5'}), 400
    
    emp = Employee(email=email, password=generate_password_hash(password))
    try:
        db.session.add(emp)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'message': 'email is already used!'}), 400

    token = generate_token(email)
    return jsonify({'auth_token': token}), 201


@app.route("/login", methods=['POST'])
def login():
    body = request.get_json()

    # require body
    if body is None:
        abort(400)

    # get body params
    email = body.get('email', None)
    password = body.get('password', None)

    if not email:
        return jsonify({'message': 'email is missing'}), 400
    if not password:
        return jsonify({'message': 'password is missing'}), 400
    if len(password) < 5:
        return jsonify({'message': 'password length should be greater than 5'}), 400
    
    emp = Employee.query.filter_by(email=email).first()
    if emp is None:
        return jsonify({'message': "email doesn't exist"}), 400
    
    if not check_password_hash(emp.password, password):
        return jsonify({'message': 'password is wrong!'}), 400

    token = generate_token(email)
    return jsonify({'auth_token': token}), 200


@app.route("/attendences", methods=['POST'])
@requires_auth()
def get_logs(payload):

    email = payload['email']

    emp = Employee.query.filter_by(email=email).first()
    logs = Log.query.filter_by(employee_id=emp.id).all()

    if len(logs) == 0:
        return jsonify({'message': 'no logs found'}), 200

    res = []
    for idx, log in enumerate(logs):
        res.append(f'record {idx+1}: check-in at {log.attendence.checkin} and check-out at {log.attendence.checkout}')
    
    return jsonify({'records': res}), 200

@app.route("/checkin", methods=['POST'])
@requires_auth()
def checkin(payload):
    body = request.get_json()

    checkin = body.get('checkin', None)
    date = body.get('date', None)

    if not checkin:
        return jsonify({'message': 'checkin time is missing'}), 400
    if not date:
        return jsonify({'message': 'date is missing'}), 400

    try:
        datetime.datetime.strptime(checkin, "%H:%M:%S")
    except ValueError:
        return jsonify({'message': 'check-in time format is invalid. It should be HH-MM-SS'}), 400
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({'message': 'date format is invalid. It should be YY-MM-DD'}), 400

    email = payload['email']
    if cache.exists(email):
        return jsonify({'message': "this user didn't check-out since last check-in"}), 400
    
    emp = Employee.query.filter_by(email=email).first()
    logs = Log.query.filter_by(employee_id=emp.id).all()

    for log in logs:
        if (checkin >= str(log.attendence.checkin) and checkin <= str(log.attendence.checkout)):
            return jsonify({'message': f'attendence overlapping with {log.attendence}'}), 400
    cache.set(email, f'{checkin},{date}')
    return jsonify({'message': "checked in!"}), 200


@app.route("/checkout", methods=['POST'])
@requires_auth()
def checkout(payload):
    body = request.get_json()

    checkout = body.get('checkout', None)
    date = body.get('date', None)

    if not checkout:
        return jsonify({'message': 'checkout time is missing'}), 400
    if not date:
        return jsonify({'message': 'date is missing'}), 400

    try:
        datetime.datetime.strptime(checkout, "%H:%M:%S")
    except ValueError:
        return jsonify({'message': 'check-in time format is invalid. It should be HH-MM-SS'}), 400
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({'message': 'date format is invalid. It should be YY-MM-DD'}), 400

    email = payload['email']

    if not cache.exists(email):
        return jsonify({'message': 'You should check-in first'}), 400
    
    checkin, checkin_date = cache.get(email).decode('utf-8').split(',')
    if date != checkin_date:
        return jsonify({'message': 'check-in date is different from check-out date'}), 400

    if checkout <= checkin:
        return jsonify({'message': 'check-out time must be always bigger than check-in time'}), 400

    emp = Employee.query.filter_by(email=email).first()
    logs = Log.query.filter_by(employee_id=emp.id).all()

    for log in logs:
        if (checkout >= str(log.attendence.checkin) and checkout <= str(log.attendence.checkout)) \
         or (checkin <= str(log.attendence.checkin)  and str(log.attendence.checkout) <= checkout):
            return jsonify({'message': f'attendence overlapping with {log.attendence}'}), 400

    attendence = Attendence(checkin=checkin, checkout=checkout, date=date)
    try:
        db.session.add(attendence)
        db.session.commit()
        log = Log(employee_id=emp.id, attendence_id=attendence.id)
        try:
            db.session.add(log)
            db.session.commit()
        except:
            db.session.rollback()
    except:
        db.session.rollback()
        return jsonify({'message': "can't check-out"}), 400

    cache.delete(email)
    return jsonify({'message': f'checked-out: {attendence}'}), 201


if __name__ == '__main__':
    app.run()