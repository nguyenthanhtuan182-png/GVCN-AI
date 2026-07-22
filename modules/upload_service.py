import pandas as pd

from modules.import_students import safe_import_students
from modules.import_academic import safe_import_academic


ALLOWED_EXTENSIONS = {
    "xlsx",
    "xls"
}


REQUIRED_HEADERS = {

    "students": [
        "Mã định danh",
        "Họ tên"
    ],

    "academic": [
        "Họ Tên",
        "Ngày sinh",
        "Kết quả học tập"
    ],

    "gvcn": [
        "Họ và tên",
        "Ngày sinh"
    ]

}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def get_headers(file):

    file.seek(0)

    try:

        df = pd.read_excel(
            file,
            header=5,
            nrows=0
        )

    except Exception:

        file.seek(0)

        df = pd.read_excel(
            file,
            nrows=0
        )

    file.seek(0)

    return [
        str(col).strip()
        for col in df.columns
    ]


def detect_template(headers):

    headers = set(headers)

    if set(REQUIRED_HEADERS["students"]).issubset(headers):
        return "students"

    if set(REQUIRED_HEADERS["academic"]).issubset(headers):
        return "academic"

    if set(REQUIRED_HEADERS["gvcn"]).issubset(headers):
        return "gvcn"

    return None


def get_handlers():

    return {

        "students":
            safe_import_students,

        "academic":
            safe_import_academic,

        # Sau này bổ sung
        # "gvcn":
        #     safe_import_gvcn

    }
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


def normalize_result(result):

    default = empty_result()

    default.update(result)

    return default
def process_upload(file):

    try:

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

        headers = get_headers(file)

        template = detect_template(headers)

        if template is None:

            return {
                **empty_result(),
                "status": "danger",
                "message": "Không nhận dạng được mẫu Excel."
            }

        handlers = get_handlers()

        handler = handlers.get(template)

        if handler is None:

            return {
                **empty_result(),
                "status": "danger",
                "message": "Chức năng đang được phát triển."
            }

        file.seek(0)

        result = handler(file)

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