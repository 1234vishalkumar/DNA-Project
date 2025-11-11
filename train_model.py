# train_model.py — Final Version (with rare-class fix)

import pandas as pd
import numpy as np
import os, json, joblib
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

# -----------------------------
# Configuration
# -----------------------------
DATA_PATH = "dataset/human.txt"   # dataset path
ARTIFACT_DIR = "model"
K = 6  # K-mer length (change to 4 or 7 to experiment)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# -----------------------------
# Step 1: Load dataset
# -----------------------------
df = pd.read_csv(DATA_PATH, sep="\t", header=None, names=["sequence", "label"])
print("✅ Dataset loaded! Shape:", df.shape)
df.dropna(inplace=True)

# -----------------------------
# Step 2: Clean sequences
# -----------------------------
df["sequence"] = df["sequence"].astype(str).str.upper().str.replace("[^ATGC]", "", regex=True)
print("✅ Cleaned sequences. Shape:", df.shape)

# -----------------------------
# Step 3: Encode labels
# -----------------------------
le = LabelEncoder()
df["label_enc"] = le.fit_transform(df["label"].astype(str))
label_map = {int(i): cls for i, cls in enumerate(le.classes_)}
print("✅ Labels encoded:", label_map)

# -----------------------------
# Step 4: Remove rare classes (important fix)
# -----------------------------
label_counts = df["label_enc"].value_counts()
df = df[df["label_enc"].isin(label_counts[label_counts >= 2].index)]
print("✅ Removed rare classes. Remaining samples:", len(df))

# -----------------------------
# Step 5: K-mer extraction
# -----------------------------
def get_kmers(seq, k=K):
    return [seq[i:i+k] for i in range(len(seq)-k+1)] if len(seq) >= k else []

# Build vocabulary
all_kmers = []
for s in df["sequence"]:
    all_kmers.extend(get_kmers(s, K))
VOCAB = sorted(set(all_kmers))
print("✅ Vocabulary size:", len(VOCAB))

vocab_index = {kmer: i for i, kmer in enumerate(VOCAB)}

def seq_to_vector(seq, k=K):
    vec = [0]*len(VOCAB)
    for kmer in get_kmers(seq, k):
        idx = vocab_index.get(kmer)
        if idx is not None:
            vec[idx] += 1
    s = sum(vec)
    return [v/s if s>0 else 0 for v in vec]

# Convert sequences to features
print("🔄 Converting sequences to feature vectors (this may take a minute)...")
X = np.array([seq_to_vector(s) for s in df["sequence"]])
y = df["label_enc"].values
print("✅ Features ready. Shape:", X.shape)

# -----------------------------
# Step 6: Split & scale
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# Step 7: Train model
# -----------------------------
model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)

acc = accuracy_score(y_test, y_pred)
print(f"🎯 Model Accuracy: {acc:.4f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# -----------------------------
# Step 8: Confusion Matrix
# -----------------------------
plt.figure(figsize=(5,4))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# -----------------------------
# Step 9: Save Artifacts
# -----------------------------
joblib.dump(model, os.path.join(ARTIFACT_DIR, "best_model.pkl"))
joblib.dump(scaler, os.path.join(ARTIFACT_DIR, "scaler.pkl"))

with open(os.path.join(ARTIFACT_DIR, "kmer_vocab.json"), "w") as f:
    json.dump({"K": K, "VOCAB": VOCAB}, f, indent=2)

with open(os.path.join(ARTIFACT_DIR, "label_info.json"), "w") as f:
    json.dump({"label_map": label_map}, f, indent=2)

print("✅ Model and artifacts saved successfully in:", ARTIFACT_DIR)
