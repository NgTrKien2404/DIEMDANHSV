import tkinter as tk
from tkinter import messagebox
import db_handler
import subprocess
import os
import capture_face
# Nếu chưa có CSDL thì tạo mới
if not os.path.exists("diemdanh.db"):
    subprocess.run(["python", "setup_db.py"])

# Tải dữ liệu sinh viên
def load_data():
    listbox.delete(0, tk.END)
    try:
        for sv in db_handler.get_all_sinhvien():
            listbox.insert(tk.END, f"{sv[0]} - {sv[1]} - {sv[2]}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {str(e)}")

# Thêm sinh viên
def them():
    ma = entry_ma.get().strip()
    ten = entry_ten.get().strip()
    lop = entry_lop.get().strip()

    if not ma.isdigit():
        messagebox.showwarning("Lỗi", "Mã SV phải là số.")
        return

    if ma and ten and lop:
        existing = db_handler.get_all_sinhvien()
        if any(sv[0] == ma for sv in existing):
            messagebox.showwarning("Lỗi", "Mã SV đã tồn tại.")
        else:
            # Chụp ảnh khuôn mặt trước khi thêm vào CSDL
            from capture_face import capture_face
            capture_face(ma)  # Truyền mã SV để đặt tên file ảnh
            
            # Thêm thông tin vào CSDL
            db_handler.add_sinhvien(ma, ten, lop)
            load_data()
            clear_entries()
            messagebox.showinfo("Thành công", "Đã thêm sinh viên và chụp ảnh khuôn mặt.")
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập đủ thông tin.")

# Sửa tên sinh viên
def sua():
    ma = entry_ma.get().strip()
    ten = entry_ten.get().strip()

    if not ma.isdigit():
        messagebox.showwarning("Lỗi", "Mã SV phải là số.")
        return

    if ma and ten:
        db_handler.update_sinhvien(ma, ten)
        load_data()
        clear_entries()
    else:
        messagebox.showwarning("Lỗi", "Nhập mã và tên mới.")

# Xóa sinh viên
def xoa():
    ma = entry_ma.get().strip()
    if ma:
        db_handler.delete_sinhvien(ma)
        load_data()
        clear_entries()
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập mã sinh viên.")

# Xóa nội dung các ô nhập
def clear_entries():
    entry_ma.delete(0, tk.END)
    entry_ten.delete(0, tk.END)
    entry_lop.delete(0, tk.END)

# Khi chọn sinh viên từ danh sách
def on_select(event):
    selected = listbox.get(listbox.curselection())
    parts = selected.split(" - ")
    if len(parts) >= 3:
        entry_ma.delete(0, tk.END)
        entry_ma.insert(0, parts[0])
        entry_ten.delete(0, tk.END)
        entry_ten.insert(0, parts[1])
        entry_lop.delete(0, tk.END)
        entry_lop.insert(0, parts[2])

# Tìm kiếm sinh viên theo tên
def tim_kiem():
    query = entry_search.get().strip().lower()
    listbox.delete(0, tk.END)
    for sv in db_handler.get_all_sinhvien():
        if query in sv[1].lower():
            listbox.insert(tk.END, f"{sv[0]} - {sv[1]} - {sv[2]}")

# Giao diện chính
window = tk.Tk()
window.title("QUẢN LÝ SINH VIÊN")
window.geometry("700x550")
window.configure(padx=20, pady=20)

font_label = ("Arial", 14)
font_entry = ("Arial", 14)

# Nhập liệu
tk.Label(window, text="Mã SV:", font=font_label).grid(row=0, column=0, sticky="e")
entry_ma = tk.Entry(window, font=font_entry)
entry_ma.grid(row=0, column=1, padx=10, pady=5, sticky="w")

tk.Label(window, text="Họ tên:", font=font_label).grid(row=1, column=0, sticky="e")
entry_ten = tk.Entry(window, font=font_entry)
entry_ten.grid(row=1, column=1, padx=10, pady=5, sticky="w")

tk.Label(window, text="Lớp:", font=font_label).grid(row=2, column=0, sticky="e")
entry_lop = tk.Entry(window, font=font_entry)
entry_lop.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Nút chức năng
tk.Button(window, text="Thêm", width=10, font=font_label, command=them).grid(row=0, column=2, padx=10)
tk.Button(window, text="Sửa", width=10, font=font_label, command=sua).grid(row=1, column=2, padx=10)
tk.Button(window, text="Xóa", width=10, font=font_label, command=xoa).grid(row=2, column=2, padx=10)
tk.Button(window, text="Điểm danh bằng khuôn mặt", font=font_label,
          command=lambda: subprocess.run(["python", "face_attendance.py"])).grid(row=5, column=1, pady=10)
tk.Button(window, text="Xóa ô nhập", width=10, font=font_label, command=clear_entries).grid(row=5, column=0, padx=10)

# Tìm kiếm
tk.Label(window, text="Tìm theo tên:", font=font_label).grid(row=3, column=0, sticky="e")
entry_search = tk.Entry(window, font=font_entry)
entry_search.grid(row=3, column=1, sticky="w")
tk.Button(window, text="Tìm", font=font_label, command=tim_kiem).grid(row=3, column=2)

# Danh sách sinh viên
listbox = tk.Listbox(window, width=60, height=15, font=("Courier New", 12))
listbox.grid(row=4, column=0, columnspan=3, pady=10)
listbox.bind("<<ListboxSelect>>", on_select)

load_data()
window.mainloop()
