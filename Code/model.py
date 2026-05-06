'''
Plant Disease Classification Training Pipeline

This script downloads a disease image dataset, prepares it for training, builds a convolutional neural network usign transfer learning (MobileNetV2),
and trains a model to classify crop diseases from leaf images

Pipeline steps:
1. Download dataset from KaggleHub
2. Verify dataset structure (train/validation directories)
3. Load images using tf.keras image_dataset_from_directory
4. Cache, shuffle, and prefetch data
5. Build a transfer learning model using MobileNetV2
6. Train the model in two phases:
    - Initial training with frozen base model
    - Fine-tuning with partial unfreezing
7. Save trained model and class labels for prediction use

Key Components:
    - Dataset: PlantVillage (KaggleHub)
    - Input size: 128x128 RGB images
    - Model: MobileNetV2
    - Optimisation: Adam optimizer with transfer learning strategy
    - Output: Trained .keras model + class_names.txt file

Outputs:
    - crop_disease_model.keras (trained model)
    - class_names.txt (mapping of class indices to labels)
'''

import pathlib
import os
import kagglehub
import tensorflow as tf


#Download dataset from kagglehub

print("Downloading dataset...")
path = kagglehub.dataset_download("mohitsingh1804/plantvillage")
print(f"Dataset downloaded to: {path}")

print(f"Train path: {pathlib.Path(path) / 'PlantVillage' / 'train'}")
print(f"Train exists: {(pathlib.Path(path) / 'PlantVillage' / 'train').exists()}")
print(f"Val path: {pathlib.Path(path) / 'PlantVillage' / 'val'}")
print(f"Val exists: {(pathlib.Path(path) / 'PlantVillage' / 'val').exists()}")

#Locate the subfolders from the download path

train_dir = pathlib.Path(path) / "PlantVillage" / "train"
val_dir = pathlib.Path(path)/ "PlantVillage" / "val"

#Load dataset

train_data = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    seed = 42,
    image_size = (128, 128),
    batch_size = 16
)

val_data = tf.keras.utils.image_dataset_from_directory(
    val_dir,
    seed = 42,
    image_size = (128, 128),
    batch_size = 16
)

#Save class names
class_names = train_data.class_names

with open('class_names.txt', 'w') as f:
    f.write("\n".join(class_names))

#Tune performance

AUTOTUNE = tf.data.AUTOTUNE
train_data = train_data.cache().shuffle(1000).prefetch(buffer_size = AUTOTUNE)
val_data = val_data.cache().prefetch(buffer_size = AUTOTUNE)

#Build model
base_model = tf.keras.applications.MobileNetV2(
    input_shape = (128, 128, 3),
    include_top = False,
    weights = 'imagenet'
)

base_model.trainable = False #freeze pretrained weights

model = tf.keras.Sequential([
    tf.keras.layers.Lambda(
        lambda x: tf.keras.applications.mobilenet_v2.preprocess_input(x)
    ),
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer="adam",
    loss = "sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

#Train
print("Training...")
model.fit(train_data,  validation_data= val_data, epochs = 10)

base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False  # keep early layers frozen

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),  # much lower LR
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)
print("Phase 2 fine-tuning...")
model.fit(train_data, validation_data=val_data, epochs=10)

model.save("crop_disease_model.keras")
print("Model saved")
