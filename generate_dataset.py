import pandas as pd
import random
import nlpaug.augmenter.word as naw

# Initialize Synonym Augmenter
syn_aug = naw.SynonymAug(aug_p=0.3)  # 30% words replaced with synonyms

# Lists of messages
suspicious_messages = [
    "Get rich quick with this investment opportunity!",
    "Free crypto giveaway, send your wallet address!",
    "Earn money without doing anything, sign up now!",
    "Investment in crypto is guaranteed to make you rich!",
    "Claim your prize by sending your details now!",
    "Hurry up! Limited offer to make quick money!",
    "Click here to unlock your free vacation prize!",
    "Pay now and double your money instantly!",
    "Invest in this high-return crypto project!",
    "Exclusive offer to join the crypto revolution!"
]

non_suspicious_messages = [
    "Hello, how are you?",
    "Let's grab coffee sometime!",
    "Good morning, everyone!",
    "Did you see the new movie last night?",
    "Can you recommend a good restaurant?",
    "Looking forward to our meeting tomorrow.",
    "How was your weekend?",
    "I'm going to the gym later, want to join?",
    "What do you think about the latest sports game?",
    "Can you send me the presentation from last week?"
]

# Function to generate augmented messages
def augment_messages(messages, label, num_samples=1500):
    augmented_data = []
    for _ in range(num_samples):
        original_msg = random.choice(messages)
        augmented_msg = syn_aug.augment(original_msg)  # Apply Synonym Augmentation
        augmented_data.append([augmented_msg, label])
    return augmented_data

# Generate 1,500 suspicious and 1,500 non-suspicious messages
messages = augment_messages(suspicious_messages, 1, 1500) + augment_messages(non_suspicious_messages, 0, 1500)

# Shuffle the dataset
random.shuffle(messages)

# Create a DataFrame
df = pd.DataFrame(messages, columns=["message", "label"])

# Save to CSV
df.to_csv("data/augmented_labeled_messages.csv", index=False)

print("Augmented dataset with 3,000 messages has been generated and saved.")
