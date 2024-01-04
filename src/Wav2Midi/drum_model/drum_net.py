import librosa
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from sklearn.metrics import confusion_matrix, classification_report
from keras.regularizers import l2
from keras.layers import Dense, Dropout, Flatten, Conv1D, MaxPooling1D
from keras.models import Sequential
from keras.callbacks import EarlyStopping
from utils import extract_features_file

# Base directory containing the sample pack
base_dir = 'MDB_subset/kit'

# Define max padding length
max_pad_len = 174

# Get labels and features
labels = []
features = []

for label in os.listdir(base_dir):
    # Ensure we're only processing directories
    if os.path.isdir(os.path.join(base_dir, label)):
        for file in os.listdir(os.path.join(base_dir, label)):
            # Load and extract features for each audio file
            file_path = os.path.join(base_dir, label, file)
            if file_path.lower().endswith('.wav'):
                data = extract_features_file(file_path)
                if data is not None:
                    features.append(data)
                    labels.append(label)

# Convert features and labels to numpy arrays
features = np.array(features)
labels = np.array(labels)

# Encode the classification labels
le = LabelEncoder()
labels_encoded = to_categorical(le.fit_transform(labels))

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(features, labels_encoded, test_size=0.2, random_state=42)

# Print how many samples of each category we have in our training and testing data
print("Training samples:")
unique_elements, counts_elements = np.unique(np.argmax(y_train, axis=1), return_counts=True)
print(np.asarray((unique_elements, counts_elements)))

print("Testing samples:")
unique_elements, counts_elements = np.unique(np.argmax(y_test, axis=1), return_counts=True)
print(np.asarray((unique_elements, counts_elements)))

# Number of labels
num_labels = y_train.shape[1]

# Build the model
model = Sequential()
model.add(Conv1D(64, 3, activation='relu', input_shape=(40, max_pad_len)))
model.add(Conv1D(64, 3, activation='relu'))
model.add(MaxPooling1D(3))
model.add(Dropout(0.5))  # added dropout layer
model.add(Conv1D(128, 3, activation='relu', kernel_regularizer=l2(0.01)))  # added L2 regularization
model.add(Conv1D(128, 3, activation='relu', kernel_regularizer=l2(0.01)))  # added L2 regularization
model.add(MaxPooling1D(3))
model.add(Dropout(0.5))  # added dropout layer
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_labels, activation='softmax'))

# Compile the model
model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='adam')

# Define early stopping
early_stopping = EarlyStopping(monitor='val_loss', patience=10)

# Train the model
model.fit(X_train, y_train, epochs=100, validation_data=(X_test, y_test), verbose=1, callbacks=[early_stopping])

# Evaluate the model
score = model.evaluate(X_test, y_test, verbose=0)
print("Test Loss:", score[0])
print("Test Accuracy:", score[1])

# Save the model
model.save('drum_model.keras')

# Predict on test data
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true = np.argmax(y_test, axis=1)

# Generate a confusion matrix
cm = confusion_matrix(y_true, y_pred_classes)

# Print the confusion matrix
print("Confusion Matrix:")
print(cm)

# Generate a classification report
cr = classification_report(y_true, y_pred_classes, target_names=le.classes_)

# Print the classification report
print("Classification Report:")
print(cr)