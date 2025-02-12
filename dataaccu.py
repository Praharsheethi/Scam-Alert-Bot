import pandas as pd
from sklearn.utils import resample
import random

# Load the dataset
df = pd.read_csv("data/augmented_labeled_messages.csv")

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

# Balance the dataset
scam_messages = df[df['label'] == 1]
non_scam_messages = df[df['label'] == 0]

if len(scam_messages) > len(non_scam_messages):
    scam_messages = resample(scam_messages, n_samples=len(non_scam_messages), random_state=42)
else:
    non_scam_messages = resample(non_scam_messages, n_samples=len(scam_messages), random_state=42)

# Combine the balanced datasets
df = pd.concat([scam_messages, non_scam_messages])

# Save the cleaned and balanced dataset
df.to_csv("data/cleaned_balanced_messages.csv", index=False)

print("Yes working")