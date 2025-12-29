"""
Mood-Based Recommendation Service.
Links customer feelings → recommended services → suggested extras.
"""

from typing import List, Tuple, Optional, Dict
from database.db_manager import DatabaseManagement
from models.service import Service
from models.extra import Extra
from models.customer import Customer
from models.appointment import Appointment
from models.feeling_service_mapping import FeelingServiceMapping


class MoodRecommendationService:
    """
    Service that provides recommendations based on customer mood/feeling.
    Creates a link: Feeling → Service → Extras
    """
    
    # Feeling categories and their service matches
    FEELING_SERVICE_MAP = {
        "stressed": {
            "services": ["thermal_bath", "massage"],
            "priority": ["thermal_bath"],  # Most effective for this feeling
            "description": "Perfect for melting away tension and stress"
        },
        "tired": {
            "services": ["massage", "tea_therapy"],
            "priority": ["massage"],
            "description": "Rejuvenate your energy and restore balance"
        },
        "celebrating": {
            "services": ["thermal_bath", "massage", "tea_therapy"],
            "priority": ["thermal_bath", "massage"],
            "description": "Treat yourself to something special"
        },
        "relaxed": {
            "services": ["tea_therapy", "thermal_bath"],
            "priority": ["tea_therapy"],
            "description": "Maintain your peaceful state"
        },
        "energetic": {
            "services": ["massage", "thermal_bath"],
            "priority": ["massage"],
            "description": "Channel your energy into wellness"
        },
        "exploring": {
            "services": ["tea_therapy", "thermal_bath", "massage"],
            "priority": ["tea_therapy"],  # Often less tried
            "description": "Discover new experiences"
        },
        "sore": {
            "services": ["massage"],
            "priority": ["massage"],
            "description": "Relief for tired muscles"
        },
        "indulgent": {
            "services": ["thermal_bath", "massage"],
            "priority": ["thermal_bath"],
            "description": "Luxury experience awaits"
        }
    }
    
    # Service to Extras mapping
    SERVICE_EXTRAS_MAP = {
        "thermal_bath": {
            "stressed": ["aromatherapy", "extended_time"],
            "tired": ["aromatherapy", "premium_tea"],
            "celebrating": ["premium_tea", "extended_time", "special_treatment"],
            "relaxed": ["aromatherapy"],
            "energetic": ["extended_time"],
            "exploring": ["aromatherapy", "premium_tea"],
            "sore": ["hot_stones", "extended_time"],
            "indulgent": ["premium_tea", "extended_time", "special_treatment"]
        },
        "massage": {
            "stressed": ["aromatherapy", "hot_stones"],
            "tired": ["aromatherapy", "extended_time"],
            "celebrating": ["hot_stones", "extended_time", "special_treatment"],
            "relaxed": ["aromatherapy"],
            "energetic": ["hot_stones"],
            "exploring": ["aromatherapy", "hot_stones"],
            "sore": ["hot_stones", "extended_time"],
            "indulgent": ["hot_stones", "extended_time", "special_treatment"]
        },
        "tea_therapy": {
            "stressed": ["premium_tea", "extended_time"],
            "tired": ["premium_tea"],
            "celebrating": ["premium_tea", "special_treatment"],
            "relaxed": ["premium_tea"],
            "energetic": ["premium_tea"],
            "exploring": ["premium_tea"],
            "sore": ["premium_tea"],
            "indulgent": ["premium_tea", "extended_time", "special_treatment"]
        }
    }
    
    def __init__(self, db_manager: DatabaseManagement):
        """
        Initialize mood recommendation service.
        
        Args:
            db_manager: DatabaseManagement instance
        """
        self.db_manager = db_manager
    
    def get_recommendations_by_feeling(self, feeling: str, customer_id: Optional[int] = None) -> Dict:
        """
        Get service and extra recommendations based on customer feeling.
        First checks database mappings, then falls back to hardcoded mappings.
        
        Args:
            feeling: Customer's current feeling/mood
            customer_id: Optional customer ID for personalized recommendations
            
        Returns:
            Dictionary with:
                - services: List of recommended services
                - extras_by_service: Dict mapping service_id to list of extras
                - description: Why these recommendations
        """
        feeling_lower = feeling.lower().strip()
        
        # First, try to get mappings from database
        db_mappings = self.db_manager.find(
            FeelingServiceMapping,
            feeling=feeling_lower,
            is_active=True
        )
        
        recommended_services = []
        
        if db_mappings:
            # Use database mappings (sorted by priority)
            db_mappings.sort(key=lambda m: m.priority)
            for mapping in db_mappings:
                service = self.db_manager.get_by_id(Service, mapping.service_id)
                if service and service.is_available:
                    if service not in recommended_services:
                        recommended_services.append(service)
                        if len(recommended_services) >= 3:
                            break
        else:
            # Fall back to hardcoded mappings
            if feeling_lower not in self.FEELING_SERVICE_MAP:
                # Default to "exploring" if feeling not recognized
                feeling_lower = "exploring"
            
            feeling_data = self.FEELING_SERVICE_MAP[feeling_lower]
            recommended_service_types = feeling_data["priority"]
            
            # Get available services matching the feeling
            for service_type in recommended_service_types:
                services = self.db_manager.find(
                    Service,
                    service_type=service_type,
                    is_available=True
                )
                recommended_services.extend(services)
            
            # If not enough services, add from secondary list
            if len(recommended_services) < 2:
                for service_type in feeling_data["services"]:
                    if service_type not in recommended_service_types:
                        services = self.db_manager.find(
                            Service,
                            service_type=service_type,
                            is_available=True
                        )
                        for service in services:
                            if service not in recommended_services:
                                recommended_services.append(service)
                                if len(recommended_services) >= 3:
                                    break
                    if len(recommended_services) >= 3:
                        break
        
        # Get extras for each recommended service
        extras_by_service = {}
        for service in recommended_services[:3]:  # Limit to top 3 services
            service_type = service.service_type
            if service_type in self.SERVICE_EXTRAS_MAP:
                feeling_extras = self.SERVICE_EXTRAS_MAP[service_type].get(feeling_lower, [])
                
                # Find actual extra objects
                service_extras = []
                for extra_name in feeling_extras:
                    # Try to find by name (case-insensitive partial match)
                    all_extras = self.db_manager.get_all(Extra)
                    for extra in all_extras:
                        if extra.is_available and extra.is_compatible_with(service_type):
                            # Check if extra name contains the keyword
                            if extra_name.lower() in extra.name.lower() or \
                               any(keyword in extra.name.lower() for keyword in extra_name.split('_')):
                                service_extras.append(extra)
                                break
                
                if service_extras:
                    extras_by_service[service.id] = service_extras
        
        # Get description (use hardcoded if available, otherwise generic)
        if feeling_lower in self.FEELING_SERVICE_MAP:
            description = self.FEELING_SERVICE_MAP[feeling_lower]["description"]
        else:
            description = f"Services recommended for when you're feeling {feeling_lower}"
        
        return {
            "feeling": feeling_lower,
            "services": recommended_services[:3],
            "extras_by_service": extras_by_service,
            "description": description,
            "message": self._generate_recommendation_message(feeling_lower, recommended_services)
        }
    
    def _generate_recommendation_message(self, feeling: str, services: List[Service]) -> str:
        """
        Generate a creative, personalized recommendation message.
        
        Args:
            feeling: Customer feeling
            services: Recommended services
            
        Returns:
            Personalized message string
        """
        messages = {
            "stressed": [
                "🧘 Melt away your stress with our calming thermal waters",
                "💆 Let tension dissolve in our peaceful spa sanctuary",
                "🌊 Find your calm in our therapeutic waters"
            ],
            "tired": [
                "⚡ Recharge your energy with a revitalizing experience",
                "🌿 Restore your balance and feel refreshed",
                "✨ Renew your spirit with our rejuvenating treatments"
            ],
            "celebrating": [
                "🎉 Treat yourself to something special today!",
                "✨ You deserve this luxurious experience",
                "🌟 Celebrate with our premium spa treatments"
            ],
            "relaxed": [
                "☕ Maintain your peaceful state with gentle therapy",
                "🌸 Continue your journey of tranquility",
                "🌙 Keep the calm flowing"
            ],
            "energetic": [
                "💪 Channel your energy into wellness",
                "🔥 Transform your vitality into relaxation",
                "⚡ Harness your energy for ultimate balance"
            ],
            "exploring": [
                "🔍 Discover new experiences waiting for you",
                "🌟 Try something you've never experienced before",
                "🌿 Expand your wellness horizons"
            ],
            "sore": [
                "💆 Relief for your tired muscles awaits",
                "🔥 Soothe your aches with therapeutic treatments",
                "🌿 Gentle care for your body"
            ],
            "indulgent": [
                "💎 Luxury experience awaits you",
                "✨ Indulge in our premium offerings",
                "🌟 Treat yourself to the finest"
            ]
        }
        
        import random
        base_message = random.choice(messages.get(feeling, messages["exploring"]))
        
        if services:
            service_names = ", ".join([s.name for s in services[:2]])
            return f"{base_message} — Try: {service_names}"
        
        return base_message
    
    def get_available_feelings(self) -> List[str]:
        """
        Get list of available feeling options.
        Combines database mappings with hardcoded feelings.
        
        Returns:
            List of feeling strings
        """
        # Get feelings from database mappings
        db_mappings = self.db_manager.get_all(FeelingServiceMapping)
        db_feelings = set(m.feeling for m in db_mappings)
        
        # Combine with hardcoded feelings
        all_feelings = set(self.FEELING_SERVICE_MAP.keys()) | db_feelings
        
        # Return sorted list
        return sorted(list(all_feelings))
    
    def get_extras_for_service_and_feeling(self, service_id: int, feeling: str) -> List[Extra]:
        """
        Get recommended extras for a specific service and feeling.
        
        Args:
            service_id: ID of the service
            feeling: Customer feeling
            
        Returns:
            List of recommended Extra objects
        """
        service = self.db_manager.get_by_id(Service, service_id)
        if not service:
            return []
        
        feeling_lower = feeling.lower().strip()
        service_type = service.service_type
        
        if service_type not in self.SERVICE_EXTRAS_MAP:
            return []
        
        feeling_extras = self.SERVICE_EXTRAS_MAP[service_type].get(feeling_lower, [])
        
        # Find actual extra objects
        recommended_extras = []
        all_extras = self.db_manager.get_all(Extra)
        
        for extra_name in feeling_extras:
            for extra in all_extras:
                if extra.is_available and extra.is_compatible_with(service_type):
                    if extra_name.lower() in extra.name.lower() or \
                       any(keyword in extra.name.lower() for keyword in extra_name.split('_')):
                        if extra not in recommended_extras:
                            recommended_extras.append(extra)
                            break
        
        return recommended_extras

