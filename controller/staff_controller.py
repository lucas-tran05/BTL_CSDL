from model.database import Database
from model.staff import Staff


class StaffController:
    """Controller layer to connect View and Model"""
    
    def __init__(self, view):
        self.view = view
        self.db = Database()
        self.staff_model = Staff(self.db)
        
        # Connect to database
        if not self.db.connect():
            self.view.show_message("Lỗi kết nối", 
                                  "Không thể kết nối đến cơ sở dữ liệu. Vui lòng kiểm tra cấu hình.",
                                  "error")
    
    def create_staff(self, data):
        """Create a new staff"""
        try:
            success, message = self.staff_model.create_staff(
                data['ma_nv'],
                data['ho_va_ten'],
                data['sdt'],
                data['chuc_vu'],
                data['ngay_vao_lam'],
                data['ma_quan_ly'],
                data['so_gio_lam'],
                data.get('thuong', 0)
            )
            
            if success:
                self.view.show_message("Thành công", "Tạo nhân viên thành công!", "info")
                self.view.clear_form()
                self.view.loadData()
            else:
                self.view.show_message("Lỗi", message, "error")
        except Exception as e:
            self.view.show_message("Lỗi", f"Không thể tạo nhân viên: {str(e)}", "error")
    
    def get_all_positions(self):
        """Get all available positions from BAC_LUONG"""
        return self.staff_model.get_all_positions()
    
    def update_staff(self, ma_nv, data):
        """Update a staff"""
        try:
            result = self.staff_model.update_staff(
                ma_nv,
                data['ho_va_ten'],
                data['sdt'],
                data['chuc_vu'],
                data['ngay_vao_lam'],
                data['ma_quan_ly'],
                data['so_gio_lam'],
                data.get('thuong', 0)
            )
            
            if result:
                self.view.show_message("Thành công", "Cập nhật nhân viên thành công!", "info")
                self.view.clear_form()
                self.view.loadData()
            else:
                self.view.show_message("Lỗi", "Không thể cập nhật nhân viên", "error")
        except Exception as e:
            self.view.show_message("Lỗi", f"Không thể cập nhật nhân viên: {str(e)}", "error")
    
    def delete_staff(self, ma_nv):
        """Delete a staff"""
        try:
            result = self.staff_model.delete_staff(ma_nv)
            
            if result:
                self.view.show_message("Thành công", "Xóa nhân viên thành công!", "info")
                self.view.clear_form()
                self.view.loadData()
            else:
                self.view.show_message("Lỗi", "Không thể xóa nhân viên. Vui lòng kiểm tra.", "error")
        except Exception as e:
            self.view.show_message("Lỗi", f"Không thể xóa nhân viên: {str(e)}", "error")
    
    def load_all_staff(self):
        """Load all staff"""
        try:
            staff_list = self.staff_model.get_all_staff()
            self.view.display_staff(staff_list)
        except Exception as e:
            self.view.show_message("Lỗi", f"Không thể tải danh sách nhân viên: {str(e)}", "error")
    
    def search_staff(self, search_term):
        """Search staff"""
        try:
            if search_term:
                staff_list = self.staff_model.search_staff(search_term)
                self.view.display_staff(staff_list)
            else:
                self.load_all_staff()
        except Exception as e:
            self.view.show_message("Lỗi", f"Không thể tìm kiếm nhân viên: {str(e)}", "error")
    
    def get_all_positions(self):
        """Get all positions from BAC_LUONG table"""
        try:
            positions = self.staff_model.get_all_positions()
            return positions if positions else []
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []
    
    def close(self):
        """Close database connection"""
        self.db.disconnect()
