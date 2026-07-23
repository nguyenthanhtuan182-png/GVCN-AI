from collections import Counter

from modules.database import get_connection


class AIAnalyzer:

    def __init__(self):

        self.conn = get_connection()

        self.cursor = self.conn.cursor()


    # =====================================================
    # DANH SÁCH LỚP
    # =====================================================

    def get_classes(self):

        self.cursor.execute("""

            SELECT DISTINCT lop

            FROM students

            WHERE lop IS NOT NULL
              AND lop<>''

            ORDER BY lop

        """)

        return [

            row[0]

            for row in self.cursor.fetchall()

        ]


    # =====================================================
    # HỌC SINH THEO LỚP
    # =====================================================

    def get_students(self, lop):

        self.cursor.execute("""

            SELECT *

            FROM students

            WHERE lop=?

            ORDER BY ho_ten

        """, (lop,))

        columns = [

            c[0]

            for c in self.cursor.description

        ]

        return [

            dict(zip(columns, row))

            for row in self.cursor.fetchall()

        ]


    # =====================================================
    # KẾT QUẢ HỌC TẬP THEO LỚP
    # =====================================================

    def get_academic(self, lop):

        self.cursor.execute("""

            SELECT
                a.*
            FROM academic a

            INNER JOIN students s

            ON a.ma_dinh_danh=s.ma_dinh_danh

            WHERE s.lop=?

            ORDER BY
                a.mon_hoc,
                s.ho_ten

        """, (lop,))

        columns = [

            c[0]

            for c in self.cursor.description

        ]

        return [

            dict(zip(columns, row))

            for row in self.cursor.fetchall()

        ]


# =====================================================
# AI CHÍNH
# =====================================================

    def analyze(self, lop):

        students = self.get_students(lop)

        academic = self.get_academic(lop)

        return {

            "classes": self.get_classes(),

            "selected_class": lop,

            "students": self.analyze_students(students),

            "academic": self.analyze_academic(students, academic),

            "gender": self.analyze_gender(students, academic),

            "subjects": self.analyze_subjects(academic),

            "learning": self.analyze_learning_levels(academic),

            "ranking": self.rank_students(students, academic),

            "attention": self.detect_students_need_attention(
                students,
                academic
            ),

            "summary": self.generate_summary(
                students,
                academic
            ),

            "recommendations": self.generate_recommendations(
                students,
                academic
            )

        }


