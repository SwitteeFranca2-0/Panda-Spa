# Panda Spa - Agile Vertical Layer Implementation Plan

## Implementation Philosophy
**Vertical Slices**: Each feature is implemented completely across all layers (Database → Models → Business Logic → GUI) and tested before moving to the next feature.

---

## Phase 0: Foundation Setup
**Goal**: Establish database infrastructure and verify it works

### Step 0.1: Database Infrastructure
- [ ] Create `database/` folder structure
- [ ] Create `database/base.py` - SQLAlchemy declarative base
- [ ] Create `database/db_manager.py` - DatabaseManagement class
  - [ ] Implement `__init__()` with SQLite connection
  - [ ] Implement `initialize_database()`
  - [ ] Implement `get_session()`
  - [ ] Implement `close()`
- [ ] Create `database/__init__.py`
- [ ] Create `requirements.txt` with SQLAlchemy dependency

### Step 0.2: Database Tests
- [ ] Create `tests/` folder
- [ ] Create `tests/test_database.py`
  - [ ] Test database initialization
  - [ ] Test session creation
  - [ ] Test connection closing
  - [ ] Test database file creation
- [ ] Run tests: `python -m pytest tests/test_database.py -v`

**Acceptance Criteria**: Database connects, sessions work, tests pass

---

## Phase 1: Customer Management (Vertical Slice 1)
**Goal**: Complete CRUD for customers across all layers

### Step 1.1: Customer Model
- [ ] Create `models/` folder
- [ ] Create `models/customer.py` - Customer model class
  - [ ] Define all fields (id, name, species, contact_info, etc.)
  - [ ] Define relationships
  - [ ] Add `to_dict()` method
- [ ] Create `models/__init__.py`
- [ ] Update `database/base.py` to include Customer in imports

### Step 1.2: Database - Customer Operations
- [ ] Update `database/db_manager.py` to create Customer table
- [ ] Create `database/unit_of_work.py` - UnitOfWork class
  - [ ] Implement context manager (`__enter__`, `__exit__`)
  - [ ] Implement `get_customer_repo()` method
- [ ] Create `database/repositories/customer_repository.py`
  - [ ] `add(customer)` - Create
  - [ ] `get_by_id(id)` - Read
  - [ ] `get_all()` - Read all
  - [ ] `update(customer)` - Update
  - [ ] `delete(customer)` - Delete
  - [ ] `get_by_name(name)` - Search
  - [ ] `get_by_species(species)` - Filter

### Step 1.3: Customer Tests
- [ ] Create `tests/test_customer.py`
  - [ ] Test customer creation
  - [ ] Test customer retrieval
  - [ ] Test customer update
  - [ ] Test customer deletion
  - [ ] Test search/filter operations
- [ ] Run tests: `python -m pytest tests/test_customer.py -v`

### Step 1.4: GUI - Customer Management
- [ ] Create `gui/` folder
- [ ] Create `gui/customer_window.py` - CustomerWindow class
  - [ ] Form for creating new customer
  - [ ] List/table showing all customers
  - [ ] Edit customer functionality
  - [ ] Delete customer functionality
  - [ ] Search/filter by name/species
- [ ] Create `gui/__init__.py`
- [ ] Test GUI manually: Create, Read, Update, Delete customers

**Acceptance Criteria**: 
- ✅ Can create customer via GUI
- ✅ Can view all customers
- ✅ Can edit customer details
- ✅ Can delete customer
- ✅ All operations persist to database
- ✅ All tests pass

---

## Phase 2: Service Management (Vertical Slice 2)
**Goal**: Complete CRUD for services across all layers

### Step 2.1: Service Model
- [ ] Create `models/service.py` - Service model class
  - [ ] Define all fields (id, name, service_type, price, etc.)
  - [ ] Define relationships
  - [ ] Add `to_dict()` method
  - [ ] Add validation for service_type enum

### Step 2.2: Database - Service Operations
- [ ] Update `database/db_manager.py` to create Service table
- [ ] Update `database/unit_of_work.py`
  - [ ] Implement `get_service_repo()` method
- [ ] Create `database/repositories/service_repository.py`
  - [ ] `add(service)` - Create
  - [ ] `get_by_id(id)` - Read
  - [ ] `get_all()` - Read all
  - [ ] `get_by_type(service_type)` - Filter by type
  - [ ] `update(service)` - Update
  - [ ] `delete(service)` - Delete
  - [ ] `get_available()` - Get only available services

