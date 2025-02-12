import joblib
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import random

nltk.download('vader_lexicon')

# Load the dataset
df = pd.read_csv("data/dataset.csv")

# Check for duplicates
print("Number of duplicates:", df.duplicated().sum())

# Remove duplicates
df = df.drop_duplicates()

# Add noise to the dataset
def add_noise(text):
    if random.random() < 0.1:  # 10% chance of adding noise
        words = text.split()
        random.shuffle(words)
        return ' '.join(words)
    return text

df['message'] = df['message'].apply(add_noise)

# Preprocessing function
def preprocess_text(text):
    return text.lower()

# Apply preprocessing
df['message'] = df['message'].apply(preprocess_text)

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)  # Limit features for speed

# Split the data into train (80%) and test (20%)
X_train, X_test, y_train, y_test = train_test_split(
    df['message'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# Vectorize the training and test sets
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Train a Naive Bayes model
model = MultinomialNB()
model.fit(X_train_vectorized, y_train)

# Perform cross-validation
cv_scores = cross_val_score(model, X_train_vectorized, y_train, cv=5, scoring='accuracy')
print("Cross-validation scores:", cv_scores)
print("Mean CV accuracy:", cv_scores.mean())

# Evaluate on the training set
train_pred = model.predict(X_train_vectorized)
print("Training Accuracy:", accuracy_score(y_train, train_pred))

# Evaluate on the test set
test_pred = model.predict(X_test_vectorized)
print("Test Accuracy:", accuracy_score(y_test, test_pred))
print("Classification Report:")
print(classification_report(y_test, test_pred))

# Save the model and vectorizer
joblib.dump(model, 'scam_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')