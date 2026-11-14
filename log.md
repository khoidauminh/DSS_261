# LOGS

Thông tin chung về công việc BTL.

## Bảng chia công việc (DRAFT)

| Thành viên | Công việc |
| - | - |
| Đậu Minh Khôi | Backend, bootstrap SQL |
| Nguyễn Đình Khôi | Frontend, DSS |
| Lê Minh Khoa | Frontend, DSS |

## Nhật ký

| Status | Công việc | Ghi chú |
| :-: | - | - |
| ✅ | Tìm dataset | [Predict Students' Dropout and Academic Success](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success) |
| ✅ | Chọn tech stack | Flask (Python), psycopg2-binary (PostgreSQL) |
| ✅ | Tạo schema | Snowflake schema (Deduplicated Dimensions) |
| ✅ | Viết script bootstrap | `db/bootstrap/run.py` & `bootstrap.sql` |
| ✅ | Viết ETL | Extract, Clean, Deduplicate Dimensions & Load |
| ✅ | Chọn tech DSS | L2-Regularized Logistic Regression + What-If Simulation Engine |
| ✅ | Xây dựng DSS & OLAP Cube | `/records/olap/cube`, `/dss/predict`, `/dss/early-warning`, `/dss/model-info` |
| ✅ | Xây dựng Frontend Dashboard | `frontend/index.html` + `frontend/app.js` (TailwindCSS + Chart.js) |
