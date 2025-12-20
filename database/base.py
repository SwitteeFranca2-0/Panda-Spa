"""
SQLAlchemy declarative base for all models.
All model classes should inherit from this Base.
"""

from sqlalchemy.orm import declarative_base

# Create the declarative base that all models will inherit from
Base = declarative_base()

