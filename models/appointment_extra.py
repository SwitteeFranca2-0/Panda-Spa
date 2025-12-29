"""
Association table for many-to-many relationship between Appointments and Extras.
"""

from sqlalchemy import Column, Integer, ForeignKey, Table
from database.base import Base

# Association table for appointments and extras (many-to-many)
appointment_extra_association = Table(
    'appointment_extras',
    Base.metadata,
    Column('appointment_id', Integer, ForeignKey('appointments.id'), primary_key=True),
    Column('extra_id', Integer, ForeignKey('extras.id'), primary_key=True)
)


