"""
Financial Management Window for Panda Spa.
Provides GUI for tracking revenue, expenses, and financial reporting.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from typing import Optional
from database.db_manager import DatabaseManagement
from models.financial_record import FinancialRecord
from models.supplier import Supplier
from services.financial_service import FinancialService


class FinancialWindow:
    """
    Main window for financial management.
    Provides financial tracking, reporting, and expense recording.
    """
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManagement):
        """
        Initialize financial management window.
        
        Args:
            parent: Parent Tkinter window
            db_manager: DatabaseManagement instance
        """
        self.parent = parent
        self.db_manager = db_manager
        self.financial_service = FinancialService(db_manager)
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Panda Spa - Financial Management")
        self.window.geometry("1200x800")
        
        self._create_widgets()
        self._load_suppliers()
        self._update_dashboard()
        self._load_financial_records()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Dashboard and Expense Form
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        
        # Financial Dashboard (with scrollbar)
        dashboard_frame = ttk.LabelFrame(left_panel, text="Financial Dashboard", padding="10")
        dashboard_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.rowconfigure(0, weight=1)
        
        # Create scrollable canvas for dashboard
        dashboard_canvas = tk.Canvas(dashboard_frame, highlightthickness=0)
        dashboard_scrollbar = ttk.Scrollbar(dashboard_frame, orient=tk.VERTICAL, command=dashboard_canvas.yview)
        dashboard_inner = ttk.Frame(dashboard_canvas)
        
        dashboard_canvas_window = dashboard_canvas.create_window((0, 0), window=dashboard_inner, anchor="nw")
        
        def update_dashboard_scroll(event=None):
            dashboard_canvas.update_idletasks()
            bbox = dashboard_canvas.bbox("all")
            if bbox:
                dashboard_canvas.configure(scrollregion=bbox)
        
        def update_dashboard_width(event=None):
            canvas_width = event.width if event else dashboard_canvas.winfo_width()
            if canvas_width > 1:
                dashboard_canvas.itemconfig(dashboard_canvas_window, width=canvas_width)
        
        dashboard_inner.bind("<Configure>", update_dashboard_scroll)
        dashboard_canvas.bind("<Configure>", update_dashboard_width)
        dashboard_canvas.configure(yscrollcommand=dashboard_scrollbar.set)
        
        dashboard_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dashboard_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        def on_dashboard_mousewheel(event):
            dashboard_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        dashboard_canvas.bind("<MouseWheel>", on_dashboard_mousewheel)
        
        dashboard_inner.columnconfigure(0, weight=1)
        
        # Date range selection
        date_frame = ttk.Frame(dashboard_inner)
        date_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, padx=(0, 5))
        self.start_date_entry = ttk.Entry(date_frame, width=12)
        self.start_date_entry.insert(0, (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        self.start_date_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(date_frame, text="To:").grid(row=0, column=2, padx=(0, 5))
        self.end_date_entry = ttk.Entry(date_frame, width=12)
        self.end_date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.end_date_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(date_frame, text="Update", command=self._update_dashboard).grid(row=0, column=4)
        
        # Financial summary
        summary_frame = ttk.Frame(dashboard_inner)
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.revenue_label = ttk.Label(summary_frame, text="Revenue: $0.00", font=("Arial", 14, "bold"), foreground="green")
        self.revenue_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.expense_label = ttk.Label(summary_frame, text="Expenses: $0.00", font=("Arial", 14, "bold"), foreground="red")
        self.expense_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.profit_label = ttk.Label(summary_frame, text="Profit: $0.00", font=("Arial", 16, "bold"))
        self.profit_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Category breakdown
        breakdown_frame = ttk.LabelFrame(dashboard_inner, text="Expense Breakdown by Category", padding="10")
        breakdown_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        breakdown_frame.columnconfigure(0, weight=1)
        
        breakdown_text_frame = ttk.Frame(breakdown_frame)
        breakdown_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        breakdown_text_frame.columnconfigure(0, weight=1)
        
        self.breakdown_text = tk.Text(breakdown_text_frame, height=8, width=30, state=tk.DISABLED)
        self.breakdown_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        breakdown_text_scrollbar = ttk.Scrollbar(breakdown_text_frame, orient=tk.VERTICAL, command=self.breakdown_text.yview)
        breakdown_text_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.breakdown_text.configure(yscrollcommand=breakdown_text_scrollbar.set)
        
        # Expense Form (with scrollbar)
        expense_frame = ttk.LabelFrame(left_panel, text="Record Expense", padding="10")
        expense_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        expense_frame.columnconfigure(0, weight=1)
        expense_frame.rowconfigure(0, weight=1)
        
        # Create scrollable canvas for expense form
        expense_canvas = tk.Canvas(expense_frame, highlightthickness=0)
        expense_scrollbar = ttk.Scrollbar(expense_frame, orient=tk.VERTICAL, command=expense_canvas.yview)
        expense_form_inner = ttk.Frame(expense_canvas)
        
        expense_canvas_window = expense_canvas.create_window((0, 0), window=expense_form_inner, anchor="nw")
        
        def update_expense_scroll(event=None):
            expense_canvas.update_idletasks()
            bbox = expense_canvas.bbox("all")
            if bbox:
                expense_canvas.configure(scrollregion=bbox)
        
        def update_expense_width(event=None):
            canvas_width = event.width if event else expense_canvas.winfo_width()
            if canvas_width > 1:
                expense_canvas.itemconfig(expense_canvas_window, width=canvas_width)
        
        expense_form_inner.bind("<Configure>", update_expense_scroll)
        expense_canvas.bind("<Configure>", update_expense_width)
        expense_canvas.configure(yscrollcommand=expense_scrollbar.set)
        
        expense_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        expense_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        def on_expense_mousewheel(event):
            expense_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        expense_canvas.bind("<MouseWheel>", on_expense_mousewheel)
        
        expense_form_inner.columnconfigure(1, weight=1)
        
        ttk.Label(expense_form_inner, text="Amount ($):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.amount_entry = ttk.Entry(expense_form_inner, width=25)
        self.amount_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(expense_form_inner, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(expense_form_inner, width=22, state="readonly")
        expense_categories = [
            FinancialRecord.CATEGORY_HOT_WATER,
            FinancialRecord.CATEGORY_TEA,
            FinancialRecord.CATEGORY_SUPPLIES,
            FinancialRecord.CATEGORY_EQUIPMENT,
            FinancialRecord.CATEGORY_MAINTENANCE,
            FinancialRecord.CATEGORY_OTHER
        ]
        self.category_combo['values'] = expense_categories
        self.category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(expense_form_inner, text="Supplier:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.supplier_combo = ttk.Combobox(expense_form_inner, width=22, state="readonly")
        self.supplier_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(expense_form_inner, text="Description:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.description_entry = ttk.Entry(expense_form_inner, width=25)
        self.description_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(expense_form_inner, text="Receipt #:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.receipt_entry = ttk.Entry(expense_form_inner, width=25)
        self.receipt_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(expense_form_inner, text="Notes:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.expense_notes_text = tk.Text(expense_form_inner, width=25, height=3)
        self.expense_notes_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Button(expense_form_inner, text="Record Expense", command=self._record_expense).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Right panel - Financial Records List
        list_frame = ttk.LabelFrame(main_frame, text="Financial Records", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Type:").grid(row=0, column=0, padx=(0, 5))
        self.type_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.type_filter['values'] = ['All', FinancialRecord.REVENUE, FinancialRecord.EXPENSE]
        self.type_filter.set('All')
        self.type_filter.grid(row=0, column=1, padx=(0, 5))
        self.type_filter.bind('<<ComboboxSelected>>', self._on_filter)
        
        ttk.Label(filter_frame, text="Category:").grid(row=0, column=2, padx=(10, 5))
        self.category_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.category_filter['values'] = ['All'] + FinancialRecord.get_categories()
        self.category_filter.set('All')
        self.category_filter.grid(row=0, column=3, padx=(0, 5))
        self.category_filter.bind('<<ComboboxSelected>>', self._on_filter)
        
        # Financial records list (Treeview)
        columns = ('ID', 'Date', 'Type', 'Amount', 'Category', 'Description', 'Supplier')
        self.records_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=25)
        
        # Configure columns
        self.records_tree.heading('ID', text='ID')
        self.records_tree.heading('Date', text='Date')
        self.records_tree.heading('Type', text='Type')
        self.records_tree.heading('Amount', text='Amount ($)')
        self.records_tree.heading('Category', text='Category')
        self.records_tree.heading('Description', text='Description')
        self.records_tree.heading('Supplier', text='Supplier')
        
        self.records_tree.column('ID', width=50)
        self.records_tree.column('Date', width=120)
        self.records_tree.column('Type', width=80)
        self.records_tree.column('Amount', width=100)
        self.records_tree.column('Category', width=120)
        self.records_tree.column('Description', width=200)
        self.records_tree.column('Supplier', width=150)
        
        self.records_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.records_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.records_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame, text="Refresh", command=self._load_financial_records).pack(side=tk.LEFT, padx=5)
    
    def _load_suppliers(self):
        """Load suppliers into combo box."""
        suppliers = self.db_manager.get_all(Supplier)
        supplier_list = ['None'] + [f"{s.id}: {s.name}" for s in suppliers]
        self.supplier_combo['values'] = supplier_list
        self.supplier_combo.set('None')
    
    def _update_dashboard(self):
        """Update financial dashboard with current data."""
        try:
            # Parse date range
            start_date_str = self.start_date_entry.get()
            end_date_str = self.end_date_entry.get()
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
            if end_date:
                # Set to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            
            # Get financial summary
            summary = self.financial_service.get_financial_summary(start_date, end_date)
            
            # Update labels
            self.revenue_label.config(text=f"Revenue: ${summary['revenue']:.2f}")
            self.expense_label.config(text=f"Expenses: ${summary['expenses']:.2f}")
            
            profit = summary['profit']
            profit_color = "green" if profit >= 0 else "red"
            self.profit_label.config(text=f"Profit: ${profit:.2f}", foreground=profit_color)
            
            # Update category breakdown
            self.breakdown_text.config(state=tk.NORMAL)
            self.breakdown_text.delete('1.0', tk.END)
            
            breakdown = summary['category_breakdown']
            if breakdown:
                for category, amount in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
                    category_display = category.replace('_', ' ').title()
                    self.breakdown_text.insert(tk.END, f"{category_display}: ${amount:.2f}\n")
            else:
                self.breakdown_text.insert(tk.END, "No expenses in this period")
            
            self.breakdown_text.config(state=tk.DISABLED)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
    
    def _load_financial_records(self):
        """Load financial records into the treeview."""
        # Clear existing items
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # Get all records
        records = self.db_manager.get_all(FinancialRecord)
        
        # Apply filters
        type_filter = self.type_filter.get()
        category_filter = self.category_filter.get()
        
        for record in records:
            # Type filter
            if type_filter != 'All' and record.transaction_type != type_filter:
                continue
            
            # Category filter
            if category_filter != 'All' and record.category != category_filter:
                continue
            
            # Get supplier name
            supplier_name = ''
            if record.supplier_id:
                supplier = self.db_manager.get_by_id(Supplier, record.supplier_id)
                if supplier:
                    supplier_name = supplier.name
            
            # Format date
            date_str = record.transaction_date.strftime('%Y-%m-%d %H:%M')
            
            # Format type
            type_display = record.transaction_type.title()
            
            # Format category
            category_display = record.category.replace('_', ' ').title()
            
            # Color code by type
            tag = 'revenue' if record.transaction_type == FinancialRecord.REVENUE else 'expense'
            
            self.records_tree.insert('', tk.END, values=(
                record.id,
                date_str,
                type_display,
                f"${record.amount:.2f}",
                category_display,
                record.description[:50] + '...' if len(record.description) > 50 else record.description,
                supplier_name
            ), tags=(tag,))
        
        # Configure tags for colors
        self.records_tree.tag_configure('revenue', foreground='green')
        self.records_tree.tag_configure('expense', foreground='red')
    
    def _on_filter(self, event=None):
        """Handle filter changes."""
        self._load_financial_records()
    
    def _record_expense(self):
        """Record a new expense."""
        # Validate inputs
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive amount!")
            return
        
        category = self.category_combo.get()
        if not category:
            messagebox.showerror("Error", "Please select a category!")
            return
        
        description = self.description_entry.get().strip()
        if not description:
            messagebox.showerror("Error", "Description is required!")
            return
        
        # Get supplier ID
        supplier_id = None
        supplier_str = self.supplier_combo.get()
        if supplier_str and supplier_str != 'None':
            try:
                supplier_id = int(supplier_str.split(':')[0])
            except (ValueError, IndexError):
                pass
        
        receipt_number = self.receipt_entry.get().strip() or None
        notes = self.expense_notes_text.get('1.0', tk.END).strip() or None
        
        # Record expense
        record, error = self.financial_service.record_expense(
            amount=amount,
            category=category,
            description=description,
            supplier_id=supplier_id,
            receipt_number=receipt_number,
            notes=notes
        )
        
        if record:
            messagebox.showinfo("Success", "Expense recorded successfully!")
            # Clear form
            self.amount_entry.delete(0, tk.END)
            self.category_combo.set('')
            self.supplier_combo.set('None')
            self.description_entry.delete(0, tk.END)
            self.receipt_entry.delete(0, tk.END)
            self.expense_notes_text.delete('1.0', tk.END)
            # Refresh
            self._update_dashboard()
            self._load_financial_records()
        else:
            messagebox.showerror("Error", f"Failed to record expense: {error}")





