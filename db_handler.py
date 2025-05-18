import sqlite3

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