### Step 2.3: Service Tests
- [ ] Create `tests/test_service.py`
  - [ ] Test service creation
  - [ ] Test service retrieval
  - [ ] Test service filtering by type
  - [ ] Test service update
  - [ ] Test service deletion
- [ ] Run tests: `python -m pytest tests/test_service.py -v`

### Step 2.4: GUI - Service Management
- [ ] Create `gui/service_window.py` - ServiceWindow class
  - [ ] Form for creating new service
  - [ ] List/table showing all services
  - [ ] Filter by service type (thermal_bath, massage, tea_therapy)
  - [ ] Edit service functionality
  - [ ] Toggle service availability
  - [ ] Delete service functionality
- [ ] Test GUI manually: Create, Read, Update, Delete services

**Acceptance Criteria**:
- ✅ Can create service via GUI
- ✅ Can view all services with filtering
- ✅ Can edit service details
- ✅ Can toggle availability
- ✅ Can delete service
- ✅ All operations persist to database
- ✅ All tests pass

---

## Phase 3: Appointment Management (Vertical Slice 3)
**Goal**: Complete CRUD for appointments with scheduling logic

### Step 3.1: Appointment Model
- [ ] Create `models/appointment.py` - Appointment model class
  - [ ] Define all fields (id, customer_id, service_id, datetime, status, etc.)
  - [ ] Define foreign key relationships
  - [ ] Add `to_dict()` method
  - [ ] Add status validation

### Step 3.2: Database - Appointment Operations
- [ ] Update `database/db_manager.py` to create Appointment table
- [ ] Update `database/unit_of_work.py`
  - [ ] Implement `get_appointment_repo()` method
- [ ] Create `database/repositories/appointment_repository.py`
  - [ ] `add(appointment)` - Create
  - [ ] `get_by_id(id)` - Read
  - [ ] `get_all()` - Read all
  - [ ] `get_by_customer(customer_id)` - Filter by customer
  - [ ] `get_by_service(service_id)` - Filter by service
  - [ ] `get_by_date_range(start_date, end_date)` - Filter by date
  - [ ] `get_by_status(status)` - Filter by status
  - [ ] `check_conflict(datetime, duration)` - Check scheduling conflicts
  - [ ] `update(appointment)` - Update
  - [ ] `delete(appointment)` - Delete

### Step 3.3: Business Logic - Appointment Service
- [ ] Create `services/` folder
- [ ] Create `services/appointment_service.py` - AppointmentService class
  - [ ] `create_appointment(customer_id, service_id, datetime)` - With conflict checking
  - [ ] `cancel_appointment(appointment_id, reason)` - Cancel with reason
  - [ ] `complete_appointment(appointment_id)` - Mark as completed
  - [ ] `get_available_slots(service_id, date)` - Get available time slots
  - [ ] `reschedule_appointment(appointment_id, new_datetime)` - Reschedule

### Step 3.4: Appointment Tests
- [ ] Create `tests/test_appointment.py`
  - [ ] Test appointment creation
  - [ ] Test conflict detection
  - [ ] Test appointment cancellation
  - [ ] Test appointment completion
  - [ ] Test date range queries
  - [ ] Test available slots calculation
- [ ] Run tests: `python -m pytest tests/test_appointment.py -v`

### Step 3.5: GUI - Appointment Management
- [ ] Create `gui/appointment_window.py` - AppointmentWindow class
  - [ ] Form for creating new appointment
    - [ ] Customer dropdown (from database)
    - [ ] Service dropdown (filtered by availability)
    - [ ] Date/time picker
    - [ ] Conflict warning display
  - [ ] Calendar view showing appointments
  - [ ] List view with filters (date, customer, service, status)
  - [ ] Edit appointment functionality
  - [ ] Cancel appointment with reason
  - [ ] Complete appointment button
  - [ ] Reschedule functionality
- [ ] Test GUI manually: Create, view, edit, cancel, complete appointments

**Acceptance Criteria**:
- ✅ Can create appointment via GUI
- ✅ Conflict detection works
- ✅ Can view appointments in calendar/list
- ✅ Can cancel appointments with reason
- ✅ Can complete appointments
- ✅ Can reschedule appointments
- ✅ All operations persist to database
- ✅ All tests pass

---

## Phase 4: Financial Tracking (Vertical Slice 4)
**Goal**: Track revenue and expenses with financial records

### Step 4.1: Financial & Supplier Models
- [ ] Create `models/financial_record.py` - FinancialRecord model
  - [ ] Define all fields (id, transaction_type, amount, category, etc.)
  - [ ] Define relationships
  - [ ] Add `to_dict()` method
