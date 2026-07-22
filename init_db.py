import sqlite3

conn = sqlite3.connect("database/gvcn_ai.db")
cursor = conn.cursor()

# ==========================
# Bảng học sinh
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ho_ten TEXT NOT NULL,
    lop TEXT,
    gioi_tinh TEXT,
    ngay_sinh TEXT,
    dia_chi TEXT,
    sdt_phu_huynh TEXT,

    hoc_luc TEXT,
    hanh_kiem TEXT,

    nguy_co INTEGER DEFAULT 0

)
""")

# ==========================
# Kết quả học tập
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS academic_results (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    hoc_ky TEXT,
    nam_hoc TEXT,
    diem_tb REAL,
    hoc_luc TEXT,
    xep_hang INTEGER,

    FOREIGN KEY(student_id) REFERENCES students(id)

)
""")

# ==========================
# Chuyên cần
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    nam_hoc TEXT,
    vang_co_phep INTEGER DEFAULT 0,
    vang_khong_phep INTEGER DEFAULT 0,
    di_muon INTEGER DEFAULT 0,

    FOREIGN KEY(student_id) REFERENCES students(id)

)
""")

# ==========================
# Hạnh kiểm
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS conduct (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    nam_hoc TEXT,
    hanh_kiem TEXT,
    vi_pham INTEGER DEFAULT 0,
    ghi_chu TEXT,

    FOREIGN KEY(student_id) REFERENCES students(id)

)
""")

# ==========================
# Phụ huynh
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS parents (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    ho_ten TEXT,
    so_dien_thoai TEXT,
    nghe_nghiep TEXT,
    dia_chi TEXT,

    FOREIGN KEY(student_id) REFERENCES students(id)

)
""")

# ==========================
# Lịch sử import
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS import_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loai_du_lieu TEXT,
    ten_file TEXT,
    thoi_gian TEXT,
    so_ban_ghi INTEGER,
    trang_thai TEXT

)
""")

# ==========================
# AI phân tích
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_analysis (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    risk_score REAL,
    risk_level TEXT,
    prediction TEXT,
    recommendation TEXT,
    analysis_time TEXT,

    FOREIGN KEY(student_id) REFERENCES students(id)

)
""")

conn.commit()
conn.close()

print("Đã tạo cơ sở dữ liệu thành công!")