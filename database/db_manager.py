"""
Database Management class for Panda Spa application.
Handles all SQLite database interactions using SQLAlchemy ORM.
"""

import os
import shutil
from typing import Callable, TypeVar, Optional, Type, Any, Dict, List
from sqlalchemy import create_engine, Engine, text, inspect, select, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .base import Base

T = TypeVar('T')


class DatabaseManagement:
    """
    Centralized database management class responsible for all SQLite interactions.
    Uses SQLAlchemy ORM for database operations.
    """
    
    def __init__(self, db_path: str = "panda_spa.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._initialized = False
    
    def initialize_database(self) -> None:
        """
        Initialize database: create engine, session factory, and tables.
        Should be called once at application startup.
        """
        if self._initialized:
            return
        
        # Create SQLite engine with connection pooling
        # check_same_thread=False allows multi-threaded access if needed
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,  # Set to True for SQL query logging
            connect_args={"check_same_thread": False}
        )
        
        # Create session factory
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        # Create all tables
        self.create_tables()
        
        self._initialized = True
    
    def create_tables(self) -> None:
        """
        Create all database tables if they don't exist.
        Uses SQLAlchemy declarative base to create schema.
        """
        if self.engine is None:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        # Import all models here to ensure they're registered with Base
        # This ensures all model tables are created
        try:
            from models import Customer, Service, Appointment, Supplier, FinancialRecord, CustomerPreference  # Import models to register with Base
        except ImportError:
            pass  # Models not created yet
        
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """
        Drop all database tables (use with caution - for testing/reset).
        """
        if self.engine is None:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session object
            
        Note:
            Caller is responsible for closing the session.
            Consider using UnitOfWork for automatic session management.
        """
        if self.session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        return self.session_factory()
    
    def close(self) -> None:
        """
        Close all database connections and cleanup resources.
        Should be called at application shutdown.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.session_factory = None
            self._initialized = False
    
    def execute_query(self, query_func: Callable[[Session], T]) -> T:
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
        session = self.get_session()
        try:
            result = query_func(session)
            return result
        finally:
            session.close()
    
    def execute_transaction(self, transaction_func: Callable[[Session], None]) -> bool:
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
        session = self.get_session()
        try:
            transaction_func(session)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Transaction failed: {e}")
            return False
        finally:
            session.close()
    
    def backup_database(self, backup_path: str) -> None:
        """
        Create a backup of the database file.
        
        Args:
            backup_path: Path where backup should be saved
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        # Ensure backup directory exists
        backup_dir = os.path.dirname(backup_path)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        shutil.copy2(self.db_path, backup_path)
    
    def restore_database(self, backup_path: str) -> None:
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Path to backup file
            
        Warning:
            This will overwrite current database.
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Close current connections
        self.close()
        
        # Copy backup to database path
        shutil.copy2(backup_path, self.db_path)
        
        # Reinitialize
        self.initialize_database()
    
    def get_database_info(self) -> dict:
        """
        Get database metadata (size, table counts, etc.).
        
        Returns:
            Dictionary with database information
        """
        info = {
            "db_path": self.db_path,
            "exists": os.path.exists(self.db_path),
            "initialized": self._initialized
        }
        
        if os.path.exists(self.db_path):
            info["size_bytes"] = os.path.getsize(self.db_path)
            info["size_mb"] = round(info["size_bytes"] / (1024 * 1024), 2)
        
        if self.engine:
            # Get table names using SQLAlchemy 2.0 inspect API
            inspector = inspect(self.engine)
            info["tables"] = inspector.get_table_names()
            info["table_count"] = len(info["tables"])
        
        return info
    
    # ==================== Convenience CRUD Methods ====================
    
    def save(self, obj: Base) -> bool:
        """
        Save (add) a single object to the database and commit.
        
        Args:
            obj: SQLAlchemy model instance to save
            
        Returns:
            True if saved successfully, False otherwise
            
        Example:
            customer = Customer(name="Bamboo Bear", species="Bear")
            success = db_manager.save(customer)
        """
        session = self.get_session()
        try:
            session.add(obj)
            session.flush()  # Flush to get ID
            obj_id = obj.id  # Get ID while still in session
            session.commit()
            # Update object's __dict__ to preserve ID after detach
            if obj_id is not None:
                obj.__dict__['id'] = obj_id
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Save failed: {e}")
            return False
        finally:
            session.close()
    
    def create(self, model_class: Type[Base], **kwargs) -> Optional[Base]:
        """
        Create a new instance of a model and save it to the database.
        
        Args:
            model_class: The model class to instantiate
            **kwargs: Field values for the new instance
            
        Returns:
            The created instance if successful, None otherwise
            
        Example:
            customer = db_manager.create(Customer, name="Bamboo Bear", species="Bear")
        """
        try:
            obj = model_class(**kwargs)
            session = self.get_session()
            try:
                session.add(obj)
                session.flush()  # Flush to get ID
                # Get all attribute values while in session
                obj_id = obj.id
                obj_dict = {key: getattr(obj, key) for key in obj.__table__.columns.keys()}
                session.commit()
                # Update object's __dict__ to preserve values after detach
                obj.__dict__.update(obj_dict)
                return obj
            except SQLAlchemyError as e:
                session.rollback()
                print(f"Create failed: {e}")
                return None
            finally:
                session.close()
        except Exception as e:
            print(f"Failed to create {model_class.__name__}: {e}")
            return None
    
    def update(self, obj: Base, **kwargs) -> bool:
        """
        Update an existing object's attributes and save changes.
        
        Args:
            obj: The object to update
            **kwargs: Field names and new values to update
            
        Returns:
            True if updated successfully, False otherwise
            
        Example:
            success = db_manager.update(customer, name="Updated Name", contact_info="new@email.com")
        """
        session = self.get_session()
        try:
            # Merge object into session
            merged_obj = session.merge(obj)
            
            # Update attributes
            for key, value in kwargs.items():
                if hasattr(merged_obj, key):
                    setattr(merged_obj, key, value)
                else:
                    raise AttributeError(f"{merged_obj.__class__.__name__} has no attribute '{key}'")
            
            session.commit()
            # Update original object's attributes
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            return True
        except (SQLAlchemyError, AttributeError) as e:
            session.rollback()
            print(f"Update failed: {e}")
            return False
        finally:
            session.close()
    
    def delete(self, obj: Base) -> bool:
        """
        Delete an object from the database.
        
        Args:
            obj: The object to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Example:
            success = db_manager.delete(customer)
        """
        return self.execute_transaction(
            lambda session: session.delete(session.merge(obj))
        )
    
    def get_by_id(self, model_class: Type[Base], id: int) -> Optional[Base]:
        """
        Get a single object by its ID.
        
        Args:
            model_class: The model class to query
            id: The ID of the object to retrieve
            
        Returns:
            The object if found, None otherwise
            
        Example:
            customer = db_manager.get_by_id(Customer, 1)
        """
        return self.execute_query(
            lambda session: session.get(model_class, id)
        )
    
    def get_all(self, model_class: Type[Base]) -> List[Base]:
        """
        Get all instances of a model class.
        
        Args:
            model_class: The model class to query
            
        Returns:
            List of all instances
            
        Example:
            all_customers = db_manager.get_all(Customer)
        """
        return self.execute_query(
            lambda session: list(session.scalars(select(model_class)).all())
        )
    
    def find(self, model_class: Type[Base], **filters) -> List[Base]:
        """
        Find objects matching the given filters.
        
        Args:
            model_class: The model class to query
            **filters: Field names and values to filter by
            
        Returns:
            List of matching instances
            
        Example:
            bears = db_manager.find(Customer, species="Bear")
            active_customers = db_manager.find(Customer, is_active=True)
        """
        return self.execute_query(
            lambda session: list(
                session.scalars(
                    select(model_class).filter_by(**filters)
                ).all()
            )
        )
    
    def find_one(self, model_class: Type[Base], **filters) -> Optional[Base]:
        """
        Find a single object matching the given filters.
        
        Args:
            model_class: The model class to query
            **filters: Field names and values to filter by
            
        Returns:
            The first matching instance, or None if not found
            
        Example:
            customer = db_manager.find_one(Customer, name="Bamboo Bear")
        """
        return self.execute_query(
            lambda session: session.scalars(
                select(model_class).filter_by(**filters).limit(1)
            ).first()
        )
    
    def count(self, model_class: Type[Base], **filters) -> int:
        """
        Count objects matching the given filters (or all if no filters).
        
        Args:
            model_class: The model class to query
            **filters: Optional field names and values to filter by
            
        Returns:
            Number of matching instances
            
        Example:
            total = db_manager.count(Customer)
            bear_count = db_manager.count(Customer, species="Bear")
        """
        return self.execute_query(
            lambda session: session.scalar(
                select(func.count()).select_from(model_class).filter_by(**filters)
            )
        )
    
    def exists(self, model_class: Type[Base], **filters) -> bool:
        """
        Check if any objects exist matching the given filters.
        
        Args:
            model_class: The model class to query
            **filters: Field names and values to filter by
            
        Returns:
            True if at least one match exists, False otherwise
            
        Example:
            has_bears = db_manager.exists(Customer, species="Bear")
        """
        return self.count(model_class, **filters) > 0
    
    def commit(self, session: Session) -> bool:
        """
        Commit changes in a session.
        
        Args:
            session: The session to commit
            
        Returns:
            True if committed successfully, False if rolled back
            
        Example:
            session = db_manager.get_session()
            session.add(customer)
            success = db_manager.commit(session)
            session.close()
        """
        try:
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Commit failed: {e}")
            return False
    
    def rollback(self, session: Session) -> None:
        """
        Rollback changes in a session.
        
        Args:
            session: The session to rollback
            
        Example:
            session = db_manager.get_session()
            session.add(customer)
            db_manager.rollback(session)  # Discard changes
            session.close()
        """
        session.rollback()
    
    def flush(self, session: Session) -> None:
        """
        Flush pending changes to database without committing.
        Useful for getting auto-generated IDs before commit.
        
        Args:
            session: The session to flush
            
        Example:
            session = db_manager.get_session()
            session.add(customer)
            db_manager.flush(session)  # Customer.id is now available
            customer_id = customer.id
            db_manager.commit(session)
            session.close()
        """
        session.flush()
    
    def refresh(self, obj: Base) -> bool:
        """
        Refresh an object from the database to get latest values.
        
        Args:
            obj: The object to refresh
            
        Returns:
            True if refreshed successfully, False otherwise
            
        Example:
            success = db_manager.refresh(customer)  # Get latest data from DB
        """
        if not hasattr(obj, 'id') or obj.id is None:
            return False
        
        session = self.get_session()
        try:
            # Get fresh instance from database
            fresh_obj = session.get(obj.__class__, obj.id)
            if fresh_obj:
                # Update original object's attributes
                for key in obj.__table__.columns.keys():
                    if hasattr(fresh_obj, key):
                        setattr(obj, key, getattr(fresh_obj, key))
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Refresh failed: {e}")
            return False
        finally:
            session.close()
    
    def bulk_save(self, objects: List[Base]) -> bool:
        """
        Save multiple objects in a single transaction.
        
        Args:
            objects: List of SQLAlchemy model instances to save
            
        Returns:
            True if all saved successfully, False otherwise
            
        Example:
            customers = [Customer(name="Bear1"), Customer(name="Bear2")]
            success = db_manager.bulk_save(customers)
        """
        return self.execute_transaction(
            lambda session: session.add_all(objects)
        )
    
    def bulk_delete(self, objects: List[Base]) -> bool:
        """
        Delete multiple objects in a single transaction.
        
        Args:
            objects: List of SQLAlchemy model instances to delete
            
        Returns:
            True if all deleted successfully, False otherwise
            
        Example:
            success = db_manager.bulk_delete(old_customers)
        """
        return self.execute_transaction(
            lambda session: [session.delete(session.merge(obj)) for obj in objects]
        )

