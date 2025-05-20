import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import db_handler
import subprocess
import os
import capture_face
from datetime import datetime

# Nếu chưa có CSDL thì tạo mới
if not os.path.exists("diemdanh.db"):
    subprocess.run(["python", "setup_db.py"])
    
def start_face_attendance():
    """Bắt đầu điểm danh khuôn mặt"""
    select_window = tk.Toplevel()
    select_window.title("Thông tin buổi học")
    select_window.geometry("500x300")
    
    # Frame chứa thông tin
    info_frame = ttk.LabelFrame(select_window, text="Thông tin chi tiết", padding=10)
    info_frame.pack(fill="x", padx=10, pady=5)
    
    # Labels để hiển thị thông tin
    lbl_mon = ttk.Label(info_frame, text="Môn học:", font=('Arial', 11))
    lbl_mon.grid(row=0, column=0, sticky='e', padx=5, pady=5)
    
    lbl_gv = ttk.Label(info_frame, text="Giáo viên:", font=('Arial', 11))
    lbl_gv.grid(row=1, column=0, sticky='e', padx=5, pady=5)
    
    lbl_buoi = ttk.Label(info_frame, text="Buổi học:", font=('Arial', 11))
    lbl_buoi.grid(row=2, column=0, sticky='e', padx=5, pady=5)
    
    # Labels hiển thị giá trị
    val_mon = ttk.Label(info_frame, text="", font=('Arial', 11))
    val_mon.grid(row=0, column=1, sticky='w', padx=5, pady=5)
    
    val_gv = ttk.Label(info_frame, text="", font=('Arial', 11))
    val_gv.grid(row=1, column=1, sticky='w', padx=5, pady=5)
    
    val_buoi = ttk.Label(info_frame, text="", font=('Arial', 11))
    val_buoi.grid(row=2, column=1, sticky='w', padx=5, pady=5)
    
    def on_monhoc_selected(event):
        selected = monhoc_cb.get()
        if selected:
            ma_mh = selected.split(" - ")[0]
            # Lấy thông tin môn học
            monhoc_info = db_handler.get_monhoc_info(ma_mh)
            if monhoc_info:
                val_mon.config(text=monhoc_info['ten_mh'])
                val_gv.config(text=monhoc_info['ten_gv'])
                # Lấy số buổi học
                buoi_so = db_handler.get_buoi_hoc_info(ma_mh)
                val_buoi.config(text=f"Buổi {buoi_so}")
    
    # Combobox chọn môn học
    monhoc_cb = ttk.Combobox(select_window, 
                            font=('Arial', 11), 
                            width=40, 
                            state="readonly")
    monhoc_cb['values'] = get_monhoc_list()
    monhoc_cb.pack(pady=10)
    monhoc_cb.bind('<<ComboboxSelected>>', on_monhoc_selected)
    
    def start_attendance():
        selected = monhoc_cb.get()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn môn học!")
            return
            
        ma_mh = selected.split(" - ")[0]
        select_window.destroy()
        from face_attendance import recognize_faces
        recognize_faces(ma_mh)
    
    # Nút bắt đầu điểm danh
    btn_start = ttk.Button(select_window, 
                          text="Bắt đầu điểm danh", 
                          command=start_attendance)
    btn_start.pack(pady=20)

def get_monhoc_list():
    """Lấy danh sách môn học từ database"""
    monhoc = db_handler.get_all_monhoc()
    return [f"{mh[0]} - {mh[1]}" for mh in monhoc]

