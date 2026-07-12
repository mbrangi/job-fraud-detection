"""
Train a bilingual (English + Swahili) fake job detection model.
Uses the same architecture as the original model1.pkl but with
improved preprocessing for mixed-language text.

Output: models/bilingual_model.pkl
"""

import os, re, pickle, json
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from tensorflow.keras.preprocessing.text import hashing_trick
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from sklearn.model_selection import train_test_split

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

SEED = 42
np.random.seed(SEED)

# ── Swahili stopwords ──────────────────────────────────────────────
SWAHILI_STOPWORDS = {
    'na', 'ya', 'wa', 'kwa', 'ni', 'katika', 'la', 'za', 'kutoka', 'hii',
    'hiyo', 'huo', 'hizo', 'hizi', 'watu', 'kama', 'mara', 'pia',
    'kwenye', 'au', 'lakini', 'bado', 'si', 'wala', 'hata', 'kila',
    'baada', 'kabla', 'zaidi', 'kati', 'hadi', 'tangu', 'mpaka', 'ndani',
    'nje', 'juu', 'chini', 'mbele', 'nyuma', 'sana', 'kidogo', 'kubwa',
    'ndogo', 'moja', 'mbili', 'tatu', 'nne', 'tano', 'sita', 'saba',
    'nane', 'tisa', 'kumi', 'hivyo', 'vile', 'hao', 'ambao', 'ambayo',
    'ambacho', 'ambalo', 'ambazo', 'ambawo', 'wake', 'zake', 'lake',
    'yake', 'chake', 'vyake', 'mzuri', 'zuri', 'nzuri', 'wangu', 'zangu',
    'langu', 'yangu', 'changu', 'vyangu', 'yetu', 'wetu', 'zetu', 'letu',
    'chetu', 'vyetu', 'enu', 'wenu', 'zenu', 'lenu', 'chenu', 'vyenu',
    'ao', 'wao', 'zao', 'lao', 'yao', 'chao', 'vyao', 'mimi', 'wewe',
    'yeye', 'sisi', 'nyinyi', 'huu', 'hili', 'haya', 'huku', 'huko',
    'humu', 'huno', 'wapi', 'lini', 'nini', 'kitu', 'vitu', 'mtu',
    'maji', 'moto', 'nyumba', 'kazi', 'siku', 'mwaka', 'mwezi', 'wiki',
    'saa', 'dakika', 'wakati', 'mahali', 'njia', 'jina', 'sababu',
    'matokeo', 'urahisi', 'haraka', 'tena', 'kabisa', 'pamoja', 'pekee',
    'hasa', 'karibu', 'mbali', 'bila', 'kupitia', 'kuelekea', 'kuwa',
    'kuna', 'kuko', 'pana', 'pako', 'kumekuwa', 'kulikuwa', 'kunako',
    'siyo', 'sio', 'ndiyo', 'ndio', 'ndilo', 'ndicho', 'kwamba', 'kwani',
    'maana', 'kwasababu', 'ili', 'kisha', 'ndipo', 'hapo', 'pale',
    'kule', 'hapa', 'humi',
}

# ── Parameters ─────────────────────────────────────────────────────
VOC_SIZE = 5000
MAX_LEN = 40
EPOCHS = 12
BATCH_SIZE = 64
EMBED_DIM = 50

# ── Load bilingual dataset ─────────────────────────────────────────
data_path = os.path.join(os.path.dirname(__file__), 'data', 'bilingual_job_ads.csv')
print(f"Loading dataset from {data_path}")

df = pd.read_csv(data_path)
df = df[['description', 'fraudulent']].dropna()
df['fraudulent'] = df['fraudulent'].astype(int)

print(f"Total: {len(df)} rows")
print(f"Fake: {df['fraudulent'].sum()}, Legit: {len(df) - df['fraudulent'].sum()}")

# ── Preprocessing ───────────────────────────────────────────────────
def preprocess(text):
    ps = PorterStemmer()
    text = re.sub(r'[^a-zA-Zà-ÿ\u00C0-\u00FF]', ' ', str(text))
    text = text.lower().split()
    stop_words = set(stopwords.words('english')) | SWAHILI_STOPWORDS
    result = []
    for word in text:
        if word not in stop_words and len(word) > 2:
            stemmed = ps.stem(word)
            result.append(stemmed if len(stemmed) < len(word) else word)
    return ' '.join(result)

print("Preprocessing text...")
corpus = df['description'].apply(preprocess).tolist()

# ── One-hot encode ─────────────────────────────────────────────────
print("One-hot encoding (md5, deterministic)...")
onehot_repr = [hashing_trick(text, VOC_SIZE, hash_function='md5') for text in corpus]

# ── Pad sequences ───────────────────────────────────────────────────
print(f"Padding to max length {MAX_LEN}...")
embedded_docs = pad_sequences(onehot_repr, padding='pre', maxlen=MAX_LEN)

# ── Train/Test split ────────────────────────────────────────────────
X = np.array(embedded_docs)
y = np.array(df['fraudulent'])
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)
print(f"Train: {len(X_train)}, Test: {len(X_test)}")
print(f"Train fake ratio: {y_train.mean():.3f}, Test fake ratio: {y_test.mean():.3f}")

# ── Build model ─────────────────────────────────────────────────────
print("Building model...")
model = Sequential()
model.add(Embedding(VOC_SIZE, EMBED_DIM, input_length=MAX_LEN))
model.add(Bidirectional(LSTM(100)))
model.add(Dropout(0.3))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.build(input_shape=(None, MAX_LEN))
print(model.summary())

# ── Train ───────────────────────────────────────────────────────────
print(f"Training for {EPOCHS} epochs...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=1,
)

# ── Evaluate ────────────────────────────────────────────────────────
y_pred = (model.predict(X_test) > 0.5).astype(int)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print(f"\n── Results ──")
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall:    {rec:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"Confusion Matrix:\n{cm}")

# ── Save model ──────────────────────────────────────────────────────
out_dir = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(out_dir, exist_ok=True)
model_path = os.path.join(out_dir, 'bilingual_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

# Save training metadata
meta = {
    'voc_size': VOC_SIZE,
    'max_len': MAX_LEN,
    'embed_dim': EMBED_DIM,
    'epochs': EPOCHS,
    'batch_size': BATCH_SIZE,
    'accuracy': float(acc),
    'precision': float(prec),
    'recall': float(rec),
    'f1': float(f1),
    'train_samples': int(len(X_train)),
    'test_samples': int(len(X_test)),
    'swahili_stopwords_count': len(SWAHILI_STOPWORDS),
}
meta_path = os.path.join(out_dir, 'bilingual_model_meta.json')
with open(meta_path, 'w') as f:
    json.dump(meta, f, indent=2)

print(f"\nModel saved to: {model_path}")
print(f"Metadata saved to: {meta_path}")
