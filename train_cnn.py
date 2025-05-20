import os
import cv2
import numpy as np
import time
import face_recognition
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Constants
IMG_SIZE = 96
CAPTURE_DIR = "capture"

# Haar cascade for face detection
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def preprocess_image(img):
    """Detect and preprocess a face from an image."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 5, minSize=(60, 60), maxSize=(200, 200))

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    margin = 20
    x, y = max(0, x - margin), max(0, y - margin)
    w = min(img.shape[1] - x, w + 2 * margin)
    h = min(img.shape[0] - y, h + 2 * margin)
    face = img[y:y + h, x:x + w]

    face = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
    lab = cv2.cvtColor(face, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(3.0, (8, 8)).apply(l)
    face = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB)
    face = face.astype('float32')
    return (face - face.mean()) / (face.std() + 1e-7)

def load_dataset(folder=CAPTURE_DIR):
    """Load and preprocess the dataset."""
    images, labels = [], []
    for file in os.listdir(folder):
        if file.lower().endswith(('.jpg', '.png')):
            path = os.path.join(folder, file)
            img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
            processed = preprocess_image(img)
            if processed is not None:
                images.append(processed)
                labels.append(file.split('_')[0])
    return np.array(images), np.array(labels)

def create_model(num_classes):
    """Build the CNN model."""
    model = Sequential([
        Conv2D(32, (3, 3), padding='same', input_shape=(IMG_SIZE, IMG_SIZE, 3)), BatchNormalization(),
        Conv2D(32, (3, 3), padding='same', activation='relu'), BatchNormalization(),
        MaxPooling2D((2, 2)), Dropout(0.25),

        Conv2D(64, (3, 3), padding='same'), BatchNormalization(),
        Conv2D(64, (3, 3), padding='same', activation='relu'), BatchNormalization(),
        MaxPooling2D((2, 2)), Dropout(0.25),

        Conv2D(128, (3, 3), padding='same'), BatchNormalization(),
        Conv2D(128, (3, 3), padding='same', activation='relu'), BatchNormalization(),
        MaxPooling2D((2, 2)), Dropout(0.25),

        Conv2D(256, (3, 3), padding='same'), BatchNormalization(),
        Conv2D(256, (3, 3), padding='same', activation='relu'), BatchNormalization(),
        MaxPooling2D((2, 2)), Dropout(0.25),

        Flatten(),
        Dense(512, activation='relu'), BatchNormalization(), Dropout(0.5),
        Dense(256, activation='relu'), BatchNormalization(), Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    return model

def train_face_recognition():
    """Train the CNN model."""
    X, y = load_dataset()
    if X.size == 0:
        print("Khong tim thay du lieu training!")
        return None, None

    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    y_cat = to_categorical(y_enc)

    X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest'
    )

    model = create_model(len(le.classes_))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=20, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=10, min_lr=1e-6, verbose=1)
    ]

    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=32),
        epochs=100,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1
    )

    plot_training_results(history)
    return model, le

def plot_training_results(history):
    """Plot training accuracy and loss."""
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train')
    plt.plot(history.history['val_accuracy'], label='Validation')
    plt.title('Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train')
    plt.plot(history.history['val_loss'], label='Validation')
    plt.title('Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.savefig('training_results.png')
    plt.close()
    print("\nSaved training plot to 'training_results.png'")

def capture_training_images(student_id, num_images=10):
    """Capture training images from webcam."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Khong the mo camera!")
        return False

    print(f"\nDang chup {num_images} anh cho sinh vien: {student_id}")
    time.sleep(2)
    images_captured = 0

    while images_captured < num_images:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        box = 300
        cv2.rectangle(frame, (cx - box // 2, cy - box // 2), (cx + box // 2, cy + box // 2), (255, 255, 255), 2)
        cv2.putText(frame, f"IMG {images_captured + 1}/{num_images}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE: take - Q: exit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Capture", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            filename = os.path.join(CAPTURE_DIR, f"{student_id}_{images_captured + 1}.jpg")
            cv2.imwrite(filename, frame)
            images_captured += 1
            time.sleep(0.5)
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if images_captured < num_images:
        print(f"\nChi chup duoc {images_captured}/{num_images} anh")
        return False

    print("\nHoan thanh chup anh")
    return True

if __name__ == "__main__":
    student_id = input("Nhap ma so sinh vien: ").strip()
    if not student_id:
        print("Ma so sinh vien khong duoc de trong!")
        exit()

    print("\nHuong dan:")
    print("- Dat mat vao khung trang")
    print("- Nhấn SPACE de chup, Q de huy")

    if capture_training_images(student_id):
        print("\nDang huan luyen mo hinh...")
        model, le = train_face_recognition()
        if model:
            print("\nHoan tat! Mo hinh san sang su dung.")
    else:
        print("\nChup anh that bai hoac huy bo.")
