import sqlite3

conn = sqlite3.connect("database/gvcn_ai.db")

cursor = conn.cursor()

cursor.execute("""
INSERT INTO students
(ho_ten,lop,gioi_tinh,ngay_sinh,dia_chi,sdt_phu_huynh,hoc_luc,hanh_kiem,nguy_co)

VALUES

('Nguyễn Văn A','9A1','Nam','2011-05-02','Buôn Ma Thuột','0912345678','Giỏi','Tốt',10)
""")

conn.commit()

conn.close()

print("Đã thêm dữ liệu.")