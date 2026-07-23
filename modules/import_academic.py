import pandas as pd

from modules.database import get_connection


REQUIRED_COLUMNS = [
    "Họ Tên",
    "Ngày sinh"
]


def clean_value(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def validate_columns(df):

    headers = [
        str(col).strip()
        for col in df.columns
    ]

    missing = [

        col

        for col in REQUIRED_COLUMNS

        if col not in headers

    ]

    if missing:

        raise ValueError(
            "Thiếu cột bắt buộc: "
            + ", ".join(missing)
        )


def get_student_id(
    conn,
    ho_ten,
    ngay_sinh
):

    return conn.execute(
        """
        SELECT ma_dinh_danh
        FROM students
        WHERE ho_ten = ?
        AND ngay_sinh = ?
        """,
        (
            ho_ten,
            ngay_sinh
        )
    ).fetchone()


def academic_exists(
    conn,
    ma_dinh_danh,
    nam_hoc,
    hoc_ky,
    mon_hoc
):
    return conn.execute(
        """
        SELECT
            id,
            diem_tb,
            ket_qua_hoc_tap,
            ket_qua_ren_luyen
        FROM academic
        WHERE ma_dinh_danh = ?
        AND nam_hoc = ?
        AND hoc_ky = ?
        AND mon_hoc = ?
        """,
        (
            ma_dinh_danh,
            nam_hoc,
            hoc_ky,
            mon_hoc
        )
    ).fetchone()
def save_subject(
    conn,
    ma_dinh_danh,
    nam_hoc,
    hoc_ky,
    mon_hoc,
    diem,
    ket_qua_hoc_tap,
    ket_qua_ren_luyen
):

    if diem == "":
        return False

    diem = str(diem).strip()

    row = academic_exists(
        conn,
        ma_dinh_danh,
        nam_hoc,
        hoc_ky,
        mon_hoc
    )

    # ===========================
    # ĐÃ CÓ DỮ LIỆU
    # ===========================
    if row:

        old_score = "" if row["diem_tb"] is None else str(row["diem_tb"]).strip()

        try:
            same_score = float(old_score) == float(diem)
        except:
            same_score = old_score == diem

        same_ht = (
            (row["ket_qua_hoc_tap"] or "").strip()
            == ket_qua_hoc_tap.strip()
        )

        same_rl = (
            (row["ket_qua_ren_luyen"] or "").strip()
            == ket_qua_ren_luyen.strip()
        )

        if same_score and same_ht and same_rl:
            return "duplicate"

        conn.execute(
            """
            UPDATE academic
            SET
                diem_tb = ?,
                ket_qua_hoc_tap = ?,
                ket_qua_ren_luyen = ?,
                ngay_cap_nhat = datetime('now')
            WHERE id = ?
            """,
            (
                diem,
                ket_qua_hoc_tap,
                ket_qua_ren_luyen,
                row["id"]
            )
        )

        return "updated"

    # ===========================
    # CHƯA CÓ DỮ LIỆU
    # ===========================
    conn.execute(
        """
        INSERT INTO academic
        (
            ma_dinh_danh,
            nam_hoc,
            hoc_ky,
            mon_hoc,
            diem_tb,
            ket_qua_hoc_tap,
            ket_qua_ren_luyen,
            ngay_cap_nhat
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, datetime('now')
        )
        """,
        (
            ma_dinh_danh,
            nam_hoc,
            hoc_ky,
            mon_hoc,
            diem,
            ket_qua_hoc_tap,
            ket_qua_ren_luyen
        )
    )

    return True
def import_academic(file):

    df = pd.read_excel(
        file,
        header=5
    )
# Bỏ các dòng tiêu đề lặp lại trong dữ liệu
    df = df[
    df["Họ Tên"].astype(str).str.strip() != "Họ Tên"
]
    df = df.dropna(
    subset=[
        "Họ Tên",
        "Ngày sinh"
    ]
)
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    validate_columns(df)

    conn = get_connection()

# Kiểm tra đã có dữ liệu học sinh chưa
    student_count = conn.execute(
    "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    if student_count == 0:
        conn.close()
        return {
        "status": "warning",
        "message": "Bạn phải cập nhật danh sách học sinh trước.",
        "total": 0,
        "imported": 0,
        "updated": 0,
        "duplicate": 0,
        "invalid": 0
    }

    total = len(df)

    imported = 0
    updated = 0

    duplicate = 0

    invalid = 0

    subject_mapping = {

    "Toán": "Toán",

    "Ngữ văn": "Ngữ văn",

    "Ngoại ngữ 1": "Ngoại ngữ",

    "GDCD": "GDCD",

    "Công nghệ": "Công nghệ",

    "Tin học": "Tin học",

    "Khoa học Tự nhiên": "Khoa học Tự nhiên",

    "Lịch sử và địa lý": "Lịch sử và Địa lý",

    "Giáo dục thể chất": "Giáo dục thể chất",

    "Nghệ thuật": "Nghệ thuật",

    "HĐTN": "HĐTN",

    "GDĐP": "GDĐP"

}

    for _, row in df.iterrows():

        ho_ten = clean_value(
            row.get("Họ Tên")
        )

        ngay_sinh = clean_value(
            row.get("Ngày sinh")
        )

        if not ho_ten or not ngay_sinh:

            invalid += 1

            continue

        student = get_student_id(
            conn,
            ho_ten,
            ngay_sinh
        )

        if not student:

            print("=" * 60)
            print("Không tìm thấy học sinh")
            print("Họ tên   :", repr(ho_ten))
            print("Ngày sinh:", repr(ngay_sinh))

            student2 = conn.execute(
        """
        SELECT ho_ten, ngay_sinh
        FROM students
        WHERE ho_ten = ?
        """,
            (ho_ten,)
            ).fetchone()

            print("Trong CSDL:", student2)
            print("Ngày sinh Excel :", repr(ngay_sinh))
            print("=" * 60)

            invalid += 1
            continue
        ma_dinh_danh = student[
            "ma_dinh_danh"
        ]

        nam_hoc = clean_value(
            row.get("Năm học")
        )

        hoc_ky = clean_value(
            row.get("Học kỳ")
        )

        ket_qua_hoc_tap = clean_value(
            row.get("Kết quả học tập")
        )

        ket_qua_ren_luyen = clean_value(
            row.get("Kết quả rèn luyện")
        )

        row_has_new_data = False

        row_duplicate = True

        for excel_col, mon_hoc in subject_mapping.items():

            result = save_subject(

                conn,

                ma_dinh_danh,

                nam_hoc,

                hoc_ky,

                mon_hoc,

                clean_value(
                    row.get(excel_col)
                ),

                ket_qua_hoc_tap,

                ket_qua_ren_luyen

            )

            if result is True:

                row_has_new_data = True
                row_duplicate = False

            elif result == "updated":

                updated += 1
                row_duplicate = False

            elif result == "duplicate":

                pass

            elif result is False:

                pass

        if row_has_new_data:

            imported += 1

        elif row_duplicate:

            duplicate += 1

    conn.commit()

    conn.close()
    print(df[df["Họ Tên"].isna() | df["Ngày sinh"].isna()])
    return {
    "status": "success",
    "message": f"Đã nhập: {imported}, Cập nhật: {updated}, Trùng: {duplicate}",
    "total": total,
    "imported": imported,
    "updated": updated,
    "duplicate": duplicate,
    "invalid": invalid
}
def safe_import_academic(file):

    try:

        return import_academic(file)

    except ValueError as e:

        return {

            "status": "danger",

            "message": "Mẫu Excel không hợp lệ.",

            "error": str(e),

            "total": 0,

            "imported": 0,

            "updated": 0,

            "duplicate": 0,

            "invalid": 0

        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {

            "status": "danger",

            "message": "Lỗi khi nhập dữ liệu học tập.",

            "error": str(e),

            "total": 0,

            "imported": 0,

            "updated": 0,

            "duplicate": 0,

            "invalid": 0

        }