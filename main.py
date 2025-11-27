import tkinter as tk
from tkinter import ttk
from view.staff_view import StaffView
from controller.staff_controller import StaffController
from view.invoice_view import InvoiceView
from controller.invoice_controller import InvoiceController
from view.report_view import ReportView
from controller.report_controller import ReportController
from config.db_config import load_db_config


class MainApplication:
    """Main application with menu to switch between forms"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý - Management System")
        # Set window to full screen
        self.root.state('zoomed')  # For Windows
        # Alternative: self.root.attributes('-fullscreen', True)
        
        # Current active view and controller
        self.current_view = None
        self.current_controller = None
        
        # Setup menu
        self.setup_menu()
        
        # Main container for views
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Show staff view by default
        self.show_staff_view()
    
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = tk.Menu(self.root, font=('Arial', 12))
        self.root.config(menu=menubar)
        
        # Add menu items directly to menubar
        menubar.add_command(label="Nhân viên", command=self.show_staff_view)
        menubar.add_command(label="Hóa đơn", command=self.show_invoice_view)
        menubar.add_command(label="Báo cáo", command=self.show_report_view)
        menubar.add_command(label="Thoát", command=self.quit_application)
    
    def clear_main_container(self):
        """Clear all widgets from main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_staff_view(self):
        """Show staff management view"""
        # Close current controller if exists
        if self.current_controller:
            self.current_controller.close()
        
        # Clear container
        self.clear_main_container()
        
        # Create new frame for staff view
        staff_frame = ttk.Frame(self.main_container)
        staff_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create view and controller
        view = StaffView(staff_frame, None)
        controller = StaffController(view)
        view.controller = controller
        
        # Update positions combobox now that controller is set
        view.update_positions()
        
        # Store references
        self.current_view = view
        self.current_controller = controller
        
        # Load data
        view.loadData()
        
        # Update window title
        self.root.title("Hệ thống Quản lý - Nhân viên")
    
    def show_invoice_view(self):
        """Show invoice management view"""
        # Close current controller if exists
        if self.current_controller:
            self.current_controller.close()
        
        # Clear container
        self.clear_main_container()
        
        # Create new frame for invoice view
        invoice_frame = ttk.Frame(self.main_container)
        invoice_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create view and controller
        view = InvoiceView(invoice_frame, None)
        controller = InvoiceController(view)
        view.controller = controller
        
        # Populate combobox after controller is set
        view.populate_medicine_combobox()
        
        # Store references
        self.current_view = view
        self.current_controller = controller
        
        # Load data
        view.loadData()
        
        # Update window title
        self.root.title("Hệ thống Quản lý - Hóa đơn")
    
    def show_report_view(self):
        """Show report management view"""
        if self.current_controller:
            self.current_controller.close()
        self.clear_main_container()
        report_frame = ttk.Frame(self.main_container)
        report_frame.pack(fill=tk.BOTH, expand=True)
        view = ReportView(report_frame, None)
        mysql_config = load_db_config()
        controller = ReportController(view, backend="mysql", mysql_config=mysql_config)
        view.controller = controller
        self.current_view = view
        self.current_controller = controller
        controller.load_positions()
        controller.load_seniority()
        controller.load_revenue(view.revenue_frame.month_year_cb.get())
        self.root.title("Hệ thống Quản lý - Báo cáo")
    
    def quit_application(self):
        """Quit the application"""
        if self.current_controller:
            self.current_controller.close()
        self.root.destroy()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = MainApplication(root)
    
    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", app.quit_application)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
