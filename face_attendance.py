import face_recognition
import cv2
import os
import numpy as np
from datetime import datetime

def load_known_faces(folder="faces"):
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

def recognize_faces():
    known_encodings, known_ids = load_known_faces()

    if not known_encodings:
        print("Không có dữ liệu khuôn mặt.")
        return

    cap = cv2.VideoCapture(0)
    recognized = set()

    print("Đang nhận dạng khuôn mặt... Nhấn 'q' để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Thu nhỏ hình ảnh để xử lý nhanh hơn
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for encoding, loc in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, encoding)
            face_distances = face_recognition.face_distance(known_encodings, encoding)
            best_match = np.argmin(face_distances)

            if matches[best_match]:
                student_id = known_ids[best_match]
                recognized.add(student_id)

                top, right, bottom, left = [v * 4 for v in loc]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {student_id}", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Nhan dien khuon mat", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Ghi lại ai đã được điểm danh
    if recognized:
        print("Đã nhận diện:")
        for sid in recognized:
            print(f" - Mã SV: {sid}")
    else:
        print("Không nhận diện được khuôn mặt nào.")

if __name__ == "__main__":
    recognize_faces()
