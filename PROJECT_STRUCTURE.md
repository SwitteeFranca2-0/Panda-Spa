# Panda Spa - Project Structure

## Folder Tree

```
AAT/
├── models/
│   ├── __init__.py
│   ├── customer.py              # Customer model (forest animals)
│   ├── service.py                # Service model (thermal bath, massage, tea therapy)
│   ├── appointment.py            # Appointment model (bookings)
│   ├── financial_record.py      # Financial transactions (profits/expenses)
│   ├── supplier.py               # Supplier model (hot water, tea, spa suppliers)
│   ├── customer_preference.py    # Customer preference tracking
│   └── service_recommendation.py # Recommendation engine data
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py             # DatabaseManagement class
│   ├── unit_of_work.py           # UnitOfWork pattern
│   └── base.py                   # Base model class (SQLAlchemy declarative base)
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py            # Main application window
│   ├── appointment_window.py     # Appointment booking/management
│   ├── service_window.py          # Service management
│   ├── customer_window.py         # Customer management
│   ├── financial_window.py       # Financial tracking dashboard
│   ├── recommendation_window.py  # Customer recommendations
│   └── widgets/                  # Reusable GUI components
│       ├── __init__.py
│       ├── calendar_widget.py
│       └── service_card.py
│
├── services/                     # Business logic layer
│   ├── __init__.py
│   ├── appointment_service.py    # Appointment business logic
│   ├── recommendation_service.py # Recommendation engine
│   └── financial_service.py      # Financial calculations
│
├── models.py                     # Central import file for all models
├── app.py                        # Application entry point
├── requirements.txt              # Dependencies
└── README.md                     # Project documentation
```


