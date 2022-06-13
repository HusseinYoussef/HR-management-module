# HR management module
HR management system is what is used by companies to manage & organize human resources, like
tracking the employee's attendance, leaves, expenses, ...etc.

## Tech
* Python
* Flask
* MySQL
* Redis
* Docker

## Get Started
* Install python packages, run:

    `pip install -r requirements.txt`
* Make sure Docker is installed, run:
    
    `docker-compose up`
* Start the server

    `py .\api.py`
## Models
* Employee
```
{
    id: integer (primary key)
    email: string (unique)
    password: hashed string
}
```

* Attendence
```
{
    id: integer (primary key)
    check_in: time
    check_out: time
    date: date
}
```

* Logs
```
{
    id: integer
    employee_id: integer (foreign key -> employee table) 
    attendence_id: integer (foreign key -> employee table)
}
```
## Endpoints

### POST /register
* Register a new employee if email is unique (assumed email is valid).
* request body:

```
{
    "email": "hussein@gmail.com",
    "password": "my_password"
}
```

* returns:
```
{
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Imh1c3NlaW5AZ21haWwuY29tIiwiZXhwIjoxNjU1MTM0NTM0fQ.DYOZ4pxyBBA1uMR3-g-8EHAUmdRz9OuVshiAJCn6eBc"
}
```

### POST /login
* logins an existing employee to get an auth token.
* request body:

```
{
    "email": "hussein@gmail.com",
    "password": "my_password"
}
```

* returns:
```
{
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Imh1c3NlaW5AZ21haWwuY29tIiwiZXhwIjoxNjU1MTM0NTM0fQ.DYOZ4pxyBBA1uMR3-g-8EHAUmdRz9OuVshiAJCn6eBc"
}
```

### POST /attendences
* get all attendences records of an employee.
* request body:

```
{
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Imh1c3NlaW5AZ21haWwuY29tIiwiZXhwIjoxNjU1MTM0NTM0fQ.DYOZ4pxyBBA1uMR3-g-8EHAUmdRz9OuVshiAJCn6eBc"
}
```

* returns:
```
{
    "records": [
        "record 1: check-in at 09:04:03 and check-out at 09:07:03",
        "record 2: check-in at 08:05:03 and check-out at 09:01:03"
    ]
}

```
### POST /checkin
* Make a check-in for an employee.
* request body:

```
{
    "checkin": "05:44:04",
    "date": "2022-06-13",
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Imh1c3NlaW5AZ21haWwuY29tIiwiZXhwIjoxNjU1MTQxMjA0fQ.QmDHeltebebKzJBbj0Ik_fFYENenHNL7MgrmhXTW7ws"
}
```

* returns:
```
{
    "message": "checked in!"
}
```

### POST /checkout
* Make a check-out for an employee. (There are validations to make sure there is a check-in for the same day)
* request body:

```
{
    "checkout": "07:50:04",
    "date": "2022-06-13",
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Imh1c3NlaW5AZ21haWwuY29tIiwiZXhwIjoxNjU1MTQxMjA0fQ.QmDHeltebebKzJBbj0Ik_fFYENenHNL7MgrmhXTW7ws"
}
```

* returns if it is a valid check-out (no overlapping and check-out time is greater than check-in time):
```
{
    "message": "checked-out: Attendence Record, checkin: 05:44:04, checkout: 07:50:04, date: 2022-06-13"
}
```

## Todos
* Unit Tests.
* Admin Role.
* Overtime hours.
