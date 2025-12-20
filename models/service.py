"""
Service model for Panda Spa application.
Represents spa services offered (thermal baths, massages, tea therapy).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, CheckConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class Service(Base):
    """
    Service model representing spa services offered at Panda Spa.
    
    Attributes:
        id: Unique service identifier
        name: Service name (e.g., "Hot Spring Bath", "Bamboo Massage")
        service_type: Type of service (thermal_bath, massage, tea_therapy)
        description: Detailed service description
        duration_minutes: Service duration in minutes
        price: Service price
        is_available: Whether service is currently available
        max_capacity: Maximum customers per service slot
        created_at: Service creation timestamp
        popularity_score: Calculated popularity based on bookings
    """
    
    __tablename__ = 'services'
    
    # Service types
    THERMAL_BATH = "thermal_bath"
    MASSAGE = "massage"
    TEA_THERAPY = "tea_therapy"
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    service_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Service details
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    max_capacity = Column(Integer, default=1, nullable=False)
    
    # Status
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    popularity_score = Column(Float, default=0.0, nullable=False)
    
    # Relationships (backref is defined in Appointment model)
    # appointments - backref from Appointment
    
    # Constraints
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('duration_minutes > 0', name='check_duration_positive'),
        CheckConstraint('max_capacity > 0', name='check_capacity_positive'),
    )
    
    def __init__(self, name: str, service_type: str, duration_minutes: int, price: float,
                 description: str = None, max_capacity: int = 1, is_available: bool = True):
        """
        Initialize a new Service.
        
        Args:
            name: Service name (must be unique)
            service_type: Type of service (thermal_bath, massage, tea_therapy)
            duration_minutes: Service duration in minutes
            price: Service price (must be > 0)
            description: Optional service description
            max_capacity: Maximum customers per slot (default: 1)
            is_available: Whether service is available (default: True)
        """
        self.name = name
        self.service_type = service_type
        self.duration_minutes = duration_minutes
        self.price = price
        self.description = description
        self.max_capacity = max_capacity
        self.is_available = is_available
        self.popularity_score = 0.0
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def get_service_types(cls):
        """Get list of valid service types."""
        return [cls.THERMAL_BATH, cls.MASSAGE, cls.TEA_THERAPY]
    
    def to_dict(self) -> dict:
        """
        Convert service to dictionary representation.
        
        Returns:
            Dictionary with all service fields
        """
        return {
            'id': self.id,
            'name': self.name,
            'service_type': self.service_type,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'price': self.price,
            'max_capacity': self.max_capacity,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'popularity_score': self.popularity_score
        }
    
    def __repr__(self) -> str:
        """String representation of Service."""
        return f"<Service(id={self.id}, name='{self.name}', type='{self.service_type}', price=${self.price})>"

