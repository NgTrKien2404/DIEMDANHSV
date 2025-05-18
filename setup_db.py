import sqlite3

def setup_database(db_path="diemdanh.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create tables
    cursor.execute("""CREATE TABLE IF NOT EXISTS Lop (
        MaLop TEXT PRIMARY KEY,
        TenLop TEXT NOT NULL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS GiaoVien (
        MaGV TEXT PRIMARY KEY,
        HoTen TEXT NOT NULL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS MonHoc (
        MaMH TEXT PRIMARY KEY,
        TenMH TEXT NOT NULL,
        MaGV TEXT NOT NULL,
        MaLop TEXT NOT NULL,
        FOREIGN KEY (MaGV) REFERENCES GiaoVien(MaGV),
        FOREIGN KEY (MaLop) REFERENCES Lop(MaLop)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS SinhVien (
        MaSV TEXT PRIMARY KEY,
        HoTen TEXT NOT NULL,
        MaLop TEXT NOT NULL,
        HinhAnh TEXT,
        FOREIGN KEY (MaLop) REFERENCES Lop(MaLop)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS BuoiHoc (
        MaBuoi INTEGER PRIMARY KEY AUTOINCREMENT,
        MaMH TEXT NOT NULL,
        NgayHoc DATE NOT NULL,
        FOREIGN KEY (MaMH) REFERENCES MonHoc(MaMH)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS DiemDanh (
        MaSV TEXT NOT NULL,
        MaBuoi INTEGER NOT NULL,
        CoMat BOOLEAN NOT NULL,
        PRIMARY KEY (MaSV, MaBuoi),
        FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV),
        FOREIGN KEY (MaBuoi) REFERENCES BuoiHoc(MaBuoi)
    )""")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
    print("Database and tables created successfully.")
