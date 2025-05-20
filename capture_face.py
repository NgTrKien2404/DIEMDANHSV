import cv2
import os
from tkinter import messagebox
def capture_face(student_id):
    # Tạo thư mục faces nếu chưa tồn tại
    if not os.path.exists("capture"):
        os.makedirs("capture")
        
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Lỗi", "Không thể kết nối camera!")
            break
        
        # Lật ngược frame theo chiều ngang
        frame = cv2.flip(frame, 1)
             
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('SPACE to take picture or Q to quit', frame)

        key = cv2.waitKey(1)
        if key == ord(' '):  # Nhấn space để chụp
            # Lưu ảnh với tên là mã số sinh viên
            filename = f"capture/{student_id}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Đã lưu ảnh: {filename}")
            break
        elif key == ord('q'):  # Nhấn q để thoát
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_face("test")