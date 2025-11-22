# Bài tập lớn môn CSDL (Quản lí hệ thống nhà thuốc)

## Giới thiệu dự án 
...
## Cài đặt 
1. Clone repo về máy 
```bash
git clone https://github.com/lucas-tran05/BTL_CSDL.git
cd BTL_CSDL
```

2. Tạo file ``.env`` với các trường như ``.env.example``
```text
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
```

3. Cài đặt môi trường
```bash
pip install -r requirements.txt
```

4. Tạo 1 db với lệnh tạo bảng qua link 
[Link create table](https://docs.google.com/document/d/1uiwMN9kMGDCypo8SoTqHyuk_lFsSRh4-MgDHGx2NCYc/edit?tab=t.0)

5. Chạy dự án:
```bash
python main.py 
```