- [ ] Create `models/supplier.py` - Supplier model
  - [ ] Define all fields (id, name, supplier_type, etc.)
  - [ ] Define relationships
  - [ ] Add `to_dict()` method

### Step 4.2: Database - Financial Operations
- [ ] Update `database/db_manager.py` to create FinancialRecord and Supplier tables
- [ ] Update `database/unit_of_work.py`
  - [ ] Implement `get_financial_repo()` method
  - [ ] Implement `get_supplier_repo()` method
- [ ] Create `database/repositories/financial_repository.py`
  - [ ] `add(record)` - Create
  - [ ] `get_by_id(id)` - Read
  - [ ] `get_all()` - Read all
  - [ ] `get_revenue(start_date, end_date)` - Get revenue records
  - [ ] `get_expenses(start_date, end_date)` - Get expense records
  - [ ] `get_by_category(category)` - Filter by category
  - [ ] `get_by_date_range(start_date, end_date)` - Filter by date
- [ ] Create `database/repositories/supplier_repository.py`
  - [ ] `add(supplier)` - Create
  - [ ] `get_by_id(id)` - Read
  - [ ] `get_all()` - Read all
  - [ ] `get_by_type(supplier_type)` - Filter by type

### Step 4.3: Business Logic - Financial Service
- [ ] Create `services/financial_service.py` - FinancialService class
  - [ ] `record_revenue(appointment_id, amount)` - Auto-create revenue from appointment
  - [ ] `record_expense(amount, category, supplier_id, description)` - Record expense
  - [ ] `calculate_profit(start_date, end_date)` - Calculate net profit
  - [ ] `calculate_revenue(start_date, end_date)` - Calculate total revenue
  - [ ] `calculate_expenses(start_date, end_date)` - Calculate total expenses
  - [ ] `get_category_breakdown(start_date, end_date)` - Expenses by category
  - [ ] `get_financial_summary(start_date, end_date)` - Complete summary

### Step 4.4: Financial Tests
- [ ] Create `tests/test_financial.py`
  - [ ] Test revenue recording
  - [ ] Test expense recording
  - [ ] Test profit calculation
  - [ ] Test category breakdown
  - [ ] Test date range queries
- [ ] Run tests: `python -m pytest tests/test_financial.py -v`

### Step 4.5: GUI - Financial Management
- [ ] Create `gui/financial_window.py` - FinancialWindow class
  - [ ] Dashboard showing:
    - [ ] Total revenue (current period)
    - [ ] Total expenses (current period)
    - [ ] Net profit (current period)
    - [ ] Expense breakdown by category (chart/table)
  - [ ] Form for recording expenses
    - [ ] Amount input
    - [ ] Category dropdown
    - [ ] Supplier dropdown
    - [ ] Description field
  - [ ] Financial records table with filters
    - [ ] Filter by date range
    - [ ] Filter by type (revenue/expense)
    - [ ] Filter by category
  - [ ] Export financial report (optional)
- [ ] Test GUI manually: Record expenses, view financial dashboard

**Acceptance Criteria**:
- ✅ Can record expenses via GUI
- ✅ Revenue auto-recorded when appointment completed
- ✅ Financial dashboard shows accurate calculations
- ✅ Can filter financial records
- ✅ Category breakdown works
- ✅ All operations persist to database
- ✅ All tests pass

---

## Phase 5: Customer Preferences & Recommendations (Vertical Slice 5)
**Goal**: Track preferences and provide service recommendations

### Step 5.1: Preference Model
- [ ] Create `models/customer_preference.py` - CustomerPreference model
  - [ ] Define all fields (id, customer_id, service_id, preference_score, etc.)
  - [ ] Define relationships
  - [ ] Add `to_dict()` method
- [ ] Create `models/service_recommendation.py` - ServiceRecommendation model (optional)
  - [ ] Define all fields
  - [ ] Define relationships

### Step 5.2: Database - Preference Operations
- [ ] Update `database/db_manager.py` to create CustomerPreference table
- [ ] Update `database/unit_of_work.py`
  - [ ] Implement `get_preference_repo()` method
- [ ] Create `database/repositories/preference_repository.py`
  - [ ] `add(preference)` - Create
  - [ ] `get_by_customer(customer_id)` - Get all preferences for customer
  - [ ] `get_by_customer_and_service(customer_id, service_id)` - Get specific preference
  - [ ] `update_preference(customer_id, service_id, score)` - Update preference score
  - [ ] `get_top_preferences(customer_id, limit)` - Get top N preferred services

