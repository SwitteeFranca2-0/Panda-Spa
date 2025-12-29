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
from models.extra import Extra
from models.feeling_service_mapping import FeelingServiceMapping

__all__ = [
    'Customer',
    'Service',
    'Appointment',
    'Supplier',
    'FinancialRecord',
    'CustomerPreference',
    'Extra',
    'FeelingServiceMapping'
]

