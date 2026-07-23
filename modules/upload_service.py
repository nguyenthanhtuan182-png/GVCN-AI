import pandas as pd

from modules.import_students import safe_import_students
from modules.import_academic import safe_import_academic
from modules.import_gvcn import safe_import_gvcn


# =====================================================
# CẤU HÌNH
# =====================================================

ALLOWED_EXTENSIONS = {
    "xlsx",
    "xls"
}


# =====================================================
# KIỂM TRA ĐUÔI FILE
# =====================================================

def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(".", 1)[1].lower()

        in ALLOWED_EXTENSIONS

    )


# =====================================================
# ĐỌC HEADER
# =====================================================

def get_headers(file, header_row):

    file.seek(0)

    df = pd.read_excel(

        file,

        header=header_row,

        nrows=0

    )

    headers = [

        str(col).strip()

        for col in df.columns

    ]

    file.seek(0)

    return headers


# =====================================================
# NHẬN DẠNG FILE
# =====================================================

def detect_template(file):

    # ------------------------------------
    # FILE CSDL
    # ------------------------------------

    try:

        headers = set(

            get_headers(

                file,

                5

            )

        )

        # -------------------------------
        # DANH SÁCH HỌC SINH
        # -------------------------------

        if (

            "Mã định danh" in headers

            and

            "Giới tính" in headers

            and

            "Dân tộc" in headers

            and

            "Trạng thái" in headers

        ):

            return "students"

        # -------------------------------
        # KẾT QUẢ HỌC TẬP
        # -------------------------------

        if (

            "Họ Tên" in headers

            and

            "Ngày sinh" in headers

            and

            "Kết quả học tập" in headers

            and

            "Kết quả rèn luyện" in headers

        ):

            return "academic"

    except Exception:

        pass

    # ------------------------------------
    # FILE GVCN
    # ------------------------------------

    try:

        headers = set(

            get_headers(

                file,

                0

            )

        )

        if (

            "Mã định danh" in headers

            and

            "Họ tên" in headers

            and

            "Lớp" in headers

            and

            "Ghi chú GVCN" in headers

        ):

            return "gvcn"

    except Exception:

        pass

    return None


# =====================================================
# DANH SÁCH HÀM IMPORT
# =====================================================

def get_handlers():

    return {

        "students":

            safe_import_students,

        "academic":

            safe_import_academic,

        "gvcn":

            safe_import_gvcn

    }


# =====================================================
# KẾT QUẢ MẶC ĐỊNH
# =====================================================

def empty_result(message=""):

    return {

        "status": "info",

        "message": message,

        "total": 0,

        "imported": 0,

        "updated": 0,

        "duplicate": 0,

        "invalid": 0,

        "error": None

    }
# =====================================================
# CHUẨN HÓA KẾT QUẢ
# =====================================================

def normalize_result(result):

    default = empty_result()

    default.update(result)

    return default


# =====================================================
# XỬ LÝ UPLOAD
# =====================================================

def process_upload(file):

    try:

        # --------------------------------
        # Kiểm tra file
        # --------------------------------

        if not file:

            return {

                **empty_result(),

                "status": "danger",

                "message": "Chưa chọn tệp Excel."

            }

        if file.filename == "":

            return {

                **empty_result(),

                "status": "danger",

                "message": "Chưa chọn tệp Excel."

            }

        if not allowed_file(file.filename):

            return {

                **empty_result(),

                "status": "danger",

                "message": "Chỉ hỗ trợ tệp Excel (*.xlsx, *.xls)."

            }

        # --------------------------------
        # Nhận dạng loại file
        # --------------------------------

        template = detect_template(file)

        if template is None:

            return {

                **empty_result(),

                "status": "danger",

                "message": "Không nhận dạng được mẫu Excel."

            }

        # --------------------------------
        # Lấy hàm xử lý
        # --------------------------------

        handlers = get_handlers()

        handler = handlers.get(template)

        if handler is None:

            return {

                **empty_result(),

                "status": "danger",

                "message": "Chưa hỗ trợ loại dữ liệu này."

            }

        # --------------------------------
        # Đưa con trỏ file về đầu
        # --------------------------------

        file.seek(0)

        # --------------------------------
        # Thực hiện import
        # --------------------------------

        result = handler(file)

        # --------------------------------
        # Chuẩn hóa kết quả
        # --------------------------------

        return normalize_result(result)

    except ValueError as e:

        return {

            **empty_result(),

            "status": "danger",

            "message": str(e)

        }

    except Exception as e:

        return {

            **empty_result(),

            "status": "danger",

            "message": f"Lỗi xử lý dữ liệu: {str(e)}"

        }