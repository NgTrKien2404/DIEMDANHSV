import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.regularizers import l2
import matplotlib.pyplot as plt

def load_dataset(folder="capture/train_data"):
    images = []
    labels = []
    for filename in os.listdir(folder):
        if filename.endswith((".jpg", ".png")):
            img_path = os.path.join(folder, filename)
            img = cv2.imread(img_path)
            img = cv2.resize(img, (96, 96))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.astype('float32') / 255.0  # CHUẨN HÓA ẢNH
            images.append(img)
            # Giả sử tên file là maSV_xxx.jpg
            label = filename.split("_")[0]
            labels.append(label)
    return np.array(images), np.array(labels)

def create_model(num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(96, 96, 3)),
        MaxPooling2D((2, 2)),
        Dropout(0.2),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Dropout(0.2),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    return model

def train_face_recognition():
    X, y = load_dataset()

    # Loại bỏ các lớp có ít hơn 2 ảnh
    unique, counts = np.unique(y, return_counts=True)
    valid_classes = unique[counts >= 2]
    mask = np.isin(y, valid_classes)
    X = X[mask]
    y = y[mask]

    if len(np.unique(y)) < 2:
        raise ValueError("Cần ít nhất 2 lớp (mỗi lớp >= 2 ảnh) để train. Vui lòng bổ sung dữ liệu.")

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    y_categorical = to_categorical(y_encoded)
                   
    # Split dataset
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_categorical, test_size=0.3, random_state=42, stratify=y
    )

    # Data Augmentation
    datagen = ImageDataGenerator(
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True
    )
    datagen.fit(X_train)

    # Create and compile model
    model = create_model(len(le.classes_))
    model.compile(
        optimizer=Adam(learning_rate=0.0005),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # Early stopping callback
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,  # Tăng từ 10 lên 15
        restore_best_weights=True,
        min_delta=0.001  # Thêm ngưỡng tối thiểu để xem xét cải thiện
    )
    
    # Learning rate reduction callback
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,  # Tăng từ 5 lên 8
        min_lr=1e-5,
        verbose=1  # Thêm để theo dõi thay đổi learning rate
    )
    
    # Model checkpoint callback
    checkpoint = ModelCheckpoint(
        'best_model.keras',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
    
    # Train model with augmentation
    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=16),
        epochs=50,
        validation_data=(X_val, y_val),
        callbacks=[early_stopping, reduce_lr, checkpoint]
    )

    # Lưu model và label encoder
    model.save('face_recognition_model.keras')
    label_dict = dict(enumerate(le.classes_))
    np.save('label_encoder.npy', label_dict)

    # Vẽ lại biểu đồ
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.tight_layout()
    plt.show()

    print("Model and label encoder saved successfully")
    print(f"Label mapping: {label_dict}")
    return model, label_dict

if __name__ == "__main__":
    train_face_recognition()