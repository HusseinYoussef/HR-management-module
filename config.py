
database_URI = 'mysql+pymysql://admin:password@localhost/hr_db'

def configs(app):
    # hardcoded for simplicity but it should be environment variable

    app.config["SQLALCHEMY_DATABASE_URI"] = database_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = 'my_secret_key'