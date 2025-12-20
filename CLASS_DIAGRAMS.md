# Panda Spa - Class Diagrams

## Core Models

```
┌─────────────────────────────────┐
│         Customer                │
├─────────────────────────────────┤
│ + id: int                       │
│ + name: str                     │
│ + species: str                  │
│ + contact_info: str             │
│ + created_at: datetime          │
│ + preferences: List[Preference] │
│ + appointments: List[Appointment]│
├─────────────────────────────────┤
│ + __init__()                    │
│ + to_dict()                     │
└─────────────────────────────────┘
            │
            │ 1
            │
            │ *
┌─────────────────────────────────┐
│      CustomerPreference         │
├─────────────────────────────────┤
│ + id: int                       │
│ + customer_id: int (FK)         │
│ + service_id: int (FK)          │
│ + preference_score: float      │
│ + visit_count: int              │
│ + last_visited: datetime        │
│ + notes: str                    │
├─────────────────────────────────┤
│ + __init__()                    │
│ + update_preference()           │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│         Service                 │
├─────────────────────────────────┤
│ + id: int                       │
│ + name: str                     │
│ + service_type: str             │
│ + description: str              │
│ + duration_minutes: int         │
│ + price: float                  │
│ + is_available: bool            │
│ + appointments: List[Appointment]│
├─────────────────────────────────┤
│ + __init__()                    │
│ + to_dict()                     │
└─────────────────────────────────┘
            │
            │ 1
            │
            │ *
┌─────────────────────────────────┐
│        Appointment              │
├─────────────────────────────────┤
│ + id: int                       │
│ + customer_id: int (FK)         │
│ + service_id: int (FK)          │
│ + appointment_datetime: datetime│
│ + status: str                   │
│ + notes: str                    │
│ + created_at: datetime          │
│ + customer: Customer            │
│ + service: Service              │
├─────────────────────────────────┤
│ + __init__()                    │
│ + cancel()                      │
│ + complete()                    │
│ + to_dict()                     │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│      FinancialRecord            │
├─────────────────────────────────┤
│ + id: int                       │
│ + transaction_type: str         │
│ + amount: float                 │
│ + description: str              │
│ + supplier_id: int (FK, nullable)│
│ + appointment_id: int (FK, nullable)│
│ + transaction_date: datetime   │
│ + category: str                 │
│ + supplier: Supplier            │
│ + appointment: Appointment      │
├─────────────────────────────────┤
│ + __init__()                    │
│ + to_dict()                     │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│         Supplier                │
├─────────────────────────────────┤
│ + id: int                       │
│ + name: str                     │
│ + supplier_type: str            │
│ + contact_info: str             │
│ + financial_records: List[FinancialRecord]│
├─────────────────────────────────┤
│ + __init__()                    │
│ + to_dict()                     │
└─────────────────────────────────┘
```

## Database Layer

```
┌─────────────────────────────────┐
│    DatabaseManagement           │
├─────────────────────────────────┤
│ - engine: Engine                │
│ - session_factory: sessionmaker │
│ - base: declarative_base        │
├─────────────────────────────────┤
│ + initialize_database()         │
│ + create_tables()               │
│ + get_session()                 │
│ + close()                       │
│ + execute_query()               │
│ + execute_transaction()         │
└─────────────────────────────────┘
            │
            │ uses
            │
┌─────────────────────────────────┐
│        UnitOfWork                │
├─────────────────────────────────┤
│ - session: Session              │
│ - db_manager: DatabaseManagement│
│ - customers: Repository         │
│ - services: Repository          │
│ - appointments: Repository      │
│ - financial_records: Repository │
│ - suppliers: Repository         │
│ - preferences: Repository      │
├─────────────────────────────────┤
│ + __enter__()                   │
│ + __exit__()                    │
│ + commit()                      │
│ + rollback()                    │
│ + get_customer_repo()           │
│ + get_service_repo()            │
│ + get_appointment_repo()        │
│ + get_financial_repo()          │
│ + get_supplier_repo()           │
│ + get_preference_repo()          │
└─────────────────────────────────┘
```

## GUI Layer

```
┌─────────────────────────────────┐
│      MainWindow                 │
├─────────────────────────────────┤
│ - db_manager: DatabaseManagement│
│ - unit_of_work: UnitOfWork      │
│ - menu_bar: MenuBar             │
│ - status_bar: StatusBar          │
├─────────────────────────────────┤
│ + __init__()                    │
│ + setup_menu()                  │
│ + show_appointments()           │
│ + show_services()               │
│ + show_financials()             │
│ + show_recommendations()        │
│ + run()                         │
└─────────────────────────────────┘
            │
            │ creates
            │
    ┌───────┴───────┬───────────────┬───────────────┐
    │               │               │               │
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│Appointment│ │  Service  │ │ Financial │ │Recommend- │
│  Window   │ │  Window   │ │  Window   │ │  ation    │
│           │ │           │ │           │ │  Window   │
└───────────┘ └───────────┘ └───────────┘ └───────────┘
```

## Service Layer (Business Logic)

```
┌─────────────────────────────────┐
│   RecommendationService          │
├─────────────────────────────────┤
│ - unit_of_work: UnitOfWork      │
├─────────────────────────────────┤
│ + get_recommendations(customer_id)│
│ + update_preferences(appointment)│
│ + calculate_preference_score()  │
│ + get_popular_services()        │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│    AppointmentService            │
├─────────────────────────────────┤
│ - unit_of_work: UnitOfWork      │
├─────────────────────────────────┤
│ + create_appointment()          │
│ + cancel_appointment()           │
│ + get_available_slots()         │
│ + check_conflicts()              │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│      FinancialService            │
├─────────────────────────────────┤
│ - unit_of_work: UnitOfWork      │
├─────────────────────────────────┤
│ + calculate_profit()            │
│ + calculate_expenses()          │
│ + get_net_income()              │
│ + get_category_breakdown()      │
└─────────────────────────────────┘
```


