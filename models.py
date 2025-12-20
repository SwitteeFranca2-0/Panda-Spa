"""
Central import file for all models.
Provides easy access to all model classes from a single import.
"""

from models.customer import Customer
from models.service import Service
from models.appointment import Appointment
from models.supplier import Supplier
from models.financial_record import FinancialRecord
from models.customer_preference import CustomerPreference

__all__ = [
    'Customer',
    'Service',
    'Appointment',
    'Supplier',
    'FinancialRecord',
    'CustomerPreference'
]

