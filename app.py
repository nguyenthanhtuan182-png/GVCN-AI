
from modules.sort_helper import sort_students
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    send_file,
    send_from_directory
)

import os

from modules.database import (
    get_connection,
    init_database
)

from modules.upload_service import process_upload


app = Flask(__name__)

app.secret_key = "gvcn_ai_2026"

init_database()


# ==========================
# ĐĂNG NHẬP
# ==========================

@app.route("/")
def login():

    return render_template(
        "login.html"
    )


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html",
        page_title="Bảng điều khiển",
        active_page="dashboard"
    )

# ==========================
# QUẢN LÝ HỌC SINH
# ==========================

@app.route("/students")
def students():

    conn = get_connection()

    students = conn.execute("""
        SELECT *
        FROM students
    """).fetchall()

    conn.close()

    students = sort_students(students)

    return render_template(
        "students.html",
        students=students,
        page_title="Quản lý học sinh",
        active_page="students"
    )
# ==========================
# QUẢN LÝ KẾT QUẢ
# ==========================
@app.route("/academic")
def academic():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            s.ma_dinh_danh,
            s.ho_ten,
            s.lop,
            a.mon_hoc,
            a.diem_tb,
            a.ket_qua_hoc_tap,
            a.ket_qua_ren_luyen
        FROM students s
        LEFT JOIN academic a
            ON s.ma_dinh_danh = a.ma_dinh_danh
    """).fetchall()

    conn.close()

    students = {}

    for row in rows:

        ma = row["ma_dinh_danh"]

        if ma not in students:

            students[ma] = {

                "ma_dinh_danh": row["ma_dinh_danh"],
                "ho_ten": row["ho_ten"],
                "lop": row["lop"],

                "Toán": "",
                "Ngữ văn": "",
                "Ngoại ngữ": "",
                "GDCD": "",
                "Công nghệ": "",
                "Tin học": "",
                "Khoa học Tự nhiên": "",
                "Lịch sử và Địa lý": "",
                "Giáo dục thể chất": "",
                "Nghệ thuật": "",
                "HĐTN": "",
                "GDĐP": "",

                "ket_qua_hoc_tap": "",
                "ket_qua_ren_luyen": ""

            }

        if row["mon_hoc"]:

            students[ma][row["mon_hoc"]] = row["diem_tb"]

            students[ma]["ket_qua_hoc_tap"] = row["ket_qua_hoc_tap"] or ""

            students[ma]["ket_qua_ren_luyen"] = row["ket_qua_ren_luyen"] or ""

    academic = sort_students(list(students.values()))

    return render_template(
        "academic.html",
        academic=academic,
        page_title="Kết quả học tập",
        active_page="academic"
    )
# ==========================

# THÊM HỌC SINH
# ==========================

@app.route("/students/add")
def add_student():

    flash(
        "Phiên bản hiện tại sử dụng nhập liệu từ Excel.",
        "warning"
    )

    return redirect(
        "/students"
    )


# ==========================
# SỬA HỌC SINH
# ==========================

@app.route("/students/edit/<int:id>")
def edit_student(id):

    flash(
        "Chức năng đang được nâng cấp.",
        "warning"
    )

    return redirect(
        "/students"
    )


# ==========================
# XÓA HỌC SINH
# ==========================

@app.route("/students/delete/<int:id>")
def delete_student(id):

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM students
        WHERE id = ?
        """,
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect(
        "/students"
    )