def show_add_subject_form():
    """Hiển thị form thêm môn học"""
    add_window = tk.Toplevel()
    add_window.title("Thêm Môn Học")
    add_window.geometry("400x350")
    
    # Form thêm môn học
    form_frame = ttk.LabelFrame(add_window, text="Thông tin môn học", padding=20)
    form_frame.pack(fill="x", padx=10, pady=5)
    
    # Các trường nhập liệu
    ttk.Label(form_frame, text="Mã môn học:").grid(row=0, column=0, pady=5, sticky="e")
    mamh_entry = ttk.Entry(form_frame, width=30)
    mamh_entry.grid(row=0, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Tên môn học:").grid(row=1, column=0, pady=5, sticky="e")
    tenmh_entry = ttk.Entry(form_frame, width=30)
    tenmh_entry.grid(row=1, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Mã giảng viên:").grid(row=2, column=0, pady=5, sticky="e")
    magv_entry = ttk.Entry(form_frame, width=30)
    magv_entry.grid(row=2, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Mã lớp:").grid(row=3, column=0, pady=5, sticky="e")
    malop_entry = ttk.Entry(form_frame, width=30)
    malop_entry.grid(row=3, column=1, pady=5, padx=5)
    
    def save_subject():
        ma_mh = mamh_entry.get().strip()
        ten_mh = tenmh_entry.get().strip()
        ma_gv = magv_entry.get().strip()
        ma_lop = malop_entry.get().strip()
        
        if not all([ma_mh, ten_mh, ma_gv, ma_lop]):
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
            
        try:
            # Thêm hàm add_monhoc vào db_handler
            db_handler.add_monhoc(ma_mh, ten_mh, ma_gv, ma_lop)
            messagebox.showinfo("Thành công", "Đã thêm môn học!")
            add_window.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm môn học: {str(e)}")
    
    # Nút lưu
    ttk.Button(form_frame, text="Lưu", command=save_subject).grid(row=4, column=1, pady=20)

def show_add_student_form():
    """Hiển thị form quản lý sinh viên"""
    student_window = tk.Toplevel()
    student_window.title("Quản Lý Sinh Viên")
    student_window.geometry("800x600")
    
    # Frame nhập thông tin
    info_frame = ttk.LabelFrame(student_window, text="Thông tin sinh viên", padding=10)
    info_frame.pack(fill="x", padx=10, pady=5)
    
    # Các trường nhập liệu
    ttk.Label(info_frame, text="Mã số SV:", font=('Arial', 11)).grid(row=0, column=0, pady=5, padx=5, sticky='e')
    masv_entry = ttk.Entry(info_frame, width=30, font=('Arial', 11))
    masv_entry.grid(row=0, column=1, pady=5, padx=5)
    
    ttk.Label(info_frame, text="Họ và tên:", font=('Arial', 11)).grid(row=1, column=0, pady=5, padx=5, sticky='e')
    ten_entry = ttk.Entry(info_frame, width=30, font=('Arial', 11))
    ten_entry.grid(row=1, column=1, pady=5, padx=5)
    
    ttk.Label(info_frame, text="Lớp:", font=('Arial', 11)).grid(row=2, column=0, pady=5, padx=5, sticky='e')
    lop_entry = ttk.Entry(info_frame, width=30, font=('Arial', 11))
    lop_entry.grid(row=2, column=1, pady=5, padx=5)
    
    # Frame danh sách sinh viên
    list_frame = ttk.LabelFrame(student_window, text="Danh sách sinh viên", padding=10)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Tạo Treeview để hiển thị danh sách
    columns = ('masv', 'hoten', 'lop')
    tree = ttk.Treeview(list_frame, columns=columns, show='headings')
    
    # Định nghĩa các cột
    tree.heading('masv', text='Mã SV')
    tree.heading('hoten', text='Họ và tên')
    tree.heading('lop', text='Lớp')
    
    tree.column('masv', width=100)
    tree.column('hoten', width=250)
    tree.column('lop', width=100)
    
    # Thêm scrollbar
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack các thành phần
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def load_student_list():
        """Tải lại danh sách sinh viên"""
        for item in tree.get_children():
            tree.delete(item)
        for sv in db_handler.get_all_sinhvien():
            tree.insert('', 'end', values=sv)
    
    def clear_entries():
        """Xóa nội dung các ô nhập"""
        masv_entry.delete(0, tk.END)
        ten_entry.delete(0, tk.END)
        lop_entry.delete(0, tk.END)
    
    def on_select(event):
        """Xử lý khi chọn sinh viên từ danh sách"""
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0])['values']
            masv_entry.delete(0, tk.END)
            masv_entry.insert(0, values[0])
            ten_entry.delete(0, tk.END)
            ten_entry.insert(0, values[1])
            lop_entry.delete(0, tk.END)
            lop_entry.insert(0, values[2])
    
    def them_sv():
        """Thêm sinh viên mới"""
        ma = masv_entry.get().strip()
        ten = ten_entry.get().strip()
        lop = lop_entry.get().strip()

        if not ma.isdigit():
            messagebox.showwarning("Lỗi", "Mã SV phải là số.")
            return

        if ma and ten and lop:
            existing = db_handler.get_all_sinhvien()
            if any(sv[0] == ma for sv in existing):
                messagebox.showwarning("Lỗi", "Mã SV đã tồn tại.")
            else:
                from capture_face import capture_face
                capture_face(ma)
                db_handler.add_sinhvien(ma, ten, lop)
                load_student_list()
                clear_entries()
                messagebox.showinfo("Thành công", "Đã thêm sinh viên và chụp ảnh khuôn mặt.")
        else:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đủ thông tin.")
    
    def sua_sv():
        """Sửa thông tin sinh viên"""
        ma = masv_entry.get().strip()
        ten = ten_entry.get().strip()
        lop = lop_entry.get().strip()

        if not ma.isdigit():
            messagebox.showwarning("Lỗi", "Mã SV phải là số.")
            return

        if ma and ten and lop:
            db_handler.update_sinhvien(ma, ten)
            load_student_list()
            clear_entries()
        else:
            messagebox.showwarning("Lỗi", "Nhập mã và tên mới.")
    
    def xoa_sv():
        """Xóa sinh viên"""
        ma = masv_entry.get().strip()
        if ma:
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa sinh viên này?"):
                db_handler.delete_sinhvien(ma)
                load_student_list()
                clear_entries()
        else:
            messagebox.showwarning("Lỗi", "Vui lòng chọn sinh viên cần xóa.")
    
    # Frame chứa các nút
    button_frame = ttk.Frame(student_window, padding=10)
    button_frame.pack(fill="x", padx=10)
    
    # Các nút chức năng
    ttk.Button(button_frame, text="Thêm", command=them_sv, width=15).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Sửa", command=sua_sv, width=15).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Xóa", command=xoa_sv, width=15).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Xóa ô nhập", command=clear_entries, width=15).pack(side="left", padx=5)
    
    # Bind sự kiện chọn từ tree
    tree.bind('<<TreeviewSelect>>', on_select)
    
    # Load dữ liệu ban đầu
    load_student_list()

