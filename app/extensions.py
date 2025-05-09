from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

db = SQLAlchemy()  # Define db globally
cache = Cache()