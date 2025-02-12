import gradio as gr
from app import analyze_investment_scam, fetch_channel_messages, send_alert_to_all
import asyncio

# Define the analyze_text function
def analyze_text(text):
    # Use the analyze_investment_scam function for text analysis
    scam_detected, sentiment_score = analyze_investment_scam(text)
    result = {
        "text": text,
        "scam_detected": scam_detected,
        "sentiment_score": sentiment_score,
    }
    # Send alert if scam is detected
    if scam_detected:
        asyncio.run(send_alert_to_all(text))  # Send alert to all users including this user
    return result

# Define the async fetch_messages function
async def fetch_messages(channel_name):
    messages = await fetch_channel_messages(channel_name.strip())
    
    if not messages or isinstance(messages, str):
        return "Error: Unable to fetch messages. Please check the channel username."
    
    results = []
    for message in messages:
        scam_detected, sentiment_score = analyze_investment_scam(message.get('text', ''))
        result = f"{message.get('text', 'No text')} - {'Scam Detected!' if scam_detected else 'Normal message.'}"
        results.append(result)
    
    return "\n".join(results)

# Create Gradio interfaces
text_interface = gr.Interface(
    fn=analyze_text,  # Correctly reference the analyze_text function
    inputs="text",
    outputs="json",
    title="Telegram Scam Detector",
)

channel_interface = gr.Interface(
    fn=fetch_messages,
    inputs="text",
    outputs="text",
)

# Launch both interfaces in tabs and open in the browser
gr.TabbedInterface([text_interface, channel_interface]).launch(share=True, inbrowser=True)