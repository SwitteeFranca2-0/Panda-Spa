# 🐼 Panda Spa - Thermal Water Wellness Center

A Python-based desktop application for managing a luxurious thermal water spa in the bamboo forest. Built with Tkinter GUI and SQLAlchemy ORM.

## Features

### ✅ Customer Management
- Create, read, update, and delete customer records
- Track customer information (name, species, contact info)
- View customer statistics (total visits, total spent)
- Search and filter customers by name and species

### ✅ Service Management
- Manage spa services (thermal baths, massages, tea therapy)
- Set service pricing, duration, and capacity
- Toggle service availability
- Filter services by type

### ✅ Appointment Management
- Schedule appointments with conflict detection
- View appointments in calendar/list format
- Complete, cancel, and reschedule appointments
- Automatic customer statistics updates
- Real-time conflict warnings

### ✅ Financial Tracking
- Automatic revenue recording from completed appointments
- Manual expense tracking with supplier management
- Financial dashboard with revenue, expenses, and profit
- Category breakdown for expenses
- Date range filtering for financial reports

## Project Structure

```
AAT/
├── app.py                      # Application entry point
├── models.py                   # Central model imports
├── models/                     # Model classes
│   ├── customer.py
│   ├── service.py
│   ├── appointment.py
│   ├── supplier.py
│   └── financial_record.py
├── database/                   # Database management
│   ├── base.py                # SQLAlchemy base
│   └── db_manager.py          # DatabaseManagement class
├── services/                   # Business logic
│   ├── appointment_service.py
│   └── financial_service.py
├── gui/                        # Tkinter GUI windows
│   ├── main_window.py         # Main application window
│   ├── customer_window.py
│   ├── service_window.py
│   ├── appointment_window.py
│   └── financial_window.py
└── tests/                      # Test suite
    ├── test_database.py
    ├── test_customer.py
    ├── test_service.py
    ├── test_appointment.py
    ├── test_financial.py
    └── test_integration.py
```

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd /home/rgtech006/Desktop/Personal/AAT
   ```

2. **Activate virtual environment**
   ```bash
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python app.py
```

The main window will open with:
- **Navigation menu** on the left with buttons for all management windows
- **Dashboard** on the right showing:
  - Total customers
  - Active services
  - Today's appointments
  - Today's revenue
  - List of today's appointments

### Key Functions

#### Customer Management
- Click "👥 Manage Customers" to:
  - Add new forest animal customers
  - View all customers
  - Edit customer information
  - Delete customers
  - Search/filter customers

#### Service Management
- Click "💆 Manage Services" to:
  - Add new services (thermal baths, massages, tea therapy)
  - Set pricing and duration
  - Toggle service availability
  - Edit or delete services

#### Appointment Management
- Click "📅 Manage Appointments" to:
  - Book new appointments
  - View all appointments with filters
  - Complete appointments (auto-records revenue)
  - Cancel appointments
  - Reschedule appointments
  - Real-time conflict detection

#### Financial Management
- Click "💰 Financial Management" to:
  - View financial dashboard (revenue, expenses, profit)
  - Record expenses manually
  - View expense breakdown by category
  - Filter financial records by type and category
  - Set date ranges for financial reports

## Database

The application uses SQLite database (`panda_spa.db`) which is automatically created on first run. All data persists between sessions.

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test suite:
```bash
pytest tests/test_customer.py -v
pytest tests/test_appointment.py -v
```

## Technology Stack

- **Python 3.10+**
- **SQLAlchemy 2.0+** - ORM for database management
- **Tkinter** - GUI framework (included with Python)
- **pytest** - Testing framework

## Data Models

### Customer
- Tracks forest animals visiting the spa
- Fields: name, species, contact_info, total_visits, total_spent, etc.

### Service
- Spa services offered (thermal baths, massages, tea therapy)
- Fields: name, service_type, price, duration_minutes, is_available, etc.

### Appointment
- Customer bookings for services
- Fields: customer_id, service_id, appointment_datetime, status, etc.
- Statuses: scheduled, completed, cancelled, no_show

### Supplier
- Vendors for spa expenses
- Fields: name, supplier_type, contact_info, etc.

### FinancialRecord
- Revenue and expense transactions
- Fields: transaction_type, amount, category, supplier_id, appointment_id, etc.

## Key Features

### Automatic Revenue Tracking
When an appointment is completed, revenue is automatically recorded in the financial system.

### Conflict Detection
The appointment system prevents double-booking by detecting scheduling conflicts.

### Customer Statistics
Customer visit counts and spending are automatically updated when appointments are completed.

### Financial Dashboard
Real-time financial overview with revenue, expenses, profit, and category breakdowns.

## Development

### Adding New Features

1. Create model in `models/` folder
2. Update `models/__init__.py` and `models.py`
3. Update `database/db_manager.py` to import new model
4. Create service in `services/` if business logic needed
5. Create GUI window in `gui/` folder
6. Add tests in `tests/` folder
7. Update main window navigation

### Database Management

All database operations go through `DatabaseManagement` class:
- `save(obj)` - Save object
- `create(model_class, **kwargs)` - Create and save
- `update(obj, **kwargs)` - Update object
- `delete(obj)` - Delete object
- `get_by_id(model_class, id)` - Get by ID
- `get_all(model_class)` - Get all
- `find(model_class, **filters)` - Find with filters

## License

This project is part of an educational assignment.

## Author

Panda Spa Management System - Built for managing a thermal water wellness center in the bamboo forest.





