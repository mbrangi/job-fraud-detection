import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report

# Train the model
clf = RandomForestClassifier(class_weight="balanced")
clf.fit(train_X_num, train_Y)

# Predict
pred = clf.predict(test_X_num)

# Existing evaluation
evaluate(test_Y, pred)

# Confusion Matrix
cm = confusion_matrix(test_Y, pred)
print("Confusion Matrix:")
print(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(test_Y, pred))

# Plot confusion matrix heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=clf.classes_, yticklabels=clf.classes_)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix Heatmap')
plt.tight_layout()
plt.show()
