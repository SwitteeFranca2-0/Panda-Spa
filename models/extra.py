"""
Extra/Add-on model for Panda Spa application.
Represents additional services or enhancements that can be added to main services.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, CheckConstraint
from database.base import Base


class Extra(Base):
    """
    Extra model representing add-on services or enhancements.
    
    Examples:
        - Aromatherapy add-on
        - Extended session time
        - Premium tea selection
        - Special essential oils
        - Hot stone upgrade
    
    Attributes:
        id: Unique extra identifier
        name: Extra name (e.g., "Lavender Aromatherapy", "Extended 30min")
        description: Detailed description
        price: Additional price for this extra
        duration_minutes: Additional time added (0 if no time extension)
        is_available: Whether extra is currently available
        compatible_service_types: Service types this extra can be added to
        created_at: Creation timestamp
    """
    
    __tablename__ = 'extras'
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Pricing and duration
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=0, nullable=False)  # Additional time
    
    # Availability
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Compatibility: comma-separated service types (e.g., "thermal_bath,massage")
    compatible_service_types = Column(String(200), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_extra_price_non_negative'),
        CheckConstraint('duration_minutes >= 0', name='check_extra_duration_non_negative'),
    )
    
    def __init__(self, name: str, price: float, description: str = None,
                 duration_minutes: int = 0, is_available: bool = True,
                 compatible_service_types: str = None):
        """
        Initialize a new Extra.
        
        Args:
            name: Extra name (must be unique)
            price: Additional price (must be >= 0)
            description: Optional description
            duration_minutes: Additional time in minutes (default: 0)
            is_available: Whether extra is available (default: True)
            compatible_service_types: Comma-separated service types (e.g., "thermal_bath,massage")
        """
        self.name = name
        self.price = price
        self.description = description
        self.duration_minutes = duration_minutes
        self.is_available = is_available
        self.compatible_service_types = compatible_service_types
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def is_compatible_with(self, service_type: str) -> bool:
        """
        Check if this extra is compatible with a service type.
        
        Args:
            service_type: Service type to check
            
        Returns:
            True if compatible, False otherwise
        """
        if not self.compatible_service_types:
            return True  # If not specified, assume compatible with all
        
        compatible = [s.strip() for s in self.compatible_service_types.split(',')]
        return service_type in compatible
    
    def to_dict(self) -> dict:
        """
        Convert extra to dictionary representation.
        
        Returns:
            Dictionary with all extra fields
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration_minutes': self.duration_minutes,
            'is_available': self.is_available,
            'compatible_service_types': self.compatible_service_types,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        """String representation of Extra."""
        return f"<Extra(id={self.id}, name='{self.name}', price=${self.price})>"


