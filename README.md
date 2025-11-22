# Hệ thống Quản lý - Hướng dẫn cài đặt

Tệp này hướng dẫn cách thiết lập và chạy ứng dụng Tkinter (Python) trong workspace `BTL_CSDL` trên Windows (PowerShell).

**Nội dung:**
- Yêu cầu trước
- Thiết lập môi trường Python
- Cài đặt dependencies
- Cấu hình cơ sở dữ liệu (MySQL)
- Tạo bảng cần thiết (ví dụ `HOA_DON`, `CHI_TIET_HOA_DON`)
- Chạy ứng dụng
- Gỡ lỗi nhanh

---

**Yêu cầu trước**
- Python 3.10+ (đã kiểm tra với Tkinter có sẵn trong bản phân phối chính thức trên Windows)
- MySQL 5.7 / 8.0 hoặc tương đương
- PowerShell (hướng dẫn dưới đây dùng PowerShell 5.1 trên Windows)


**1) Thiết lập môi trường Python (PowerShell)**

Mở PowerShell trong thư mục dự án (`c:\Users\lucas-tran\Documents\Code\Projects\BTL_CSDL`) và tạo virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn thực thi script, cho phép tạm thời bằng lệnh (chạy với quyền Administrator nếu cần):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```


**2) Cài đặt dependencies**

Trong virtualenv đã active, cài các package cần thiết. Dự án sử dụng ít nhất:
- `mysql-connector-python` (kết nối MySQL)
- `python-dotenv` (tùy chọn, nếu dự án dùng `.env`)

Cài bằng pip:

```powershell
pip install mysql-connector-python python-dotenv
```

(optionally) Tạo `requirements.txt` để dễ cài sau này:

```powershell
pip freeze > requirements.txt
```

Và để cài từ `requirements.txt`:

```powershell
pip install -r requirements.txt
```


**3) Cấu hình cơ sở dữ liệu**

Ứng dụng cần kết nối tới MySQL. Tạo một database và user (ví dụ):

```sql
CREATE DATABASE btl_csdl CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'btl_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON btl_csdl.* TO 'btl_user'@'localhost';
FLUSH PRIVILEGES;
```

Ứng dụng có thể đọc cấu hình DB từ file `.env` (nếu dự án sử dụng `python-dotenv`). Tạo file `.env` ở gốc dự án như sau (mẫu):

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=btl_user
DB_PASSWORD=strong_password
DB_NAME=btl_csdl
```

Nếu dự án cấu hình theo cách khác, kiểm tra file kết nối trong `model/` để xem biến nào cần thiết.


**4) Tạo bảng cần thiết (ví dụ cho Hóa đơn)**

Dưới đây là các câu SQL mẫu cho bảng `HOA_DON` và `CHI_TIET_HOA_DON` mà ứng dụng hóa đơn cần (chỉnh theo schema thực tế nếu khác):

```sql
CREATE TABLE HOA_DON (
    ma_hoa_don VARCHAR(50) PRIMARY KEY,
    ten_khach_hang VARCHAR(255) NOT NULL,
    ngay_gio DATETIME NOT NULL,
    tong_tien DECIMAL(12,2) NOT NULL DEFAULT 0,
    giam_gia DECIMAL(5,2) DEFAULT 0, -- phần trăm
    thanh_tien DECIMAL(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE CHI_TIET_HOA_DON (
    ma_hoa_don VARCHAR(50),
    ma_thuoc VARCHAR(50),
    so_luong INT NOT NULL,
    don_gia DECIMAL(12,2) NOT NULL,
    thanh_tien DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (ma_hoa_don, ma_thuoc),
    FOREIGN KEY (ma_hoa_don) REFERENCES HOA_DON(ma_hoa_don) ON DELETE CASCADE
    -- FOREIGN KEY (ma_thuoc) REFERENCES THUOC(ma_thuoc) -- nếu bảng THUOC tồn tại
);
```

> Ghi chú: Nếu dự án có thêm các bảng như `THUOC`, `LO_HANG_NHAP`, hoặc bảng nhân viên `NHAN_VIEN`, đảm bảo các FK phù hợp hoặc tạm thời bỏ ràng buộc nếu test nhanh.


**5) Chạy ứng dụng**

Trong PowerShell (virtualenv active):

```powershell
python main.py
```

Trình GUI sẽ khởi chạy; menu chính có các mục: `Nhân viên`, `Hóa đơn`. Mở tab `Hóa đơn` để thử chức năng tạo hóa đơn.


**6) Gỡ lỗi nhanh**

- Lỗi kết nối DB: kiểm tra `.env` hoặc tham số kết nối trong `model` folder, đảm bảo MySQL đang chạy và thông tin user/password chính xác.
- Thiếu module: cài `mysql-connector-python` và `python-dotenv` theo bước 2.
- Lỗi Tkinter: Tkinter là module chuẩn, nếu không có hãy cài Python từ python.org (installer chính thức) hoặc xác nhận bản phân phối hỗ trợ Tk.


**7) Cách đóng góp / chỉnh sửa nhanh**
- Mã nguồn chính: `main.py` (entry), các view nằm trong `view/`, logic trong `controller/` và DB access trong `model/`.
- Nếu bạn đổi tên file hay xóa view (ví dụ đã xóa phần quản lý thuốc), kiểm tra `main.py` để loại bỏ import và lời gọi tương ứng.


---

Nếu bạn muốn, tôi có thể tiếp tục và:
- Tạo `requirements.txt` tự động từ môi trường hiện tại.
- Thêm file `.env.example` mẫu vào repository.
- Sinh script SQL để tạo toàn bộ schema dựa trên cấu trúc hiện có trong code.

Bạn muốn tôi làm bước nào tiếp theo không?
