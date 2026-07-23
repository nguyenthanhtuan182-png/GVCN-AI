import pandas as pd

from modules.database import get_connection


REQUIRED_COLUMNS = [

    "Mã định danh",

    "Họ tên",

    "Lớp",

    "Ghi chú GVCN",

    "Hoàn cảnh đặc biệt",

    "Tình hình gia đình",

    "Đã liên hệ PH",

    "Nội dung trao đổi PH",

    "Ghi chú khác"

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


def note_exists(

    conn,

    ma_dinh_danh

):

    row = conn.execute(

        """

        SELECT id

        FROM teacher_notes

        WHERE ma_dinh_danh = ?

        """,

        (ma_dinh_danh,)

    ).fetchone()

    return row is not None


def import_gvcn(file):

    df = pd.read_excel(file)

    df.columns = (

        df.columns

        .astype(str)

        .str.strip()

    )

    validate_columns(df)

    conn = get_connection()

    total = 0

    imported = 0

    updated = 0

    duplicate = 0

    invalid = 0

    duplicate_list = []

    invalid_list = []

    for index, row in df.iterrows():

        ma_dinh_danh = clean_value(

            row.get("Mã định danh")

        )

        ho_ten = clean_value(

            row.get("Họ tên")

        )

        lop = clean_value(

            row.get("Lớp")

        )

        ghi_chu_gvcn = clean_value(

            row.get("Ghi chú GVCN")

        )

        hoan_canh_dac_biet = clean_value(

            row.get("Hoàn cảnh đặc biệt")

        )

        tinh_hinh_gia_dinh = clean_value(

            row.get("Tình hình gia đình")

        )

        da_lien_he_ph = clean_value(

            row.get("Đã liên hệ PH")

        )

        noi_dung_trao_doi_ph = clean_value(

            row.get("Nội dung trao đổi PH")

        )

        ghi_chu_khac = clean_value(

            row.get("Ghi chú khác")

        )

        if not ma_dinh_danh and not ho_ten:

            continue

        total += 1

        if not ma_dinh_danh:

            invalid += 1

            invalid_list.append(

                f"Dòng {index + 2}: thiếu mã định danh"

            )

            continue

        student = conn.execute(

            """

            SELECT id

            FROM students

            WHERE ma_dinh_danh = ?

            """,

            (ma_dinh_danh,)

        ).fetchone()

        if student is None:

            invalid += 1

            invalid_list.append(

                f"{ma_dinh_danh} - Không tồn tại"

            )

            continue

        if not note_exists(

            conn,

            ma_dinh_danh

        ):

            conn.execute(

                """

                INSERT INTO teacher_notes

                (

                    ma_dinh_danh,

                    ghi_chu_gvcn,

                    hoan_canh_dac_biet,

                    tinh_hinh_gia_dinh,

                    da_lien_he_ph,

                    noi_dung_trao_doi_ph,

                    ghi_chu_khac,

                    ngay_cap_nhat

                )

                VALUES

                (

                    ?,?,?,?,?,?,?,

                    datetime('now','+7 hours')

                )

                """,

                (

                    ma_dinh_danh,

                    ghi_chu_gvcn,

                    hoan_canh_dac_biet,

                    tinh_hinh_gia_dinh,

                    da_lien_he_ph,

                    noi_dung_trao_doi_ph,

                    ghi_chu_khac

                )

            )

            imported += 1

        else:

            old = conn.execute(

                """

                SELECT *

                FROM teacher_notes

                WHERE ma_dinh_danh = ?

                """,

                (ma_dinh_danh,)

            ).fetchone()

            if (

                old["ghi_chu_gvcn"] == ghi_chu_gvcn and

                old["hoan_canh_dac_biet"] == hoan_canh_dac_biet and

                old["tinh_hinh_gia_dinh"] == tinh_hinh_gia_dinh and

                old["da_lien_he_ph"] == da_lien_he_ph and

                old["noi_dung_trao_doi_ph"] == noi_dung_trao_doi_ph and

                old["ghi_chu_khac"] == ghi_chu_khac

            ):

                duplicate += 1

                duplicate_list.append(

                    f"{ma_dinh_danh} - {ho_ten}"

                )

            else:

                conn.execute(

                    """

                    UPDATE teacher_notes

                    SET

                        ghi_chu_gvcn=?,

                        hoan_canh_dac_biet=?,

                        tinh_hinh_gia_dinh=?,

                        da_lien_he_ph=?,

                        noi_dung_trao_doi_ph=?,

                        ghi_chu_khac=?,

                        ngay_cap_nhat=datetime('now','+7 hours')

                    WHERE ma_dinh_danh=?

                    """,

                    (

                        ghi_chu_gvcn,

                        hoan_canh_dac_biet,

                        tinh_hinh_gia_dinh,

                        da_lien_he_ph,

                        noi_dung_trao_doi_ph,

                        ghi_chu_khac,

                        ma_dinh_danh

                    )

                )

                updated += 1

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

            "Thông tin GVCN",

            imported + updated,

            "Nguyễn Thanh Tuấn",

            "Thành công"

        )

    )

    conn.commit()

    conn.close()

    return {

        "status": "success",

        "message": f"Đã xử lý {imported + updated}/{total} bản ghi.",

        "total": total,

        "imported": imported,

        "updated": updated,

        "duplicate": duplicate,

        "invalid": invalid,

        "duplicate_list": duplicate_list,

        "invalid_list": invalid_list

    }


def safe_import_gvcn(file):

    try:

        return import_gvcn(file)

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

            "message": "Lỗi khi nhập dữ liệu GVCN.",

            "error": str(e),

            "total": 0,

            "imported": 0,

            "updated": 0,

            "duplicate": 0,

            "invalid": 0,

            "duplicate_list": [],

            "invalid_list": []

        }