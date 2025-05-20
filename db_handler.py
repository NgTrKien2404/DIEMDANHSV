import sqlite3
from datetime import datetime

DB_PATH = "diemdanh.db"

def connect():
    return sqlite3.connect(DB_PATH)

def get_all_sinhvien():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT MaSV, TenSV, MaLop FROM SinhVien")
    result = cursor.fetchall()
    conn.close()
    return result

def add_sinhvien(ma, ten, lop):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SinhVien (MaSV, TenSV, MaLop) VALUES (?, ?, ?)", (ma, ten, lop))
    conn.commit()
    conn.close()

def update_sinhvien(ma, ten):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE SinhVien SET TenSV = ? WHERE MaSV = ?", (ten, ma))
    conn.commit()
    conn.close()

def delete_sinhvien(ma):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SinhVien WHERE MaSV = ?", (ma,))
    conn.commit()
    conn.close()

def get_all_monhoc():
    """Lấy danh sách tất cả môn học"""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT MaMH, TenMH FROM MonHoc")
    monhoc = cursor.fetchall()
    conn.close()
    return monhoc

def create_buoi_hoc(ma_mh):
    """Tạo buổi học mới và trả về ID"""
    conn = connect()
    cursor = conn.cursor()
    try:
        ngay_hoc = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            INSERT INTO BuoiHoc (MaMH, NgayHoc)
            VALUES (?, ?)
        """, (ma_mh, ngay_hoc))
        buoi_hoc_id = cursor.lastrowid
        conn.commit()
        return buoi_hoc_id
    except Exception as e:
        print(f"Lỗi khi tạo buổi học: {e}")
        return None
    finally:
        conn.close()

def add_attendance(ma_sv, ma_buoi):
    """Thêm bản ghi điểm danh"""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO DiemDanh (MaSV, MaBuoi, CoMat)
            VALUES (?, ?, ?)
        """, (ma_sv, ma_buoi, True))
        conn.commit()
    except Exception as e:
        print(f"Lỗi khi thêm điểm danh: {e}")
    finally:
        conn.close()

def batch_add_attendance(attendance_records):
    """Thêm nhiều bản ghi điểm danh cùng lúc"""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.executemany("""
            INSERT INTO DiemDanh (MaSV, MaBuoi, CoMat, ThoiGian)
            VALUES (:MaSV, :MaBuoi, :CoMat, :ThoiGian)
        """, attendance_records)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_student_name(ma_sv):
    """Lấy tên sinh viên từ MSSV"""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT TenSV FROM SinhVien WHERE MaSV = ?", (ma_sv,))
        result = cursor.fetchone()
        return result[0] if result else "Unknown"
    finally:
        conn.close()

def get_diem_danh(ma_buoi):
    """Lấy danh sách điểm danh của một buổi học"""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SinhVien.MaSV, SinhVien.TenSV, DiemDanh.CoMat
        FROM DiemDanh
        JOIN SinhVien ON DiemDanh.MaSV = SinhVien.MaSV
        WHERE DiemDanh.MaBuoi = ?
    """, (ma_buoi,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_monhoc_info(ma_mh):
    """Lấy thông tin chi tiết của môn học và giáo viên"""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT m.TenMH, g.HoTen, m.MaLop
            FROM MonHoc m
            JOIN GiaoVien g ON m.MaGV = g.MaGV
            WHERE m.MaMH = ?
        """, (ma_mh,))
        result = cursor.fetchone()
        if result:
            return {
                'ten_mh': result[0],  # TenMH
                'ten_gv': result[1],  # HoTen của giáo viên
                'ma_lop': result[2]   # MaLop
            }
        return None
    finally:
        conn.close()

def get_buoi_hoc_info(ma_mh):
    """Lấy số buổi học của môn học"""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) + 1
            FROM BuoiHoc
            WHERE MaMH = ?
        """, (ma_mh,))
        result = cursor.fetchone()
        return result[0] if result else 1
    finally:
        conn.close()

def get_attendance_report(ma_buoi):
    """Lấy thông tin báo cáo điểm danh cho một buổi học"""
    conn = connect()
    cursor = conn.cursor()
    try:
        # Lấy thông tin buổi học và môn học
        cursor.execute("""
            SELECT m.TenMH, b.MaMH, g.HoTen, strftime('%d/%m/%Y', b.NgayHoc) as NgayHoc, l.TenLop
            FROM BuoiHoc b
            JOIN MonHoc m ON b.MaMH = m.MaMH
            JOIN GiaoVien g ON m.MaGV = g.MaGV
            JOIN Lop l ON m.MaLop = l.MaLop
            WHERE b.MaBuoi = ?
        """, (ma_buoi,))
        buoi_info = cursor.fetchone()
        
        if not buoi_info:
            return None
        
        # Lấy danh sách điểm danh với thời gian
        cursor.execute("""
            SELECT 
                sv.MaSV, 
                sv.TenSV, 
                sv.MaLop,
                strftime('%H:%M:%S', d.ThoiGian) as ThoiGian
            FROM DiemDanh d
            JOIN SinhVien sv ON d.MaSV = sv.MaSV
            WHERE d.MaBuoi = ? AND d.CoMat = 1
            ORDER BY sv.MaLop, sv.MaSV
        """, (ma_buoi,))
        attendance_list = cursor.fetchall()
        
        return {
            'buoi_info': buoi_info,
            'attendance_list': attendance_list,
            'total_count': len(attendance_list)
        }
    except Exception as e:
        print(f"Lỗi khi lấy báo cáo: {e}")
        return None
    finally:
        conn.close()

def update_diemdanh_table():
    """Update DiemDanh table structure to add ThoiGian column"""
    conn = connect()
    cursor = conn.cursor()
    try:
        # Create new table
        cursor.execute("""
            CREATE TABLE DiemDanh_new (
                MaSV TEXT NOT NULL,
                MaBuoi INTEGER NOT NULL,
                CoMat BOOLEAN NOT NULL,
                ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (MaSV, MaBuoi),
                FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV),
                FOREIGN KEY (MaBuoi) REFERENCES BuoiHoc(MaBuoi)
            )
        """)
        
        # Copy existing data
        cursor.execute("""
            INSERT INTO DiemDanh_new (MaSV, MaBuoi, CoMat, ThoiGian)
            SELECT MaSV, MaBuoi, CoMat, CURRENT_TIMESTAMP
            FROM DiemDanh
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE DiemDanh")
        cursor.execute("ALTER TABLE DiemDanh_new RENAME TO DiemDanh")
        
        conn.commit()
        print("Successfully updated DiemDanh table")
    except Exception as e:
        conn.rollback()
        print(f"Error updating table: {e}")
    finally:
        conn.close()

def add_monhoc(ma_mh, ten_mh, ma_gv, ma_lop):
    """Thêm môn học mới"""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO MonHoc (MaMH, TenMH, MaGV, MaLop)
            VALUES (?, ?, ?, ?)
        """, (ma_mh, ten_mh, ma_gv, ma_lop))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()