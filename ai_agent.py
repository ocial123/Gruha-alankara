import os
import json
from PIL import Image
from transformers import pipeline
import asyncio
import edge_tts
from langchain.llms import HuggingFaceHub
from cv_analyzer import get_latest_context
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
        
        # Retrieve context from cv_analyzer
        context = get_latest_context()
        lighting = context.get('lighting', 'dim')
        style = context.get('style', 'Modern')
        furnished_status = context.get('furnished_status', 'furnished')
        
        # Step 2: Agentic AI
        room_keywords = ['room', 'interior', 'furniture', 'bed', 'sofa', 'chair', 'table', 'floor', 'wall', 'living', 'kitchen', 'dining', 'bedroom', 'office', 'desk', 'house', 'plant']
        is_valid_room = any(k in room_description.lower() for k in room_keywords)

        if not is_valid_room:
            ai_text = "Please upload a valid room image. The room is not visible."
            ai_output = {
                "analysis": room_description,
                "theme": theme,
                "recommendations": ai_text
            }
        else:
            instruction = "starting pieces" if furnished_status == "empty" else "matching upgrades"
            prompt = (
                f"You are a strict interior design AI.\n"
                f"Image Description: {room_description}\n"
                f"The room is {furnished_status} with a {style} style and {lighting} lighting. Theme: {theme}. Provide a 2-sentence recommendation for {instruction}."
            )
                
            ai_text = llm.invoke(prompt).strip()
            
            ai_output = {
                "analysis": room_description,
                "theme": theme,
                "recommendations": ai_text
            }
            
    except Exception as e:
        print(f"Model Error: {e}")
        context = get_latest_context()
        desc = locals().get('room_description', 'your space')
        if not any(k in desc.lower() for k in ['room', 'interior', 'furniture', 'bed', 'sofa', 'table', 'floor', 'wall']):
            ai_text = "Please upload a valid room image. The room is not visible."
        elif context.get('furnished_status') == "empty":
            ai_text = f"I see {desc}. Based on the {theme} theme, I recommend starting with key foundational pieces and {context.get('lighting', 'warm')} lighting to establish the room."
        else:
            ai_text = f"I see {desc}. Based on the {theme} theme, I recommend adding matching upgrades and {context.get('lighting', 'warm')} lighting to complement your space."
        ai_output = {"error": str(e), "recommendations": ai_text}

    # Step 3: Multilingual Voice Assistant
    if language == 'hi':
        ai_text = "मैंने आपके कमरे का विश्लेषण किया है। " + ai_text
        voice = 'hi-IN-SwaraNeural'
    elif language == 'te':
        ai_text = "నేను మీ గదిని విశ్లేషించాను. " + ai_text
        voice = 'te-IN-ShrutiNeural'
    else:
        voice = 'en-US-AriaNeural'

    audio_filename = f"audio_{filename.split('.')[0]}.mp3"
    audio_path = os.path.join('static', 'uploads', audio_filename)
    
    try:
        import subprocess
        # Use subprocess to strictly bypass Python asyncio thread conflicts running in Gunicorn
        subprocess.run(["edge-tts", "--text", ai_text, "--voice", voice, "--write-media", audio_path], check=True)
    except Exception as e:
        print(f"Audio Error: {e}")

    return json.dumps(ai_output), audio_filename, filename