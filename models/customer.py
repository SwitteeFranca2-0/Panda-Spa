"""
Customer model for Panda Spa application.
Represents forest animals visiting the spa.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.orm import relationship

from database.base import Base


class Customer(Base):
    """
    Customer model representing forest animals visiting Panda Spa.
    
    Attributes:
        id: Unique customer identifier
        name: Customer's name (e.g., "Bamboo Bear", "Forest Fox")
        species: Animal species (e.g., "Bear", "Fox", "Deer", "Rabbit")
        contact_info: Contact information (phone, email, or forest location)
        created_at: Account creation timestamp
        last_visit: Date of last spa visit
        total_visits: Total number of appointments
        total_spent: Cumulative amount spent at spa
        notes: Additional notes about customer
        is_active: Whether customer account is active
    """
    
    __tablename__ = 'customers'
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    contact_info = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_visit = Column(DateTime, nullable=True)
    
    # Statistics
    total_visits = Column(Integer, default=0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)
    
    # Additional info
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships (backrefs are defined in Appointment model)
    # appointments - backref from Appointment
    # preferences - will be added when CustomerPreference model is created
    
    def __init__(self, name: str, species: str, contact_info: str = None, 
                 notes: str = None, is_active: bool = True):
        """
        Initialize a new Customer.
        
        Args:
            name: Customer's name
            species: Animal species
            contact_info: Optional contact information
            notes: Optional notes
            is_active: Whether account is active (default: True)
        """
        self.name = name
        self.species = species
        self.contact_info = contact_info
        self.notes = notes
        self.is_active = is_active
        self.total_visits = 0
        self.total_spent = 0.0
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Convert customer to dictionary representation.
        
        Returns:
            Dictionary with all customer fields
        """
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
            'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_visit': self.last_visit.isoformat() if self.last_visit else None,
            'total_visits': self.total_visits,
            'total_spent': self.total_spent,
            'notes': self.notes,
            'is_active': self.is_active
        }
    
    def __repr__(self) -> str:
        """String representation of Customer."""
        return f"<Customer(id={self.id}, name='{self.name}', species='{self.species}')>"

