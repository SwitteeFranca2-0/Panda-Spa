"""
Test Data Generation Script for Panda Spa.
Generates realistic test data for all models (at least 15 records each).
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManagement
from models.customer import Customer
from models.service import Service
from models.appointment import Appointment
from models.supplier import Supplier
from models.financial_record import FinancialRecord
from models.customer_preference import CustomerPreference
from models.extra import Extra
from models.feeling_service_mapping import FeelingServiceMapping


def generate_customers(db_manager: DatabaseManagement, count: int = 20) -> list:
    """Generate test customers."""
    print(f"Generating {count} customers...")
    
    species_list = ["Bear", "Fox", "Deer", "Rabbit", "Squirrel", "Owl", "Hedgehog", "Badger", "Raccoon", "Wolf"]
    first_names = ["Bamboo", "Forest", "Misty", "Shadow", "Golden", "Silver", "Crystal", "Amber", "Jade", "Ruby", 
                   "Willow", "Oak", "Pine", "Maple", "Cedar", "Birch", "Elm", "Ash", "Fir", "Spruce"]
    last_names = ["Paw", "Claw", "Tail", "Ear", "Fur", "Whisker", "Fang", "Tooth", "Eye", "Nose"]
    
    customers = []
    for i in range(count):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        species = random.choice(species_list)
        contact = f"forest-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        notes = random.choice([
            None,
            "Prefers morning appointments",
            "Loves hot springs",
            "Regular customer",
            "Allergic to lavender",
            "VIP customer",
            "First-time visitor",
            "Prefers quiet sessions"
        ])
        
        customer = Customer(
            name=name,
            species=species,
            contact_info=contact,
            notes=notes,
            is_active=random.choice([True, True, True, False])  # 75% active
        )
        db_manager.save(customer)
        customers.append(customer)
    
    print(f"✅ Created {len(customers)} customers")
    return customers


def generate_services(db_manager: DatabaseManagement, count: int = 18) -> list:
    """Generate test services."""
    print(f"Generating {count} services...")
    
    # Get existing services
    existing_services = db_manager.get_all(Service)
    existing_names = {s.name for s in existing_services}
    
    thermal_baths = [
        ("Mountain Hot Spring", "Natural thermal waters from mountain springs", 60, 45.00),
        ("Bamboo Grove Bath", "Hot bath surrounded by bamboo", 45, 35.00),
        ("Forest Mist Bath", "Steamy bath with forest aromas", 50, 40.00),
        ("Crystal Clear Pool", "Premium filtered thermal pool", 75, 55.00),
        ("Sunset Thermal", "Evening hot spring experience", 60, 50.00),
        ("Moonlight Bath", "Night-time thermal experience", 90, 65.00),
    ]
    
    massages = [
        ("Bamboo Massage", "Traditional bamboo stick massage", 60, 50.00),
        ("Forest Aromatherapy Massage", "Massage with forest essential oils", 75, 60.00),
        ("Deep Tissue Therapy", "Intensive muscle relief", 90, 75.00),
        ("Gentle Touch Massage", "Light, relaxing massage", 45, 40.00),
        ("Hot Stone Massage", "Heated stone therapy", 90, 70.00),
        ("Panda Paw Massage", "Signature gentle technique", 60, 55.00),
    ]
    
    tea_therapies = [
        ("Bamboo Leaf Tea Ceremony", "Traditional tea ceremony", 45, 30.00),
        ("Herbal Wellness Tea", "Medicinal herb tea session", 60, 35.00),
        ("Premium Tea Tasting", "High-quality tea selection", 90, 50.00),
        ("Relaxation Tea Session", "Calming tea experience", 30, 25.00),
        ("Energizing Tea Blend", "Revitalizing tea therapy", 45, 32.00),
        ("Meditation Tea", "Mindful tea drinking", 60, 40.00),
    ]
    
    all_services = thermal_baths + massages + tea_therapies
    
    services = list(existing_services)  # Start with existing
    created = 0
    
    for name, desc, duration, price in all_services:
        if name in existing_names:
            continue  # Skip if already exists
        
        if len(services) >= count:
            break
        
        if len(services) < 6:
            service_type = Service.THERMAL_BATH
        elif len(services) < 12:
            service_type = Service.MASSAGE
        else:
            service_type = Service.TEA_THERAPY
        
        service = Service(
            name=name,
            service_type=service_type,
            duration_minutes=duration,
            price=price,
            description=desc,
            max_capacity=random.choice([1, 1, 1, 2]),  # Mostly single, some couples
            is_available=random.choice([True, True, True, False])  # 75% available
        )
        if db_manager.save(service):
            services.append(service)
            created += 1
    
    print(f"✅ Total services: {len(services)} (created {created} new)")
    return services


def generate_extras(db_manager: DatabaseManagement, count: int = 18) -> list:
    """Generate test extras."""
    print(f"Generating {count} extras...")
    
    # Get existing extras
    existing_extras = db_manager.get_all(Extra)
    existing_names = {e.name for e in existing_extras}
    
    extras_data = [
        ("Lavender Aromatherapy", 10.00, "Lavender essential oils", 0, "thermal_bath,massage"),
        ("Eucalyptus Aromatherapy", 12.00, "Eucalyptus essential oils", 0, "thermal_bath,massage"),
        ("Extended 30 Minutes", 15.00, "Add 30 minutes to session", 30, "thermal_bath,massage,tea_therapy"),
        ("Extended 60 Minutes", 25.00, "Add 60 minutes to session", 60, "thermal_bath,massage,tea_therapy"),
        ("Premium Tea Selection", 8.00, "High-quality tea upgrade", 0, "tea_therapy"),
        ("Hot Stone Upgrade", 20.00, "Hot stone therapy add-on", 0, "massage"),
        ("Special Essential Oils", 15.00, "Premium essential oil blend", 0, "massage"),
        ("Bamboo Towel Set", 5.00, "Luxury bamboo towels", 0, "thermal_bath"),
        ("Herbal Bath Additive", 7.00, "Medicinal herbs for bath", 0, "thermal_bath"),
        ("Private Session", 30.00, "Exclusive private experience", 0, "thermal_bath,massage,tea_therapy"),
        ("Champagne Service", 25.00, "Celebration champagne", 0, "thermal_bath,tea_therapy"),
        ("Fruit Platter", 12.00, "Fresh fruit selection", 0, "tea_therapy"),
        ("Candlelight Setting", 8.00, "Romantic candlelit ambiance", 0, "thermal_bath,tea_therapy"),
        ("Music Therapy", 5.00, "Custom music selection", 0, "massage,tea_therapy"),
        ("Wellness Consultation", 15.00, "Personal wellness advice", 0, "tea_therapy"),
        ("Aromatherapy Blend", 18.00, "Custom essential oil blend", 0, "thermal_bath,massage"),
        ("Premium Robe", 10.00, "Luxury spa robe", 0, "thermal_bath"),
        ("Slipper Set", 5.00, "Comfortable spa slippers", 0, "thermal_bath,massage"),
    ]
    
    extras = list(existing_extras)  # Start with existing
    created = 0
    
    for name, price, desc, duration, compatible in extras_data:
        if name in existing_names:
            continue  # Skip if already exists
        
        if len(extras) >= count:
            break
        
        extra = Extra(
            name=name,
            price=price,
            description=desc,
            duration_minutes=duration,
            is_available=random.choice([True, True, True, False]),
            compatible_service_types=compatible
        )
        if db_manager.save(extra):
            extras.append(extra)
            created += 1
    
    print(f"✅ Total extras: {len(extras)} (created {created} new)")
    return extras


def generate_suppliers(db_manager: DatabaseManagement, count: int = 18) -> list:
    """Generate test suppliers."""
    print(f"Generating {count} suppliers...")
    
    supplier_data = [
        ("Mountain Spring Co.", Supplier.HOT_WATER, "spring-555-0100", "Mountain Base"),
        ("Thermal Water Supply", Supplier.HOT_WATER, "thermal-555-0200", "Hot Springs Valley"),
        ("Natural Springs Inc.", Supplier.HOT_WATER, "natural-555-0300", "Forest Springs"),
        ("Bamboo Tea Gardens", Supplier.TEA, "tea-555-1000", "Bamboo Grove"),
        ("Forest Herbal Teas", Supplier.TEA, "herbal-555-1100", "Herb Garden"),
        ("Premium Tea Importers", Supplier.TEA, "premium-555-1200", "Tea District"),
        ("Spa Essentials Co.", Supplier.SPA_SUPPLIES, "essentials-555-2000", "Supply Street"),
        ("Luxury Spa Supplies", Supplier.SPA_SUPPLIES, "luxury-555-2100", "Premium Plaza"),
        ("Natural Products Inc.", Supplier.SPA_SUPPLIES, "natural-555-2200", "Eco District"),
        ("Massage Equipment Pro", Supplier.EQUIPMENT, "equip-555-3000", "Equipment Row"),
        ("Spa Furniture Co.", Supplier.EQUIPMENT, "furniture-555-3100", "Furniture Avenue"),
        ("Wellness Equipment", Supplier.EQUIPMENT, "wellness-555-3200", "Wellness Center"),
        ("General Supplies Co.", Supplier.OTHER, "general-555-4000", "Main Street"),
        ("Forest Maintenance", Supplier.OTHER, "maintenance-555-4100", "Service District"),
        ("Utilities Plus", Supplier.OTHER, "utilities-555-4200", "Utility Center"),
        ("Water Treatment Co.", Supplier.OTHER, "water-555-4300", "Treatment Plant"),
        ("Cleaning Services", Supplier.OTHER, "cleaning-555-4400", "Service Plaza"),
        ("Security Systems", Supplier.OTHER, "security-555-4500", "Security Building"),
    ]
    
    suppliers = []
    for name, supplier_type, contact, address in supplier_data[:count]:
        supplier = Supplier(
            name=name,
            supplier_type=supplier_type,
            contact_info=contact,
            address=address,
            is_active=random.choice([True, True, True, False]),
            notes=random.choice([None, "Preferred supplier", "Bulk discount available", "New vendor"])
        )
        db_manager.save(supplier)
        suppliers.append(supplier)
    
    print(f"✅ Created {len(suppliers)} suppliers")
    return suppliers


def generate_appointments(db_manager: DatabaseManagement, customers: list, services: list, 
                          extras: list, count: int = 20) -> list:
    """Generate test appointments."""
    print(f"Generating {count} appointments...")
    
    feelings = ["stressed", "tired", "celebrating", "relaxed", "energetic", "exploring", "sore", "indulgent"]
    statuses = [Appointment.STATUS_SCHEDULED, Appointment.STATUS_COMPLETED, 
                Appointment.STATUS_CANCELLED, Appointment.STATUS_NO_SHOW]
    status_weights = [0.3, 0.5, 0.15, 0.05]  # 50% completed, 30% scheduled, etc.
    
    appointments = []
    base_date = datetime.now() - timedelta(days=60)  # Start 60 days ago
    
    for i in range(count):
        customer = random.choice(customers)
        service = random.choice(services)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Reload service to avoid detached instance errors
        reloaded_service = db_manager.get_by_id(Service, service.id)
        if not reloaded_service:
            continue  # Skip if service not found
        service = reloaded_service
        
        # Appointment date: mix of past and future
        if status == Appointment.STATUS_SCHEDULED:
            appointment_date = datetime.now() + timedelta(days=random.randint(1, 30))
        else:
            appointment_date = base_date + timedelta(days=random.randint(0, 60))
        
        # Set time to reasonable hours (9 AM - 8 PM)
        appointment_date = appointment_date.replace(
            hour=random.randint(9, 20),
            minute=random.choice([0, 15, 30, 45])
        )
        
        duration = service.duration_minutes
        price = service.price
        
        # Add some extras (30% chance)
        selected_extras = []
        if random.random() < 0.3 and extras:
            num_extras = random.randint(1, 3)
            # Reload extras to avoid detached instance errors
            extra_ids = [e.id for e in extras]
            loaded_extras = [db_manager.get_by_id(Extra, eid) for eid in extra_ids]
            compatible_extras = [e for e in loaded_extras if e and e.is_compatible_with(service.service_type)]
            if compatible_extras:
                selected_extras = random.sample(compatible_extras, min(num_extras, len(compatible_extras)))
                for extra in selected_extras:
                    price += extra.price
                    duration += extra.duration_minutes
        
        feeling = random.choice(feelings) if random.random() < 0.7 else None
        
        appointment = Appointment(
            customer_id=customer.id,
            service_id=service.id,
            appointment_datetime=appointment_date,
            duration_minutes=duration,
            price_paid=price,
            status=status,
            customer_feeling=feeling,
            notes=random.choice([
                None,
                "First visit",
                "Regular customer",
                "Special occasion",
                "Gift voucher",
                "Follow-up appointment"
            ])
        )
        
        db_manager.save(appointment)
        appointment_id = appointment.id
        
        # Add extras to appointment (many-to-many) using session context
        if selected_extras:
            def add_extras(session):
                appointment_obj = session.get(Appointment, appointment_id)
                if appointment_obj:
                    appointment_obj.extras = selected_extras
                    session.commit()
            
            db_manager.execute_query(add_extras)
        
        # Update status timestamps
        if status == Appointment.STATUS_COMPLETED:
            appointment.completed_at = appointment_date + timedelta(minutes=duration)
            db_manager.save(appointment)
        elif status == Appointment.STATUS_CANCELLED:
            appointment.cancelled_at = appointment_date - timedelta(days=random.randint(1, 7))
            appointment.cancellation_reason = random.choice([
                "Customer request",
                "Illness",
                "Weather",
                "Schedule conflict",
                "Emergency"
            ])
            db_manager.save(appointment)
        
        appointments.append(appointment)
    
    print(f"✅ Created {len(appointments)} appointments")
    return appointments


def generate_financial_records(db_manager: DatabaseManagement, appointments: list, 
                                suppliers: list, count: int = 25) -> list:
    """Generate test financial records."""
    print(f"Generating {count} financial records...")
    
    # Revenue from completed appointments - use IDs to avoid detached instance errors
    appointment_ids = [a.id for a in appointments]
    completed_appointment_ids = []
    for appt_id in appointment_ids:
        appt = db_manager.get_by_id(Appointment, appt_id)
        if appt and appt.status == Appointment.STATUS_COMPLETED:
            completed_appointment_ids.append(appt_id)
    
    financial_records = []
    
    for appt_id in completed_appointment_ids[:15]:
        appointment = db_manager.get_by_id(Appointment, appt_id)
        if not appointment:
            continue
        
        # Get service separately to avoid lazy loading
        service = db_manager.get_by_id(Service, appointment.service_id)
        service_name = service.name if service else f"Service ID:{appointment.service_id}"
        
        record = FinancialRecord(
            transaction_type=FinancialRecord.REVENUE,
            amount=appointment.price_paid,
            description=f"Service: {service_name}",
            category=FinancialRecord.CATEGORY_SERVICE_REVENUE,
            appointment_id=appointment.id,
            transaction_date=appointment.completed_at or appointment.appointment_datetime,
            receipt_number=f"R-{appointment.id:04d}-{random.randint(1000, 9999)}"
        )
        db_manager.save(record)
        financial_records.append(record)
    
    # Expenses
    expense_categories = [
        FinancialRecord.CATEGORY_HOT_WATER,
        FinancialRecord.CATEGORY_TEA,
        FinancialRecord.CATEGORY_SUPPLIES,
        FinancialRecord.CATEGORY_EQUIPMENT,
        FinancialRecord.CATEGORY_MAINTENANCE,
        FinancialRecord.CATEGORY_OTHER
    ]
    
    expense_descriptions = {
        FinancialRecord.CATEGORY_HOT_WATER: ["Hot water supply", "Thermal water delivery", "Spring water"],
        FinancialRecord.CATEGORY_TEA: ["Tea leaves purchase", "Premium tea import", "Herbal tea supply"],
        FinancialRecord.CATEGORY_SUPPLIES: ["Towels", "Essential oils", "Spa products", "Cleaning supplies"],
        FinancialRecord.CATEGORY_EQUIPMENT: ["Massage table", "Spa equipment", "Maintenance tools"],
        FinancialRecord.CATEGORY_MAINTENANCE: ["Pool cleaning", "Equipment repair", "Facility maintenance"],
        FinancialRecord.CATEGORY_OTHER: ["Utilities", "Insurance", "Licenses", "Marketing"]
    }
    
    # Get supplier IDs to avoid detached instance errors
    supplier_ids = [s.id for s in suppliers]
    
    for i in range(count - len(financial_records)):
        category = random.choice(expense_categories)
        
        # Find compatible suppliers by reloading them
        compatible_suppliers = []
        for sid in supplier_ids:
            supplier = db_manager.get_by_id(Supplier, sid)
            if supplier and (supplier.supplier_type in category or category == FinancialRecord.CATEGORY_OTHER):
                compatible_suppliers.append(supplier)
        
        if not compatible_suppliers:
            # Fallback to any supplier
            supplier = db_manager.get_by_id(Supplier, random.choice(supplier_ids))
        else:
            supplier = random.choice(compatible_suppliers)
        
        amount = random.uniform(50.0, 500.0)
        description = random.choice(expense_descriptions[category])
        
        transaction_date = datetime.now() - timedelta(days=random.randint(0, 60))
        
        record = FinancialRecord(
            transaction_type=FinancialRecord.EXPENSE,
            amount=amount,
            description=description,
            category=category,
            supplier_id=supplier.id,
            transaction_date=transaction_date,
            receipt_number=f"E-{i+1:04d}-{random.randint(1000, 9999)}",
            notes=random.choice([None, "Monthly order", "Bulk purchase", "Urgent delivery"])
        )
        db_manager.save(record)
        financial_records.append(record)
    
    print(f"✅ Created {len(financial_records)} financial records")
    return financial_records


def generate_customer_preferences(db_manager: DatabaseManagement, customers: list, 
                                  services: list, appointments: list, count: int = 20) -> list:
    """Generate test customer preferences."""
    print(f"Generating {count} customer preferences...")
    
    # Create preferences based on appointments - use IDs to avoid detached instance errors
    appointment_ids = [a.id for a in appointments]
    preference_map = {}  # (customer_id, service_id) -> preference
    
    for appt_id in appointment_ids:
        appointment = db_manager.get_by_id(Appointment, appt_id)
        if appointment and appointment.status == Appointment.STATUS_COMPLETED:
            key = (appointment.customer_id, appointment.service_id)
            if key not in preference_map:
                preference_map[key] = {
                    'visit_count': 0,
                    'total_spent': 0.0,
                    'first_visit': appointment.appointment_datetime,
                    'last_visit': appointment.appointment_datetime
                }
            
            pref_data = preference_map[key]
            pref_data['visit_count'] += 1
            pref_data['total_spent'] += appointment.price_paid
            if appointment.appointment_datetime < pref_data['first_visit']:
                pref_data['first_visit'] = appointment.appointment_datetime
            if appointment.appointment_datetime > pref_data['last_visit']:
                pref_data['last_visit'] = appointment.appointment_datetime
    
    preferences = []
    for (customer_id, service_id), data in list(preference_map.items())[:count]:
        # Calculate preference score (0-10) based on visits and spending
        visit_score = min(data['visit_count'] * 2, 5)  # Max 5 points for visits
        spend_score = min(data['total_spent'] / 100, 5)  # Max 5 points for spending
        preference_score = visit_score + spend_score
        
        preference = CustomerPreference(
            customer_id=customer_id,
            service_id=service_id,
            preference_score=preference_score
        )
        preference.visit_count = data['visit_count']
        preference.total_spent = data['total_spent']
        preference.first_visited = data['first_visit']
        preference.last_visited = data['last_visit']
        preference.average_rating = random.uniform(4.0, 5.0) if random.random() < 0.5 else None
        
        db_manager.save(preference)
        preferences.append(preference)
    
    # Add some additional preferences for variety
    while len(preferences) < count:
        customer = random.choice(customers)
        service = random.choice(services)
        key = (customer.id, service.id)
        
        if key not in preference_map:
            preference = CustomerPreference(
                customer_id=customer.id,
                service_id=service.id,
                preference_score=random.uniform(0.0, 8.0)
            )
            preference.visit_count = random.randint(0, 5)
            preference.total_spent = random.uniform(0.0, 300.0)
            db_manager.save(preference)
            preferences.append(preference)
            preference_map[key] = True
    
    print(f"✅ Created {len(preferences)} customer preferences")
    return preferences


def generate_feeling_mappings(db_manager: DatabaseManagement, services: list, count: int = 20) -> list:
    """Generate test feeling-service mappings."""
    print(f"Generating {count} feeling-service mappings...")
    
    feelings = ["stressed", "tired", "celebrating", "relaxed", "energetic", "exploring", "sore", "indulgent"]
    
    # Create mappings based on service types
    mappings = []
    mapping_keys = set()
    
    for feeling in feelings:
        # Map each feeling to 2-3 services
        num_services = random.randint(2, 3)
        available_services = random.sample(services, min(num_services, len(services)))
        
        for priority, service in enumerate(available_services, start=1):
            key = (feeling, service.id)
            if key not in mapping_keys:
                mapping = FeelingServiceMapping(
                    feeling=feeling,
                    service_id=service.id,
                    priority=priority,
                    is_active=True
                )
                db_manager.save(mapping)
                mappings.append(mapping)
                mapping_keys.add(key)
    
    # Add more random mappings to reach count
    while len(mappings) < count:
        feeling = random.choice(feelings)
        service = random.choice(services)
        key = (feeling, service.id)
        
        if key not in mapping_keys:
            mapping = FeelingServiceMapping(
                feeling=feeling,
                service_id=service.id,
                priority=random.randint(1, 5),
                is_active=random.choice([True, True, False])
            )
            db_manager.save(mapping)
            mappings.append(mapping)
            mapping_keys.add(key)
    
    print(f"✅ Created {len(mappings)} feeling-service mappings")
    return mappings


def main():
    """Main function to generate all test data."""
    print("=" * 60)
    print("Panda Spa - Test Data Generation")
    print("=" * 60)
    
    # Initialize database
    db_manager = DatabaseManagement("panda_spa.db")
    db_manager.initialize_database()
    
    # Check if data already exists
    existing_customers = db_manager.get_all(Customer)
    if existing_customers:
        print(f"⚠️  Found {len(existing_customers)} existing customers in database")
        print("   Script will add new records where needed (skipping duplicates)")
        print()
    
    try:
        # Generate data in order (respecting dependencies)
        customers = generate_customers(db_manager, count=20)
        services = generate_services(db_manager, count=18)
        extras = generate_extras(db_manager, count=18)
        suppliers = generate_suppliers(db_manager, count=18)
        appointments = generate_appointments(db_manager, customers, services, extras, count=25)
        financial_records = generate_financial_records(db_manager, appointments, suppliers, count=25)
        preferences = generate_customer_preferences(db_manager, customers, services, appointments, count=20)
        feeling_mappings = generate_feeling_mappings(db_manager, services, count=20)
        
        # Update customer statistics
        print("\nUpdating customer statistics...")
        appointment_ids = [a.id for a in appointments]
        for customer in customers:
            # Reload customer to avoid detached instance errors
            customer = db_manager.get_by_id(Customer, customer.id)
            if not customer:
                continue
            
            # Get appointments for this customer
            customer_appointments = []
            for appt_id in appointment_ids:
                appt = db_manager.get_by_id(Appointment, appt_id)
                if appt and appt.customer_id == customer.id:
                    customer_appointments.append(appt)
            
            customer.total_visits = len([a for a in customer_appointments if a.status == Appointment.STATUS_COMPLETED])
            customer.total_spent = sum(a.price_paid for a in customer_appointments if a.status == Appointment.STATUS_COMPLETED)
            if customer_appointments:
                customer.last_visit = max(a.appointment_datetime for a in customer_appointments)
            db_manager.save(customer)
        
        print("\n" + "=" * 60)
        print("✅ Test data generation complete!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   - Customers: {len(customers)}")
        print(f"   - Services: {len(services)}")
        print(f"   - Extras: {len(extras)}")
        print(f"   - Suppliers: {len(suppliers)}")
        print(f"   - Appointments: {len(appointments)}")
        print(f"   - Financial Records: {len(financial_records)}")
        print(f"   - Customer Preferences: {len(preferences)}")
        print(f"   - Feeling Mappings: {len(feeling_mappings)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error generating test data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.close()


if __name__ == "__main__":
    main()

