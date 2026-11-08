# HƯỚNG DẪN SETUP PROJECT

## BACKEND

### 1. Cài đặt PostgreSQL 18

Chỉnh sửa port và mật khẩu postgres tùy ý

### 2. Tạo database student_performance

### 3. Tạo env.json

Trong thư mục gốc của repo (có chứa README.md này), tạo file `repo.json` với template như sau:

```json
{
    "dbname": "student_performance",
    "user": "postgres",
    "password": "<mật khẩu đã tạo>",
    "host": "localhost",
    "port": "<5432 hoặc port đã tạo>"
}
```

### 4. Cài dependency cho Backend

```py
python -m pip install -r requirements.txt
```

### 5. Chạy bootstrap

**‼️LỆNH SẼ XOÁ MỌI SCHEMA VÀ BẢNG TRONG DATABASE student_performance ĐỂ NHẬP LẠI DỮ LIỆU!!!**

Ở thư mục gốc của repo (có chứa README.md này), chạy lệnh sau:

```py
python -m db.bootstrap.run
```

### 5. Chạy backend [Hướng dẫn API](backend/API.md)

```py
python -m backend.server
```

## FRONTEND

TODO
