# ==========================================
# modules/sort_helper.py
# Sắp xếp học sinh theo LỚP -> TÊN
# ==========================================

import unicodedata


def normalize_text(text):
    """
    Chuyển chuỗi về dạng không dấu để so sánh.
    """

    if text is None:
        return ""

    text = str(text).strip().lower()

    text = unicodedata.normalize("NFD", text)

    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

    text = text.replace("đ", "d")
    text = text.replace("Đ", "D")

    return text


def split_name(full_name):
    """
    Tách họ tên thành:
    - tên
    - họ + tên đệm
    """

    if full_name is None:
        return "", ""

    full_name = str(full_name).strip()

    if full_name == "":
        return "", ""

    words = full_name.split()

    ten = words[-1]

    ho_dem = " ".join(words[:-1])

    return (
        normalize_text(ten),
        normalize_text(ho_dem)
    )


def sort_students(data):
    """
    Sắp xếp:
    1. Lớp
    2. Tên
    3. Họ + tên đệm
    """

    return sorted(
        data,
        key=lambda s: (
            normalize_text(s["lop"] or ""),
            split_name(s["ho_ten"] or "")[0],
            split_name(s["ho_ten"] or "")[1]
        )
    )