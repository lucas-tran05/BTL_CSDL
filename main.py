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
        
        # Font scale for zoom functionality
        self.font_scale = 1.0
        
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
        
        # Settings menu with font size options
        settings_menu = tk.Menu(menubar, tearoff=0, font=('Arial', 11))
        menubar.add_cascade(label="Cài đặt", menu=settings_menu)
        settings_menu.add_command(label="Phóng to (Ctrl +)", command=self.zoom_in)
        settings_menu.add_command(label="Thu nhỏ (Ctrl -)", command=self.zoom_out)
        settings_menu.add_command(label="Đặt lại (Ctrl 0)", command=self.zoom_reset)
        settings_menu.add_separator()
        settings_menu.add_command(label="Cỡ chữ hiện tại: 100%", state='disabled')
        self.font_scale_label = settings_menu
        
        menubar.add_command(label="Thoát", command=self.quit_application)
        
        # Keyboard shortcuts
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())  # For Ctrl+=
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_reset())
    
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
        view = StaffView(staff_frame, None, font_scale=self.font_scale)
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
        view = InvoiceView(invoice_frame, None, font_scale=self.font_scale)
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
        view = ReportView(report_frame, None, font_scale=self.font_scale)
        mysql_config = load_db_config()
        controller = ReportController(view, backend="mysql", mysql_config=mysql_config)
        view.controller = controller
        self.current_view = view
        self.current_controller = controller
        controller.load_positions()
        controller.load_seniority()
        controller.load_revenue(view.revenue_frame.month_year_cb.get())
        self.root.title("Hệ thống Quản lý - Báo cáo")
    
    def zoom_in(self):
        """Increase font size"""
        if self.font_scale < 2.0:  # Max 200%
            self.font_scale += 0.1
            self.update_font_scale()
    
    def zoom_out(self):
        """Decrease font size"""
        if self.font_scale > 0.5:  # Min 50%
            self.font_scale -= 0.1
            self.update_font_scale()
    
    def zoom_reset(self):
        """Reset font size to default"""
        self.font_scale = 1.0
        self.update_font_scale()
    
    def update_font_scale(self):
        """Update font scale and reload current view"""
        # Update menu label
        percent = int(self.font_scale * 100)
        
        # Reload current view to apply new font size
        if hasattr(self.current_view, '__class__'):
            view_class = self.current_view.__class__.__name__
            if 'StaffView' in view_class:
                self.show_staff_view()
            elif 'InvoiceView' in view_class:
                self.show_invoice_view()
            elif 'ReportView' in view_class:
                self.show_report_view()
    
    def get_scaled_font_size(self, base_size):
        """Get scaled font size based on current scale"""
        return int(base_size * self.font_scale)
    
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
