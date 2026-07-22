import pandas as pd
import re

from modules.database import get_connection


REQUIRED_COLUMNS = [

    "Mã định danh",

    "Họ tên",

    "Ngày sinh",

    "Giới tính",

    "Dân tộc",

    "Trạng thái"

]


def clean_value(value):

    if pd.isna(value):

        return ""

    return str(value).strip()
def get_class_name(file):

    file.seek(0)

    title = pd.read_excel(
        file,
        header=None,
        nrows=4
    )

    file.seek(0)

    text = " ".join(
        str(x)
        for x in title.fillna("").values.flatten()
    )

    m = re.search(
        r"LỚP\s+([0-9A-Za-z]+)",
        text,
        re.IGNORECASE
    )

    if m:
        return m.group(1).strip()

    return ""

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


def student_exists(

    conn,

    ma_dinh_danh

):

    row = conn.execute(

        """
        SELECT id
        FROM students
        WHERE ma_dinh_danh = ?
        """,

        (ma_dinh_danh,)

    ).fetchone()

    return row is not None
def import_students(file):

    df = pd.read_excel(
        file,
        header=5
    )
    file.seek(0)

    lop = get_class_name(file)
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    validate_columns(df)

    conn = get_connection()

    total = 0

    imported = 0

    duplicate = 0

    invalid = 0

    duplicate_list = []

    invalid_list = []

    for index, row in df.iterrows():

        value = row.get("Mã định danh")

        if pd.isna(value):
            ma_dinh_danh = ""
        else:
            ma_dinh_danh = str(int(float(value)))

        ho_ten = clean_value(
            row.get("Họ tên")
        )

        ngay_sinh = clean_value(
            row.get("Ngày sinh")
        )

        gioi_tinh = clean_value(
            row.get("Giới tính")
        )

        dan_toc = clean_value(
            row.get("Dân tộc")
        )

        trang_thai = clean_value(
            row.get("Trạng thái")
        )

        if not ma_dinh_danh and not ho_ten:

            continue

        total += 1

        noi_sinh = ""

        dia_chi = ""

    
        if not ma_dinh_danh:

            invalid += 1

            invalid_list.append(

                f"Dòng {index + 7}: thiếu mã định danh"

            )

            continue

        if not ho_ten:

            invalid += 1

            invalid_list.append(

                f"Dòng {index + 7}: thiếu họ tên"

            )

            continue

        if student_exists(
            conn,
            ma_dinh_danh
        ):

            duplicate += 1

            duplicate_list.append(

                f"{ma_dinh_danh} - {ho_ten}"

            )

            continue

        conn.execute(
            """
            INSERT INTO students
            (
                ma_dinh_danh,
                ho_ten,
                ngay_sinh,
                gioi_tinh,
                dan_toc,
                noi_sinh,
                dia_chi,
                lop,
                trang_thai,
                ngay_cap_nhat
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                datetime('now')
            )
            """,
            (
                ma_dinh_danh,
                ho_ten,
                ngay_sinh,
                gioi_tinh,
                dan_toc,
                noi_sinh,
                dia_chi,
                lop,
                trang_thai
            )
        )

        imported += 1
    file.seek(0)
# ==========================
# TỰ ĐỘNG TẠO LỚP HỌC
# ==========================

    if lop:

            conn.execute(
                """
                INSERT OR IGNORE INTO classes
                (
                ten_lop,
                gvcn,
                nam_hoc,
                trang_thai
                )
                VALUES
                (
                ?, ?, ?, ?
                )
                """,
                (
                    lop,
                    "Nguyễn Thanh Tuấn",
                    "2026-2027",
                    1
                )
            )
    # ==========================
# LƯU LỊCH SỬ NHẬP LIỆU
# ==========================

    conn.execute(
    """
    INSERT INTO import_history
(
    ten_tep,
    loai_du_lieu,
    so_ban_ghi,
    nguoi_nhap,
    trang_thai,
    thoi_gian
)
VALUES
(
    ?, ?, ?, ?, ?,
    datetime('now','+7 hours')
)
    """,
    (
        file.filename,
        "Danh sách học sinh",
        imported,
        "Nguyễn Thanh Tuấn",
        "Thành công"
    )
)
    conn.commit()

    conn.close()

    return {

        "status": "success",

        "message":
            f"Đã nhập {imported}/{total} học sinh.",

        "total":
            total,

        "imported":
            imported,

        "updated":
            0,

        "duplicate":
            duplicate,

        "invalid":
            invalid,

        "duplicate_list":
            duplicate_list,

        "invalid_list":
            invalid_list

    }


def safe_import_students(file):

    try:

        return import_students(file)

    except ValueError as e:

        return {

        "status": "danger",

        "message": str(e),

        "error": str(e),

            "total": 0,

            "imported": 0,

            "updated": 0,

            "duplicate": 0,

            "invalid": 0,

            "duplicate_list": [],

            "invalid_list": []

        }

    except Exception as e:

        return {

            "status": "danger",

            "message": "Lỗi khi nhập dữ liệu học sinh.",

            "error": str(e),

            "total": 0,

            "imported": 0,

            "updated": 0,

            "duplicate": 0,

            "invalid": 0,

            "duplicate_list": [],

            "invalid_list": []

        }