### Step 5.3: Business Logic - Recommendation Service
- [ ] Create `services/recommendation_service.py` - RecommendationService class
  - [ ] `update_preferences_from_appointment(appointment)` - Update after appointment
  - [ ] `calculate_preference_score(customer_id, service_id)` - Calculate score
  - [ ] `get_recommendations(customer_id, limit=3)` - Get top recommendations
  - [ ] `get_recommendation_reason(customer_id, service_id)` - Why recommended
  - [ ] `get_popular_services(limit=5)` - Most popular services overall
  - [ ] `get_complementary_services(service_id)` - Services that go well together

### Step 5.4: Preference Tests
- [ ] Create `tests/test_preferences.py`
  - [ ] Test preference creation
  - [ ] Test preference score calculation
  - [ ] Test recommendation generation
  - [ ] Test preference updates after appointment
- [ ] Run tests: `python -m pytest tests/test_preferences.py -v`

### Step 5.5: GUI - Recommendations
- [ ] Create `gui/recommendation_window.py` - RecommendationWindow class
  - [ ] Customer selection dropdown
  - [ ] Display personalized recommendations
    - [ ] Service name
    - [ ] Recommendation score
    - [ ] Reason for recommendation
  - [ ] "Book Recommended Service" button (links to appointment window)
  - [ ] Show customer's booking history
  - [ ] Show popular services overall
- [ ] Integrate recommendations into appointment creation window
  - [ ] Show recommendations when customer selected
  - [ ] Quick-book from recommendations
- [ ] Test GUI manually: View recommendations, book from recommendations

**Acceptance Criteria**:
- ✅ Preferences update automatically after appointments
- ✅ Recommendations shown in GUI
- ✅ Recommendation reasons are meaningful
- ✅ Can book directly from recommendations
- ✅ Preference scores calculate correctly
- ✅ All operations persist to database
- ✅ All tests pass

---

## Phase 6: Main Application & Integration (Vertical Slice 6)
**Goal**: Integrate all features into main application

### Step 6.1: Main Window
- [ ] Create `gui/main_window.py` - MainWindow class
  - [ ] Menu bar with navigation
    - [ ] Customers
    - [ ] Services
    - [ ] Appointments
    - [ ] Financials
    - [ ] Recommendations
  - [ ] Status bar showing current user/status
  - [ ] Dashboard/home view (optional)
    - [ ] Today's appointments
    - [ ] Recent revenue
    - [ ] Quick stats

### Step 6.2: Application Entry Point
- [ ] Create `app.py` - Main application file
  - [ ] Initialize database manager
  - [ ] Create database tables if needed
  - [ ] Initialize main window
  - [ ] Start Tkinter main loop
  - [ ] Handle application shutdown (close database)

### Step 6.3: Integration Tests
- [ ] Create `tests/test_integration.py`
  - [ ] Test complete workflow: Create customer → Create service → Book appointment → Complete → Check financials
  - [ ] Test recommendation workflow: Multiple appointments → Check recommendations
  - [ ] Test data persistence across application restarts
- [ ] Run all tests: `python -m pytest tests/ -v`

### Step 6.4: Error Handling & Validation
- [ ] Add input validation to all GUI forms
- [ ] Add error handling for database operations
- [ ] Add user-friendly error messages
- [ ] Add confirmation dialogs for destructive operations

### Step 6.5: Polish & Documentation
- [ ] Create `models.py` - Central import file
  - [ ] Import all models from `models/` folder
- [ ] Add docstrings to all classes and methods
- [ ] Create `README.md` with setup instructions
- [ ] Test complete application end-to-end

**Acceptance Criteria**:
- ✅ Application starts successfully
- ✅ All features accessible from main window
- ✅ All workflows function correctly
- ✅ Error handling works
- ✅ Data persists correctly
- ✅ All tests pass
- ✅ Application is ready for stakeholder presentation

---

## Testing Strategy

### Unit Tests
- Each model class
- Each repository method
- Each service method

### Integration Tests
- Complete workflows
- Cross-feature interactions
- Database persistence

### Manual GUI Tests
- User workflows
- Form validation
- Error messages
- Navigation

### Test Execution
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_customer.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

---

## Implementation Order Summary

1. **Phase 0**: Database foundation ✅
2. **Phase 1**: Customer Management ✅
3. **Phase 2**: Service Management ✅
4. **Phase 3**: Appointment Management ✅
5. **Phase 4**: Financial Tracking ✅
6. **Phase 5**: Preferences & Recommendations ✅
7. **Phase 6**: Main App & Integration ✅

Each phase is **complete and tested** before moving to the next!


