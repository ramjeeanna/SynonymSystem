from flask import Flask
from flask_restful import Api, Resource
from controller.SynonymSystem import SynonymSystem
from flask_caching import Cache
from sqlalchemy import text
from app.extensions import db, cache
import json, os

app_config = {}

def configure_cache(app):
    cache_config = app_config['cache_config']
    cache_type = cache_config.get(type, "simple").lower()
    app.config['CACHE_TYPE'] = 'simple'
    if cache_type == 'redis' and cache_config.get("url", None):
        app.config['CACHE_TYPE'] = 'redis'
        app.config['CACHE_REDIS_URL'] = cache_config.get("url")
    app.config['CACHE_DEFAULT_TIMEOUT'] = cache_config.get("cache_ttl", 300)
    cache.init_app(app)

def configure_db(app):
    db_config = app_config['db_config']
    db_uname = db_config.get("user_name", "root")
    db_pwd = db_config.get("password", "password")
    db_server_name = db_config.get('server_name','localhost')
    db_name = db_config.get('db_name', 'master')
    conn_str = "mssql+pyodbc://{}:{}@{}/{}?driver=ODBC+Driver+17+for+SQL+Server".format(db_uname,
                                                                                        db_pwd,db_server_name, db_name)
    app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_size": db_config.get('pool_size',10),
        "max_overflow": db_config.get('max_overflow',5),
        "pool_timeout": db_config.get('pool_timeout',30),
        "pool_recycle": db_config.get('pool_recycle',1800)
    }
    print("Connection string is ", conn_str)
    db.init_app(app)

def create_app():
    global app_config
    file_name = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.cfg')
    print(file_name)
    with open(file_name) as app_cfg_fp:
        app_config = json.load(app_cfg_fp)
        print(app_config)
    app = Flask(__name__)
    api = Api(app,prefix='/api/v1')
    configure_cache(app)
    configure_db(app)
    print("Configured app config is ", app.config)
# Add resource routes
    api.add_resource(SynonymSystem, "/synonym", "/synonym/<inword>")

    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))  # Simple DB query
            print("Database connection successful!")
    except Exception as e:
        print(f" Database connection failed: {e}")
    return app
