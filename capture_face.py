import cv2
import os
from tkinter import messagebox

def capture_face(masv):
    save_dir = "capture/train_data"
    os.makedirs(save_dir, exist_ok=True)
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    count = 0

    while count < 5:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Lỗi", "Không thể mở camera!")
            break
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (96, 96))
            filename = os.path.join(save_dir, f"{masv}_{count+1}.jpg")
            cv2.imwrite(filename, face_img)
            count += 1 #
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Saved: {count}/5", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.imshow("Capture Face", frame)
            cv2.waitKey(1000)  # Đợi 1 giây giữa các lần chụp
            break  # Chỉ lấy 1 khuôn mặt mỗi lần
        else:
            cv2.imshow("Capture Face", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
    if count == 2:
        messagebox.showinfo("Thành công", f"Đã lưu 2 ảnh cho SV {masv}")
    else:
        messagebox.showwarning("Chưa đủ ảnh", f"Chỉ lưu được {count}/5 ảnh cho SV {masv}")

if __name__ == "__main__":
    capture_face("test")