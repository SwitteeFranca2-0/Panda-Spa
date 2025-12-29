"""
Feeling-Service Mapping model for Panda Spa.
Allows customization of which services are recommended for each feeling.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from database.base import Base


class FeelingServiceMapping(Base):
    """
    Mapping between customer feelings and recommended services.
    Allows customization of recommendations.
    
    Attributes:
        id: Unique mapping identifier
        feeling: Customer feeling/mood (e.g., "stressed", "tired")
        service_id: ID of the service to recommend
        priority: Priority/order (lower = higher priority, 1 = most recommended)
        is_active: Whether this mapping is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = 'feeling_service_mappings'
    
    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    feeling = Column(String(50), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    
    # Configuration
    priority = Column(Integer, default=1, nullable=False)  # Lower = higher priority
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", backref="feeling_mappings")
    
    # Unique constraint: one mapping per feeling-service pair
    __table_args__ = (
        UniqueConstraint('feeling', 'service_id', name='unique_feeling_service_mapping'),
    )
    
    def __init__(self, feeling: str, service_id: int, priority: int = 1, is_active: bool = True):
        """
        Initialize a new FeelingServiceMapping.
        
        Args:
            feeling: Customer feeling/mood
            service_id: ID of the service
            priority: Priority order (default: 1)
            is_active: Whether mapping is active (default: True)
        """
        self.feeling = feeling
        self.service_id = service_id
        self.priority = priority
        self.is_active = is_active
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert mapping to dictionary representation."""
        return {
            'id': self.id,
            'feeling': self.feeling,
            'service_id': self.service_id,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<FeelingServiceMapping(feeling='{self.feeling}', service_id={self.service_id}, priority={self.priority})>"


