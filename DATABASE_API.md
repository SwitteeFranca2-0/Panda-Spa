# Database Management API & UnitOfWork Methods

## DatabaseManagement Class API

### Initialization & Setup
```python
class DatabaseManagement:
    """
    Centralized database management class responsible for all SQLite interactions.
    Uses SQLAlchemy ORM for database operations.
    """
    
    def __init__(self, db_path: str = "panda_spa.db")
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
    
    def initialize_database(self) -> None
        """
        Initialize database: create engine, session factory, and tables.
        Should be called once at application startup.
        """
    
    def create_tables(self) -> None
        """
        Create all database tables if they don't exist.
        Uses SQLAlchemy declarative base to create schema.
        """
    
    def drop_tables(self) -> None
        """
        Drop all database tables (use with caution - for testing/reset).
        """
```

### Session Management
```python
    def get_session(self) -> Session
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session object
            
        Note:
            Caller is responsible for closing the session.
            Consider using UnitOfWork for automatic session management.
        """
    
    def close(self) -> None
        """
        Close all database connections and cleanup resources.
        Should be called at application shutdown.
        """
```

### Query Execution
```python
    def execute_query(self, query_func: Callable[[Session], T]) -> T
        """
        Execute a query function within a session context.
        
        Args:
            query_func: Function that takes a Session and returns a result
            
        Returns:
            Result from query_func
            
        Example:
            result = db_manager.execute_query(lambda session: 
                session.query(Customer).all())
        """
    
    def execute_transaction(self, transaction_func: Callable[[Session], None]) -> bool
        """
        Execute a transaction function with automatic commit/rollback.
        
        Args:
            transaction_func: Function that performs database operations
            
        Returns:
            True if transaction succeeded, False if rolled back
            
        Example:
            success = db_manager.execute_transaction(lambda session:
                session.add(new_customer))
        """
```

### Utility Methods
```python
    def backup_database(self, backup_path: str) -> None
        """
        Create a backup of the database file.
        
        Args:
            backup_path: Path where backup should be saved
        """
    
    def restore_database(self, backup_path: str) -> None
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Path to backup file
            
        Warning:
            This will overwrite current database.
        """
    
    def get_database_info(self) -> dict
        """
        Get database metadata (size, table counts, etc.).
        
        Returns:
            Dictionary with database information
        """
```

---

## UnitOfWork Pattern Methods

### Context Manager
```python
class UnitOfWork:
    """
    Unit of Work pattern implementation for managing database transactions.
    Ensures all operations in a transaction are committed or rolled back together.
    """
    
    def __init__(self, db_manager: DatabaseManagement)
        """
        Initialize UnitOfWork with database manager.
        
        Args:
            db_manager: DatabaseManagement instance
        """
    
    def __enter__(self) -> 'UnitOfWork'
        """
        Enter context manager - creates new session.
        
        Returns:
            Self for use in 'with' statement
        """
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None
        """
        Exit context manager - commits or rolls back transaction.
        
        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value
            exc_tb: Exception traceback
        """
```

### Transaction Control
```python
    def commit(self) -> None
        """
        Manually commit the current transaction.
        Usually called automatically in __exit__, but can be called explicitly.
        """
    
    def rollback(self) -> None
        """
        Rollback the current transaction.
        Discards all changes made in this unit of work.
        """
    
    def flush(self) -> None
        """
        Flush pending changes to database without committing.
        Useful for getting auto-generated IDs before commit.
        """
```

### Repository Access Methods
```python
    def get_customer_repo(self) -> CustomerRepository
        """
        Get customer repository for customer operations.
        
        Returns:
            CustomerRepository instance bound to current session
        """
    
    def get_service_repo(self) -> ServiceRepository
        """
        Get service repository for service operations.
        
        Returns:
            ServiceRepository instance bound to current session
        """
    
    def get_appointment_repo(self) -> AppointmentRepository
        """
        Get appointment repository for appointment operations.
        
        Returns:
            AppointmentRepository instance bound to current session
        """
    
    def get_financial_repo(self) -> FinancialRepository
        """
        Get financial record repository for financial operations.
        
        Returns:
            FinancialRepository instance bound to current session
        """
    
    def get_supplier_repo(self) -> SupplierRepository
        """
        Get supplier repository for supplier operations.
        
        Returns:
            SupplierRepository instance bound to current session
        """
    
    def get_preference_repo(self) -> PreferenceRepository
        """
        Get preference repository for customer preference operations.
        
        Returns:
            PreferenceRepository instance bound to current session
        """
```

### Batch Operations
```python
    def batch_add(self, objects: List[Base]) -> None
        """
        Add multiple objects to session in batch.
        
        Args:
            objects: List of model instances to add
        """
    
    def batch_delete(self, objects: List[Base]) -> None
        """
        Delete multiple objects from session in batch.
        
        Args:
            objects: List of model instances to delete
        """
```

### Query Helpers
```python
    def query(self, model_class: Type[Base]) -> Query
        """
        Get a query object for the specified model.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            SQLAlchemy Query object
            
        Example:
            customers = uow.query(Customer).filter_by(species='Bear').all()
        """
```

---

## Usage Pattern

### Example 1: Simple Query
```python
with UnitOfWork(db_manager) as uow:
    customers = uow.get_customer_repo().get_all()
    # Transaction auto-commits on exit
```

### Example 2: Create with Related Objects
```python
with UnitOfWork(db_manager) as uow:
    customer = Customer(name="Bamboo Bear", species="Bear")
    appointment = Appointment(customer=customer, service=service)
    uow.get_appointment_repo().add(appointment)
    # Both customer and appointment committed together
```

### Example 3: Transaction with Rollback
```python
with UnitOfWork(db_manager) as uow:
    try:
        # Multiple operations
        uow.get_appointment_repo().add(appointment1)
        uow.get_appointment_repo().add(appointment2)
        uow.commit()  # Explicit commit
    except Exception:
        uow.rollback()  # Rollback on error
```

### Example 4: Financial Transaction
```python
with UnitOfWork(db_manager) as uow:
    # Create appointment
    appointment = uow.get_appointment_repo().create(...)
    
    # Record revenue
    revenue = FinancialRecord(
        transaction_type="revenue",
        amount=appointment.service.price,
        appointment_id=appointment.id
    )
    uow.get_financial_repo().add(revenue)
    
    # Update customer preferences
    uow.get_preference_repo().update_preference(
        customer_id=appointment.customer_id,
        service_id=appointment.service_id
    )
    # All changes committed atomically
```