# ==========================
# QUẢN LÝ LỚP HỌC
# ==========================
@app.route("/classes")
def classes():

    conn = get_connection()

    # Thống kê
    total_students = conn.execute("""
        SELECT COUNT(*)
        FROM students
    """).fetchone()[0]

    total_classes = conn.execute("""
        SELECT COUNT(DISTINCT lop)
        FROM students
        WHERE lop IS NOT NULL
        AND lop <> ''
    """).fetchone()[0]

   # Danh sách lớp
    classes = conn.execute("""
SELECT

    c.id,

    c.ten_lop,

    c.gvcn,

    c.nam_hoc,

    c.trang_thai,

    COUNT(s.id) AS si_so,

    SUM(
        CASE
            WHEN s.gioi_tinh='Nam'
            THEN 1
            ELSE 0
        END
    ) AS nam,

    SUM(
        CASE
            WHEN s.gioi_tinh='Nữ'
            THEN 1
            ELSE 0
        END
    ) AS nu

FROM classes c

LEFT JOIN students s

ON s.lop = c.ten_lop

GROUP BY

    c.id,
    c.ten_lop,
    c.gvcn,
    c.nam_hoc,
    c.trang_thai

ORDER BY c.ten_lop

""").fetchall()

    conn.close()

    return render_template(

        "classes.html",

        classes=classes,

        total_classes=total_classes,

        total_students=total_students,

        attendance_rate=0,

        page_title="Quản lý lớp học",

        active_page="classes"

    )

# ==========================
# CẬP NHẬT / THÊM LỚP HỌC
# ==========================
@app.route("/classes/update", methods=["POST"])
def update_class():

    old_class = request.form.get("old_class", "").strip()
    new_class = request.form.get("new_class", "").strip()
    teacher = request.form.get("teacher_name", "").strip()
    status = request.form.get("class_status", "1")

    if new_class == "":
        return {"success": False, "message": "Tên lớp không được để trống"}

    conn = get_connection()

    if old_class == "":

        conn.execute("""
            INSERT INTO classes
            (
                ten_lop,
                gvcn,
                nam_hoc,
                trang_thai
            )
            VALUES
            (?, ?, ?, ?)
        """,
        (
            new_class,
            teacher,
            "2026-2027",
            status
        ))

    else:

        conn.execute("""
            UPDATE classes
            SET
                ten_lop = ?,
                gvcn = ?,
                trang_thai = ?
            WHERE ten_lop = ?
        """,
        (
            new_class,
            teacher,
            status,
            old_class
        ))

    conn.commit()
    conn.close()

    return {"success": True}
# ==========================
# XÓA LỚP HỌC
# ==========================
@app.route("/classes/delete", methods=["POST"])
def delete_class():

    class_name = request.form.get("class_name", "").strip()

    conn = get_connection()

    # Kiểm tra còn học sinh không
    row = conn.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE lop = ?
    """, (class_name,)).fetchone()

    if row[0] > 0:

        conn.close()

        return {
            "success": False,
            "message": "Không thể xóa. Lớp vẫn còn học sinh."
        }

    # Xóa lớp
    conn.execute("""
        DELETE FROM classes
        WHERE ten_lop = ?
    """, (class_name,))

    conn.commit()

    conn.close()

    return {
        "success": True,
        "message": "Đã xóa lớp học."
    }
# ==========================
# NHẬP DỮ LIỆU
# ==========================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    stats = {

        "total": 0,

        "imported": 0,

        "updated": 0,

        "duplicate": 0,

        "invalid": 0

    }

    conn = get_connection()

    if request.method == "POST":

        file = request.files.get("file")

        result = process_upload(file)

        flash(

            result.get(
                "message",
                "Hoàn thành nhập dữ liệu."
            ),

            result.get(
                "status",
                "info"
            )

        )

        stats = {

            "total": result.get("total", 0),

            "imported": result.get("imported", 0),

            "updated": result.get("updated", 0),

            "duplicate": result.get("duplicate", 0),

            "invalid": result.get("invalid", 0)

        }

    # ==========================
# LỊCH SỬ NHẬP DỮ LIỆU
# ==========================

    history = conn.execute("""
SELECT

    ten_tep,

    loai_du_lieu,

    so_ban_ghi,

    nguoi_nhap,

    trang_thai,

    thoi_gian

FROM import_history

ORDER BY id DESC

LIMIT 20

