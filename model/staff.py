from model.database import Database
from datetime import datetime


class Staff:
    """Staff model for database operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def _convert_date_format(self, date_str):
        """Convert date from DD/MM/YYYY to YYYY-MM-DD for MySQL"""
        try:
            if not date_str:
                return None
            # Try parsing DD/MM/YYYY format
            if '/' in date_str:
                dt = datetime.strptime(date_str, '%d/%m/%Y')
                return dt.strftime('%Y-%m-%d')
            # Already in YYYY-MM-DD format
            elif '-' in date_str:
                return date_str
            return None
        except:
            return None
    
    def get_all_positions(self):
        """Get all available positions from BAC_LUONG"""
        query = "SELECT chuc_vu, he_so_luong FROM BAC_LUONG ORDER BY chuc_vu"
        return self.db.fetch_query(query)
    
    def check_position_exists(self, chuc_vu):
        """Check if position exists in BAC_LUONG"""
        query = "SELECT COUNT(*) as count FROM BAC_LUONG WHERE chuc_vu = %s"
        result = self.db.fetch_query(query, (chuc_vu,))
        return result[0]['count'] > 0 if result else False
    
    def create_staff(self, ma_nv, ho_va_ten, sdt, chuc_vu, ngay_vao_lam, ma_quan_ly):
        """
        Create a new staff (NHAN_VIEN and LUONG tables)
        Returns: (success: bool, error_message: str)
        """
        try:
            # Check if position exists in BAC_LUONG
            if not self.check_position_exists(chuc_vu):
                return False, f"Chức vụ '{chuc_vu}' không tồn tại trong hệ thống. Vui lòng chọn chức vụ hợp lệ."
            
            # Convert date format
            ngay_vao_lam_formatted = self._convert_date_format(ngay_vao_lam)
            if not ngay_vao_lam_formatted:
                return False, "Định dạng ngày không hợp lệ. Vui lòng nhập theo định dạng DD/MM/YYYY."
            
            # Insert into NHAN_VIEN table first
            query_nv = """
            INSERT INTO NHAN_VIEN (ma_nv, ho_va_ten, sdt, chuc_vu, ngay_vao_lam, ma_quan_ly)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params_nv = (ma_nv, ho_va_ten, sdt, chuc_vu, ngay_vao_lam_formatted, ma_quan_ly if ma_quan_ly else None)
            cursor_nv = self.db.execute_query(query_nv, params_nv)
            
            if not cursor_nv:
                return False, "Không thể thêm nhân viên. Có thể mã nhân viên đã tồn tại."
            
            # Insert into LUONG table with default values (0 for so_gio_lam and thuong)
            query_luong = """
            INSERT INTO LUONG (ma_nv, so_gio_lam, thuong)
            VALUES (%s, 0, 0)
            """
            params_luong = (ma_nv,)
            cursor_luong = self.db.execute_query(query_luong, params_luong)
            
            if cursor_luong:
                return True, "Thành công"
            else:
                return False, "Không thể tạo bản ghi lương."
        except Exception as e:
            error_msg = str(e)
            print(f"Error creating staff: {error_msg}")
            return False, f"Lỗi: {error_msg}"
    
    def get_all_staff(self):
        """
        Get all staff information
        """
        query = """
        SELECT nv.ma_nv, nv.ho_va_ten, nv.chuc_vu, nv.sdt, nv.ngay_vao_lam, 
               nv.ma_quan_ly
        FROM NHAN_VIEN nv
        ORDER BY nv.ma_nv DESC
        """
        return self.db.fetch_query(query)
    
    def search_staff(self, search_term):
        """
        Search staff by name, position, or phone
        """
        query = """
        SELECT nv.ma_nv, nv.ho_va_ten, nv.chuc_vu, nv.sdt, nv.ngay_vao_lam, 
               nv.ma_quan_ly
        FROM NHAN_VIEN nv
        WHERE nv.ho_va_ten LIKE %s OR nv.chuc_vu LIKE %s OR nv.sdt LIKE %s OR nv.ma_nv LIKE %s
        ORDER BY nv.ma_nv DESC
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern)
        return self.db.fetch_query(query, params)
    
    def get_staff_by_id(self, ma_nv):
        """
        Get staff by ma_nv
        """
        query = """
        SELECT nv.ma_nv, nv.ho_va_ten, nv.chuc_vu, nv.sdt, nv.ngay_vao_lam, 
               nv.ma_quan_ly
        FROM NHAN_VIEN nv
        WHERE nv.ma_nv = %s
        """
        params = (ma_nv,)
        result = self.db.fetch_query(query, params)
        return result[0] if result else None
    
    def update_staff(self, ma_nv, ho_va_ten, sdt, chuc_vu, ngay_vao_lam, ma_quan_ly, so_gio_lam, thuong=0):
        """
        Update staff information (NHAN_VIEN and LUONG tables)
        """
        try:
            # Convert date format
            ngay_vao_lam_formatted = self._convert_date_format(ngay_vao_lam)
            
            # Update NHAN_VIEN table
            query_nv = """
            UPDATE NHAN_VIEN 
            SET ho_va_ten=%s, sdt=%s, chuc_vu=%s, ngay_vao_lam=%s, ma_quan_ly=%s
            WHERE ma_nv=%s
            """
            params_nv = (ho_va_ten, sdt, chuc_vu, ngay_vao_lam_formatted, ma_quan_ly if ma_quan_ly else None, ma_nv)
            cursor = self.db.execute_query(query_nv, params_nv)
            
            # Update LUONG table
            query_luong = """
            UPDATE LUONG 
            SET so_gio_lam=0, thuong=0
            WHERE ma_nv=%s
            """
            params_luong = (ma_nv,)
            cursor = self.db.execute_query(query_luong, params_luong)
            
            return cursor is not None
        except Exception as e:
            print(f"Error updating staff: {e}")
            return False
    
    def delete_staff(self, ma_nv):
        """
        Delete staff (CASCADE will delete LUONG record automatically)
        """
        query = "DELETE FROM NHAN_VIEN WHERE ma_nv = %s"
        params = (ma_nv,)
        cursor = self.db.execute_query(query, params)
        return cursor is not None
