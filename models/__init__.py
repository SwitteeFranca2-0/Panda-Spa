"""
Models package for Panda Spa application.
All model classes are imported here for easy access.
"""

from .customer import Customer
from .service import Service
from .appointment import Appointment
from .supplier import Supplier
from .financial_record import FinancialRecord
from .customer_preference import CustomerPreference
from .extra import Extra
from .feeling_service_mapping import FeelingServiceMapping

__all__ = ['Customer', 'Service', 'Appointment', 'Supplier', 'FinancialRecord', 'CustomerPreference', 'Extra', 'FeelingServiceMapping']