""").fetchall()

    conn.close()

    return render_template(

        "upload.html",

        stats=stats,

        history=history,

        page_title="Nhập dữ liệu",

        active_page="upload"

    )
# ==========================
# XÓA LỊCH SỬ NHẬP LIỆU
# ==========================

@app.route("/upload/history/clear", methods=["POST"])
def clear_upload_history():

    conn = get_connection()

    conn.execute("DELETE FROM import_history")

    conn.commit()

    conn.close()

    flash(

        "Đã xóa toàn bộ lịch sử nhập liệu.",

        "success"

    )

    return redirect("/upload")
# ==========================
# AI PHÂN TÍCH
# ==========================

@app.route("/ai")
def ai():

    return render_template(
        "ai.html",
        page_title="AI phân tích",
        active_page="ai"
    )


# ==========================
# BẢN ĐỒ HỌC SINH
# ==========================

@app.route("/map")
def map_page():

    return render_template(
        "map.html",
        page_title="Bản đồ học sinh",
        active_page="map"
    )


# ==========================
# BÁO CÁO
# ==========================

@app.route("/reports")
def reports():

    return render_template(
        "reports.html",
        page_title="Báo cáo",
        active_page="reports"
    )
# ==========================
# CÀI ĐẶT
# ==========================

@app.route("/settings")
def settings():

    return render_template(
        "settings.html",
        page_title="Cài đặt",
        active_page="settings"
    )


# ==========================
# TẢI FILE MẪU
# ==========================

@app.route("/download-template/students")
def download_students_template():

    return send_file(
        "static/templates_excel/students_template.xlsx",
        as_attachment=True
    )


@app.route("/download-template/<data_type>")
def download_template(data_type):

    files = {

        "students":
            "students_template.xlsx",

        "academic":
            "academic_template.xlsx",

        "attendance":
            "attendance_template.xlsx",

        "conduct":
            "conduct_template.xlsx",

        "parents":
            "parents_template.xlsx",

        "survey":
            "survey_template.xlsx",

        "gvcn":
            "gvcn_template.xlsx"

    }

    filename = files.get(
        data_type
    )

    if not filename:

        return (
            "Không tìm thấy file mẫu",
            404
        )

    return send_from_directory(

        os.path.join(
            app.root_path,
            "static",
            "templates_excel"
        ),

        filename,

        as_attachment=True

    )


# ==========================
# API THỐNG KÊ HỌC SINH
# ==========================

@app.route("/api/students/count")
def api_students_count():

    conn = get_connection()

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        """
    ).fetchone()[0]

    conn.close()

    return {
        "total": total
    }


# ==========================
# API THỐNG KÊ HỌC TẬP
# ==========================

@app.route("/api/academic/count")
def api_academic_count():

    conn = get_connection()

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM academic
        """
    ).fetchone()[0]

    conn.close()

    return {
        "total": total
    }
# ==========================
# API THỐNG KÊ THEO LỚP
# ==========================

@app.route("/api/classes")
def api_classes():

    conn = get_connection()

    data = conn.execute(
        """
        SELECT

            lop,

            COUNT(*) AS so_luong

        FROM students

        GROUP BY lop

        ORDER BY lop

        """
    ).fetchall()

    conn.close()

    result = []

    for row in data:

        result.append({

            "lop": row["lop"],

            "so_luong": row["so_luong"]

        })

    return result


# ==========================
# API THỐNG KÊ GIỚI TÍNH
# ==========================

@app.route("/api/gender")
def api_gender():

    conn = get_connection()

    data = conn.execute(
        """
        SELECT

            gioi_tinh,

            COUNT(*) AS so_luong

        FROM students

        GROUP BY gioi_tinh
        """
    ).fetchall()

    conn.close()

    result = []

    for row in data:

        result.append({

            "gioi_tinh": row["gioi_tinh"],

            "so_luong": row["so_luong"]

        })

    return result


# ==========================
# CHẠY CHƯƠNG TRÌNH
# ==========================

import os

if __name__ == "__main__":

    init_database()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )