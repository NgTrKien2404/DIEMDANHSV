import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def load_dataset(folder="faces"):
    images = []
    labels = []
    
    for filename in os.listdir(folder):
        if filename.endswith((".jpg", ".png")):
            # Đọc và resize ảnh về kích thước cố định
            img_path = os.path.join(folder, filename)
            img = cv2.imread(img_path)
            img = cv2.resize(img, (96, 96))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Normalize ảnh
            img = img / 255.0
            
            # Lấy student_id từ tên file
            student_id = os.path.splitext(filename)[0]
            
            images.append(img)
            labels.append(student_id)
    
    return np.array(images), np.array(labels)

def create_model(num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(96, 96, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    return model

def train_face_recognition():
    # Load dataset
    X, y = load_dataset()
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    y_categorical = to_categorical(y_encoded)
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_categorical, test_size=0.2, random_state=42
    )
    
    # Create and compile model
    model = create_model(len(le.classes_))
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train model
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test)
    )
    
    # Save model and label encoder
    model.save('face_recognition_model.h5')
    np.save('label_encoder.npy', le.classes_)
    
    # Evaluate model
    test_loss, test_acc = model.evaluate(X_test, y_test)
    print(f"\nĐộ chính xác trên tập test: {test_acc*100:.2f}%")

if __name__ == "__main__":
    train_face_recognition()