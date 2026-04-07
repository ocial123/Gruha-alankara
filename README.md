---
title: Gruha Alankara
emoji: 🛋️
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🛋️ Gruha Alankara

Welcome to **Gruha Alankara**, an AI-powered AR Interior Design application. Instantly see how beautiful furniture fits into your real space using advanced computer vision and Agentic AI! 

## ✨ Key Features
- 📷 **AR Visualizer**: Use your mobile camera to see how furniture fits and looks in your actual room instantly.
- 🗣️ **Multilingual Voice Assistant**: Interact naturally with your AI Buddy using voice commands in Telugu, Hindi, or English.
- 📊 **User Dashboard**: Manage your designs, saved layouts, and preferences through a dedicated, personalized dashboard interface.

## 🧰 Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla CSS3, JavaScript
- **AI/ML**: Agentic AI frameworks & local Hugging Face Transformers (`blip-image-captioning-base`) for personalized spatial recommendations.
- **Deployment**: Hugging Face Spaces (Dockerized)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ocial123/Gruha-alankara.git
   cd Gruha-alankara
   ```

2. **Install dependencies:**
   Make sure you have Python 3.10+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Hugging Face API Token (needed for the AI agent):
   ```env
   HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
   SECRET_KEY=super-secret-gruha-key
   ```

4. **Run the application locally:**
   ```bash
   python app.py
   ```
   *The application will launch locally at `http://localhost:5000`.*

---

## 📂 Architecture & Structure
- `app.py`: The main entry point and route handler for the Flask web application.
- `ai_agent.py`: Handles AI pipeline integrations, computer vision, text-generation logic, and voice synthesis.
- `models.py`: Defines the SQLAlchemy database schemas for Users, Designs, Bookings, and Furniture.
- `config.py`: Application configurations and cross-site cookie settings (required for Hugging Face Spaces iframes).
- `Dockerfile`: Production deployment instructions utilized by Hugging Face Spaces to build the container.
