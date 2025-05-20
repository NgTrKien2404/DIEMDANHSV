import face_recognition
import cv2
import os
import numpy as np
import db_handler
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def load_known_faces(folder="capture"):
    known_encodings = []
    known_ids = []

    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(folder, filename)
            img = face_recognition.load_image_file(img_path)
            encoding = face_recognition.face_encodings(img)
            if encoding:
                known_encodings.append(encoding[0])
                student_id = os.path.splitext(filename)[0]
                known_ids.append(student_id)
    return known_encodings, known_ids

def recognize_faces(ma_mh=None):
    """Nhận diện khuôn mặt và điểm danh cho môn học cụ thể"""
    if ma_mh is None:
        print("Chưa chọn môn học!")
        return

    # Tạo buổi học mới
    buoi_hoc_id = db_handler.create_buoi_hoc(ma_mh)
    if not buoi_hoc_id:
        print("Lỗi khi tạo buổi học mới!")
        return

    known_encodings, known_ids = load_known_faces()
    if not known_encodings:
        print("Không có dữ liệu khuôn mặt.")
        return
    
    cap = cv2.VideoCapture(0)
    recognized = set()
    attendance_records = []  # Lưu trữ các bản ghi điểm danh

    print("Đang nhận dạng khuôn mặt... Nhấn 'q' để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Lật ngược frame theo chiều ngang
        frame = cv2.flip(frame, 1)

        # Thu nhỏ hình ảnh để xử lý nhanh hơn
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        current_time = datetime.now()

        for encoding, loc in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
            if True in matches:
                face_distances = face_recognition.face_distance(known_encodings, encoding)
                best_match = np.argmin(face_distances)
                
                if matches[best_match]:
                    student_id = known_ids[best_match]
                    
                    # Vẽ khung và hiển thị thông tin
                    top, right, bottom, left = [v * 4 for v in loc]
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Lấy tên sinh viên từ CSDL
                    student_name = db_handler.get_student_name(student_id)
                    display_text = f"{student_id} - {student_name}"
                    
                    # Hiển thị thông tin chi tiết hơn
                    cv2.putText(frame, display_text, (left, top - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Điểm danh ngay lập tức nếu chưa được điểm danh
                    if student_id not in recognized:
                        recognized.add(student_id)
                        # Lưu vào danh sách để batch insert sau
                        attendance_records.append({
                            'MaSV': student_id,
                            'MaBuoi': buoi_hoc_id,
                            'ThoiGian': current_time,
                            'CoMat': True
                        })
                        print(f"Đã điểm danh: {display_text}")

        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Lưu tất cả bản ghi điểm danh vào CSDL
    if attendance_records:
        try:
            db_handler.batch_add_attendance(attendance_records)
            print("\nĐã lưu điểm danh thành công.")
            show_attendance_report(buoi_hoc_id)
        except Exception as e:
            print(f"Lỗi khi lưu điểm danh: {e}")
    else:
        print("Không có sinh viên nào được điểm danh.")

    return True

def show_attendance_report(ma_buoi):
    """Hiển thị báo cáo điểm danh"""
    report_data = db_handler.get_attendance_report(ma_buoi)
    if not report_data:
        return
        
    # Tạo cửa sổ báo cáo
    report_window = tk.Toplevel()
    report_window.title("Báo cáo điểm danh")
    report_window.geometry("800x600")
    
    # Frame thông tin chung
    info_frame = ttk.LabelFrame(report_window, text="Thông tin buổi học")
    info_frame.pack(fill="x", padx=10, pady=5)
    
    buoi_info = report_data['buoi_info']
    ttk.Label(info_frame, text=f"Môn học: {buoi_info[0]} ({buoi_info[1]})").pack()
    ttk.Label(info_frame, text=f"Giảng viên: {buoi_info[2]}").pack()
    ttk.Label(info_frame, text=f"Ngày: {buoi_info[3]}").pack()
    ttk.Label(info_frame, text=f"Lớp: {buoi_info[4]}").pack()
    ttk.Label(info_frame, text=f"Tổng số sinh viên điểm danh: {report_data['total_count']}").pack()
    
    # Frame danh sách điểm danh
    list_frame = ttk.LabelFrame(report_window, text="Danh sách điểm danh")
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Treeview để hiển thị danh sách
    columns = ('stt', 'masv', 'tensv', 'lop', 'thoigian')
    tree = ttk.Treeview(list_frame, columns=columns, show='headings')
    
    # Định nghĩa các cột
    tree.heading('stt', text='STT')
    tree.heading('masv', text='Mã SV')
    tree.heading('tensv', text='Họ và tên')
    tree.heading('lop', text='Lớp')
    tree.heading('thoigian', text='Thời gian điểm danh')
    
    # Thiết lập độ rộng cột
    tree.column('stt', width=50)
    tree.column('masv', width=100)
    tree.column('tensv', width=200)
    tree.column('lop', width=150)
    tree.column('thoigian', width=150)
    
    # Thêm scrollbar
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Đổ dữ liệu vào bảng
    for idx, student in enumerate(report_data['attendance_list'], 1):
        tree.insert('', 'end', values=(
            idx, 
            student[0],  # MaSV
            student[1],  # TenSV
            student[2],  # MaLop
            student[3]   # ThoiGian
        ))
    
    # Pack các thành phần
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Nút xuất báo cáo
    def export_report():
        from datetime import datetime
        filename = f"report/baocao_diemdanh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("STT,Mã SV,Họ và tên,Lớp,Thời gian điểm danh\n")
            for idx, student in enumerate(report_data['attendance_list'], 1):
                f.write(f"{idx},{student[0]},{student[1]},{student[2]},{student[3]}\n")
        messagebox.showinfo("Thành công", f"Đã xuất báo cáo: {filename}")
    
    ttk.Button(report_window, text="Xuất báo cáo CSV", command=export_report).pack(pady=10)

if __name__ == "__main__":
    import sys
    ma_mh = sys.argv[1] if len(sys.argv) > 1 else None
    recognize_faces(ma_mh)