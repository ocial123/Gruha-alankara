import os
import json
from PIL import Image
from transformers import pipeline
from gtts import gTTS
from langchain.llms import HuggingFaceHub
from dotenv import load_dotenv

# Load the API token from your .env file
load_dotenv()

# 1. Vision Model (Kept lightweight for local image-to-text conversion)
vision_analyzer = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

# 2. Cloud AI via Hugging Face (No local RAM used for text generation)
llm = HuggingFaceHub(
    repo_id="ibm-granite/granite-7b-instruct", 
    model_kwargs={"temperature": 0.7, "max_new_tokens": 100}
)

def process_room_design(filename, theme, language='en'):
    image_path = os.path.join('static', 'uploads', filename)
    
    try:
        # Step 1: Computer Vision Analysis
        img = Image.open(image_path).convert('RGB')
        room_description = vision_analyzer(img)[0]['generated_text']
        
        # Step 2: Agentic AI 
        prompt = f"Act as an interior designer. Room: {room_description}. Theme: {theme}. Give a 2-sentence furniture recommendation."
        ai_text = llm.invoke(prompt).strip()
        
        ai_output = {
            "analysis": room_description,
            "theme": theme,
            "recommendations": ai_text
        }
        
    except Exception as e:
        print(f"Model Error: {e}")
        ai_text = f"Based on the {theme} theme, I recommend adding matching furniture and warm lighting to complement your space."
        ai_output = {"error": str(e), "recommendations": ai_text}

    # Step 3: Multilingual Voice Assistant
    if language == 'hi':
        ai_text = "मैंने आपके कमरे का विश्लेषण किया है। " + ai_text
    elif language == 'te':
        ai_text = "నేను మీ గదిని విశ్లేషించాను. " + ai_text

    audio_filename = f"audio_{filename.split('.')[0]}.mp3"
    audio_path = os.path.join('static', 'uploads', audio_filename)
    
    try:
        tts = gTTS(text=ai_text, lang=language[:2])
        tts.save(audio_path)
    except Exception as e:
        print(f"Audio Error: {e}")

    return json.dumps(ai_output), audio_filename, filename