# Giao diện chính
window = tk.Tk()
window.title("HỆ THỐNG ĐIỂM DANH")
window.geometry("400x300")
# Frame chính
main_frame = ttk.Frame(window, padding="20")
main_frame.pack(fill="both", expand=True)

# Style cho buttons
style = ttk.Style()
style.configure("Menu.TButton", 
                font=("Arial", 12),
                padding=10,
                width=30,
                anchor="center")

# Các nút menu
ttk.Button(main_frame, 
          text="1. Thêm sinh viên",
          style="Menu.TButton",
          command=show_add_student_form).pack(pady=5)

ttk.Button(main_frame, 
          text="2. Thêm môn học",
          style="Menu.TButton", 
          command=show_add_subject_form).pack(pady=5)

ttk.Button(main_frame,
          text="3. Thu thập ảnh khuôn mặt",
          style="Menu.TButton",
          command=lambda: capture_face.capture_face(None)).pack(pady=5)

ttk.Button(main_frame,
          text="4. Điểm danh khuôn mặt",
          style="Menu.TButton",
          command=start_face_attendance).pack(pady=5)

#ttk.Button(main_frame,
#          text="5. Xem lịch sử điểm danh",
#          style="Menu.TButton",
#          command=lambda: messagebox.showinfo("Thông báo", "Tính năng đang phát triển")).pack(pady=5)

#ttk.Button(main_frame,
#          text="6. Xuất file Excel",
#          style="Menu.TButton",
#          command=lambda: messagebox.showinfo("Thông báo", "Tính năng đang phát triển")).pack(pady=5)

#ttk.Button(main_frame,
#          text="7. Nhập sinh viên từ Excel",
#          style="Menu.TButton",
#          command=lambda: messagebox.showinfo("Thông báo", "Tính năng đang phát triển")).pack(pady=5)


# Thêm icon cho cửa sổ chính (tùy chọn)
try:
    window.iconbitmap("icon.ico")  # Thêm file icon nếu có
except:
    pass

# Căn giữa cửa sổ
window.update()
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
window.geometry(f"+{x}+{y}")

window.mainloop()