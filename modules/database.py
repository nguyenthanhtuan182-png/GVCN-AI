import sqlite3

DATABASE = "database/gvcn_ai.db"


def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_database():

    conn = get_connection()

    cur = conn.cursor()

    # ==========================
    # STUDENTS
    # ==========================

    cur.execute("""

    CREATE TABLE IF NOT EXISTS students(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ma_dinh_danh TEXT UNIQUE,

        ho_ten TEXT,

        ngay_sinh TEXT,

        gioi_tinh TEXT,

        dan_toc TEXT,

        noi_sinh TEXT,

        dia_chi TEXT,

        lop TEXT,

        trang_thai TEXT,

        ngay_cap_nhat TEXT

    )

    """)
# ==========================
# BẢNG LỚP HỌC
# ==========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS classes (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ten_lop TEXT UNIQUE NOT NULL,

        gvcn TEXT,

        nam_hoc TEXT,

        trang_thai INTEGER DEFAULT 1,

        ghi_chu TEXT,

        ngay_cap_nhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)
    # ==========================
    # ACADEMIC
    # ==========================

    cur.execute("""

    CREATE TABLE IF NOT EXISTS academic(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ma_dinh_danh TEXT,

        nam_hoc TEXT,

        hoc_ky TEXT,

        mon_hoc TEXT,

        diem_tb REAL,

        ket_qua_hoc_tap TEXT,

        ket_qua_ren_luyen TEXT,

        ngay_cap_nhat TEXT,

        FOREIGN KEY(ma_dinh_danh)

        REFERENCES students(ma_dinh_danh)

    )

    """)
    # ==========================
    # ATTENDANCE
    # ==========================

    cur.execute("""

    CREATE TABLE IF NOT EXISTS attendance(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ma_dinh_danh TEXT,

        ngay TEXT,

        tiet INTEGER,

        trang_thai TEXT,

        ghi_chu TEXT,

        FOREIGN KEY(ma_dinh_danh)

        REFERENCES students(ma_dinh_danh)

    )

    """)

    # ==========================
    # CONDUCT
    # ==========================

    cur.execute("""

    CREATE TABLE IF NOT EXISTS conduct(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ma_dinh_danh TEXT,

        ngay TEXT,

        noi_dung TEXT,

        diem INTEGER,

        ghi_chu TEXT,

        FOREIGN KEY(ma_dinh_danh)

        REFERENCES students(ma_dinh_danh)

    )

    """)

# ==========================
# PARENTS
# ==========================

    cur.execute("""

    CREATE TABLE IF NOT EXISTS parents(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ma_dinh_danh TEXT,

    ho_ten TEXT,

    quan_he TEXT,

    dien_thoai TEXT,

    nghe_nghiep TEXT,

    FOREIGN KEY(ma_dinh_danh)

    REFERENCES students(ma_dinh_danh)

)

""")

# ==========================
# IMPORT HISTORY
# ==========================

    cur.execute("""

    CREATE TABLE IF NOT EXISTS import_history(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ten_tep TEXT,

    loai_du_lieu TEXT,

    so_ban_ghi INTEGER,

    nguoi_nhap TEXT,

    trang_thai TEXT,

    thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

""")

    conn.commit()

    conn.close()