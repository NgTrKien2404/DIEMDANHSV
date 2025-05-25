import traceback
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import db_handler
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def load_model_and_labels():
    """Load model đã train và labels"""
    try:
        # Load model in new .keras format
        model = load_model('face_recognition_model.keras', compile=False)
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Load label mapping
        label_dict = np.load('label_encoder.npy', allow_pickle=True).item()
        
        print("Model and labels loaded successfully")
        print(f"Available labels: {list(label_dict.values())}")
        return model, label_dict
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        traceback.print_exc()
        return None, None

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

    # Load model và labels
    model, label_encoder = load_model_and_labels()
    if model is None or label_encoder is None:
        print("Không thể load model hoặc labels!")
        return
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    recognized = set()
    attendance_records = []

    print("Đang nhận dạng khuôn mặt... Nhấn 'q' để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        current_time = datetime.now()

        for (x, y, w, h) in faces:
            # Cắt và xử lý khuôn mặt
            face = frame[y:y+h, x:x+w]
            face = cv2.resize(face, (96, 96))
            face = face.astype('float32') / 255.0
            face = np.expand_dims(face, axis=0)

            # Dự đoán
            predictions = model.predict(face)
            predicted_class = np.argmax(predictions[0])
            confidence = predictions[0][predicted_class]
            
            if confidence > 0.5:  # Ngưỡng tin cậy
                student_id = label_encoder[predicted_class]
                
                # Vẽ khung và hiển thị thông tin
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Lấy tên sinh viên từ CSDL
                student_name = db_handler.get_student_name(student_id)
                display_text = f"{student_id} - {student_name} ({confidence:.2f})"
                
                cv2.putText(frame, display_text, (x, y-10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Điểm danh
                if student_id not in recognized:
                    recognized.add(student_id)
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

    # Lưu điểm danh và hiển thị báo cáo
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