# =====================================================
# AI 01
# THỐNG KÊ HỌC SINH
# =====================================================

    def analyze_students(self, students):

        result = {

            "tong_hoc_sinh": len(students),

            "so_nam": 0,

            "so_nu": 0,

            "dan_toc": {},

            "trang_thai": {}

        }

        ethnic = Counter()

        status = Counter()

        for hs in students:

            gt = str(

                hs.get("gioi_tinh", "")

            ).strip().lower()

            if gt == "nam":

                result["so_nam"] += 1

            elif gt == "nữ":

                result["so_nu"] += 1

            ethnic[

                hs.get("dan_toc", "")

            ] += 1

            status[

                hs.get("trang_thai", "")

            ] += 1

        result["dan_toc"] = dict(ethnic)

        result["trang_thai"] = dict(status)

        return result


    # =====================================================
    # AI 02
    # THỐNG KÊ KẾT QUẢ HỌC TẬP
    # =====================================================

    def analyze_academic(self, students, academic):

        result = {

            "tong_ban_ghi": len(academic),

            "diem_trung_binh": 0,

            "mon_hoc": {},

            "mon_cao_nhat": "-",

            "mon_thap_nhat": "-",

            "ket_qua_hoc_tap": {},

            "ket_qua_ren_luyen": {}

        }

        if len(academic) == 0:

            return result

        tong = 0

        dem = 0

        mon = {}

        hoc_luc = Counter()

        ren_luyen = Counter()

        for row in academic:

            try:

                diem = float(

                    row["diem_tb"]

                )

            except:

                continue

            tong += diem

            dem += 1

            mon.setdefault(

                row["mon_hoc"],

                []

            )

            mon[

                row["mon_hoc"]

            ].append(diem)

            hoc_luc[

                row["ket_qua_hoc_tap"]

            ] += 1

            ren_luyen[

                row["ket_qua_ren_luyen"]

            ] += 1

        if dem > 0:

            result["diem_trung_binh"] = round(

                tong / dem,

                2

            )

        avg = {}

        for ten_mon, ds in mon.items():

            avg[ten_mon] = round(

                sum(ds) / len(ds),

                2

            )

        result["mon_hoc"] = avg

        result["ket_qua_hoc_tap"] = dict(hoc_luc)

        result["ket_qua_ren_luyen"] = dict(ren_luyen)

        if avg:

            result["mon_cao_nhat"] = max(

                avg,

                key=avg.get

            )

            result["mon_thap_nhat"] = min(

                avg,

                key=avg.get

            )

        return result
    # =====================================================
    # AI 03
    # PHÂN TÍCH GIỚI TÍNH
    # =====================================================

    def analyze_gender(self, students, academic):

        result = {

            "Nam": 0,

            "Nữ": 0,

            "ket_luan": ""

        }

        gender_map = {}

        for hs in students:

            gender_map[

                hs["ma_dinh_danh"]

            ] = hs["gioi_tinh"]

        gender_score = {

            "Nam": [],

            "Nữ": []

        }

        for row in academic:

            try:

                diem = float(row["diem_tb"])

            except:

                continue

            gt = gender_map.get(

                row["ma_dinh_danh"],

                ""

            )

            if gt in gender_score:

                gender_score[gt].append(diem)

        for gt in gender_score:

            if gender_score[gt]:

                result[gt] = round(

                    sum(gender_score[gt]) /

                    len(gender_score[gt]),

                    2

                )

        if result["Nam"] > result["Nữ"]:

            result["ket_luan"] = "Nam học tốt hơn."

        elif result["Nam"] < result["Nữ"]:

            result["ket_luan"] = "Nữ học tốt hơn."

        else:

            result["ket_luan"] = "Kết quả tương đương."

        return result


    # =====================================================
    # AI 04
    # PHÂN TÍCH MÔN HỌC
    # =====================================================

    def analyze_subjects(self, academic):

        subjects = {}

        for row in academic:

            try:

                diem = float(row["diem_tb"])

            except:

                continue

            mon = row["mon_hoc"]

            subjects.setdefault(mon, [])

            subjects[mon].append(diem)

        result = {}

        for mon, ds in subjects.items():

            result[mon] = {

                "diem_tb": round(

                    sum(ds) / len(ds),

                    2

                ),

                "cao_nhat": round(

                    max(ds),

                    2

                ),

                "thap_nhat": round(

                    min(ds),

                    2

                ),

                "so_hoc_sinh": len(ds)

            }

        return result
    # =====================================================
    # AI 05
    # PHÂN LOẠI HỌC LỰC
    # =====================================================

    def analyze_learning_levels(self, academic):

        student_scores = {}

        for row in academic:

            ma = row["ma_dinh_danh"]

            try:

                diem = float(row["diem_tb"])

            except:

                continue

            student_scores.setdefault(ma, [])

            student_scores[ma].append(diem)

        result = {

            "Giỏi": 0,

            "Khá": 0,

            "Đạt": 0,

            "Chưa đạt": 0

        }

        for scores in student_scores.values():

            avg = sum(scores) / len(scores)

            if avg >= 8:

                result["Giỏi"] += 1

            elif avg >= 6.5:

                result["Khá"] += 1

            elif avg >= 5:

                result["Đạt"] += 1

            else:

                result["Chưa đạt"] += 1

        return result

        # =====================================================
    # AI 06
    # XẾP HẠNG HỌC SINH
    # =====================================================

    # =====================================================
    # AI 06
    # XẾP HẠNG HỌC SINH
    # =====================================================

    def rank_students(self, students, academic):

        ranking = {}

        # Khởi tạo dữ liệu học sinh
        for hs in students:

            ranking[hs["ma_dinh_danh"]] = {

                "ho_ten": hs["ho_ten"],

                "lop": hs["lop"],

                "tong": 0,

                "so_mon": 0,

                "diem_tb": 0,

                "risk_score": 0,

                "risk_level": "An toàn",

                "mon_duoi_5": 0,

                "mon_duoi_3": 0,

                "hoc_tap_chua_dat": False,

                "ren_luyen_chua_dat": False

            }

        # Tổng hợp điểm từng học sinh
        for row in academic:

            ma = row["ma_dinh_danh"]

            if ma not in ranking:

                continue

            try:

                diem = float(row["diem_tb"])

            except:

                continue

            hs = ranking[ma]

            hs["tong"] += diem

            hs["so_mon"] += 1

            if diem < 5:

                hs["mon_duoi_5"] += 1

            if diem < 3:

                hs["mon_duoi_3"] += 1

            if str(row.get("ket_qua_hoc_tap", "")).strip() == "Chưa đạt":

                hs["hoc_tap_chua_dat"] = True

            if str(row.get("ket_qua_ren_luyen", "")).strip() == "Chưa đạt":

                hs["ren_luyen_chua_dat"] = True

        result = []

                # Tính điểm trung bình
        for hs in ranking.values():

            if hs["so_mon"] > 0:

                hs["diem_tb"] = round(

                    hs["tong"] / hs["so_mon"],

                    2

                )

            # AI07 - Risk Engine
            risk = self.calculate_risk_score(hs)

            hs["risk_score"] = risk["risk_score"]

            hs["risk_level"] = risk["risk_level"]

            hs["risk_reasons"] = risk["reasons"]

            result.append(hs)
        # Xếp hạng theo điểm trung bình
        result.sort(

            key=lambda x: x["diem_tb"],

            reverse=True

        )

        # Gán thứ hạng
        for i, hs in enumerate(result):

            hs["xep_hang"] = i + 1

        return result    
         # =====================================================
    # AI 07
    # RISK ENGINE - HỌC SINH CẦN QUAN TÂM
    # =====================================================

    def calculate_risk_score(self, student):

        risk = 0

        reasons = []

        # ----------------------------
        # Học lực
        # ----------------------------

        if student["diem_tb"] < 5:

            risk += 40

            reasons.append("Điểm trung bình dưới 5")

        elif student["diem_tb"] < 6.5:

            risk += 20

            reasons.append("Điểm trung bình dưới 6.5")

        # ----------------------------
        # Môn dưới 5
        # ----------------------------

        if student["mon_duoi_5"] > 0:

            risk += student["mon_duoi_5"] * 5

            reasons.append(
                f"{student['mon_duoi_5']} môn dưới 5"
            )

        # ----------------------------
        # Môn dưới 3
        # ----------------------------

        if student["mon_duoi_3"] > 0:

            risk += student["mon_duoi_3"] * 10

            reasons.append(
                f"{student['mon_duoi_3']} môn dưới 3"
            )

        # ----------------------------
        # Học tập
        # ----------------------------

        if student["hoc_tap_chua_dat"]:

            risk += 20

            reasons.append(
                "Kết quả học tập: Chưa đạt"
            )

        # ----------------------------
        # Rèn luyện
        # ----------------------------

        if student["ren_luyen_chua_dat"]:

            risk += 15

            reasons.append(
                "Kết quả rèn luyện: Chưa đạt"
            )

        # ----------------------------
        # Chuẩn hóa
        # ----------------------------

        if risk > 100:

            risk = 100

        if risk >= 60:

            level = "Nguy cơ cao"

        elif risk >= 30:

            level = "Cần theo dõi"

        else:

            level = "An toàn"

        return {

            "risk_score": risk,

            "risk_level": level,

            "reasons": reasons

        }

    def detect_students_need_attention(self, students, academic):

        info = {}

        for hs in students:

            info[hs["ma_dinh_danh"]] = {

                "ho_ten": hs["ho_ten"],

                "lop": hs["lop"],

                "tong_diem": 0,

                "so_mon": 0,

                "diem_tb": 0,

                "mon_duoi_5": 0,

                "mon_duoi_3": 0,

                "hoc_tap_chua_dat": False,

                "ren_luyen_chua_dat": False

            }

        for row in academic:

            ma = row["ma_dinh_danh"]

            if ma not in info:

                continue

            try:

                diem = float(row["diem_tb"])

            except:

                continue

            hs = info[ma]

            hs["tong_diem"] += diem

            hs["so_mon"] += 1

            if diem < 5:

                hs["mon_duoi_5"] += 1

            if diem < 3:

                hs["mon_duoi_3"] += 1

            if str(row.get("ket_qua_hoc_tap", "")).strip() == "Chưa đạt":

                hs["hoc_tap_chua_dat"] = True

            if str(row.get("ket_qua_ren_luyen", "")).strip() == "Chưa đạt":

                hs["ren_luyen_chua_dat"] = True

        result = []

        for hs in info.values():

            if hs["so_mon"] == 0:

                continue

            hs["diem_tb"] = round(

                hs["tong_diem"] /

                hs["so_mon"],

                2

            )

            ai = self.calculate_risk_score(hs)

            hs["risk_score"] = ai["risk_score"]

            hs["muc_do"] = ai["risk_level"]

            hs["nguyen_nhan"] = ", ".join(ai["reasons"])

            if ai["risk_score"] >= 30:

                result.append(hs)

        result.sort(

            key=lambda x: x["risk_score"],

            reverse=True

        )

        return result
       # =====================================================
    # AI 08
    # KẾT LUẬN
    # =====================================================

    def generate_summary(self, students, academic):

        student_info = self.analyze_students(students)

        academic_info = self.analyze_academic(students, academic)

        attention = self.detect_students_need_attention(
            students,
            academic
        )

        ranking = self.rank_students(
            students,
            academic
        )

        summary = []

        summary.append(
            f"Lớp có {student_info['tong_hoc_sinh']} học sinh."
        )

        summary.append(
            f"Nam: {student_info['so_nam']} - Nữ: {student_info['so_nu']}."
        )

        if len(academic) == 0:

            summary.append(
                "Chưa có dữ liệu học tập."
            )

            return summary

        summary.append(
            f"Điểm trung bình lớp: {academic_info['diem_trung_binh']}."
        )

        summary.append(
            f"Môn mạnh: {academic_info['mon_cao_nhat']}."
        )

        summary.append(
            f"Môn cần cải thiện: {academic_info['mon_thap_nhat']}."
        )

        summary.append(
            f"Có {len(attention)} học sinh cần quan tâm."
        )

        if len(ranking) > 0:

            summary.append(
                f"Học sinh đứng đầu: {ranking[0]['ho_ten']} ({ranking[0]['diem_tb']})."
            )

            summary.append(
                f"Học sinh cuối lớp: {ranking[-1]['ho_ten']} ({ranking[-1]['diem_tb']})."
            )

        return summary


    # =====================================================
    # AI 09
    # KHUYẾN NGHỊ
    # =====================================================

    def generate_recommendations(self, students, academic):

        recommendations = []

        attention = self.detect_students_need_attention(
            students,
            academic
        )

        academic_info = self.analyze_academic(
            students,
            academic
        )

        if len(academic) == 0:

            recommendations.append(
                "Cập nhật dữ liệu học tập để AI phân tích."
            )

            return recommendations

        if academic_info["diem_trung_binh"] >= 8:

            recommendations.append(
                "Tiếp tục duy trì chất lượng học tập."
            )

        elif academic_info["diem_trung_binh"] >= 6.5:

            recommendations.append(
                "Đẩy mạnh bồi dưỡng học sinh khá giỏi."
            )

        elif academic_info["diem_trung_binh"] >= 5:

            recommendations.append(
                "Tăng cường phụ đạo học sinh trung bình."
            )

        else:

            recommendations.append(
                "Cần xây dựng kế hoạch nâng cao chất lượng học tập."
            )

        if len(attention) > 0:

            recommendations.append(
                f"Theo dõi {len(attention)} học sinh có nguy cơ."
            )

        recommendations.append(
            "Cập nhật dữ liệu sau mỗi lần kiểm tra."
        )

        return recommendations


    # =====================================================
    # ĐÓNG KẾT NỐI
    # =====================================================

    def close(self):

        self.conn.close()