"""
Panda Spa - Main Application Entry Point
Thermal Water Wellness Center Management System
"""

import sys
import traceback
from database.db_manager import DatabaseManagement
from gui.main_window import MainWindow


def main():
    """Main application entry point."""
    db_manager = None
    
    try:
        # Initialize database
        print("Initializing Panda Spa database...")
        db_manager = DatabaseManagement(db_path="panda_spa.db")
        db_manager.initialize_database()
        print("Database initialized successfully!")
        
        # Create and run main window
        print("Starting Panda Spa application...")
        app = MainWindow(db_manager)
        app.run()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        if db_manager:
            db_manager.close()
        sys.exit(1)
    
    finally:
        # Ensure database is closed
        if db_manager:
            db_manager.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()

