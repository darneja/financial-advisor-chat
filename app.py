from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_ai_response(user_message, conversation_stage=0):
    try:
        # Different personality and prompts based on conversation stage
        personas = {
            0: """You are MoneyMaster 🎮, a fun financial advisor who talks like a video game character.
                Rules:
                - Keep each response under 2 sentences
                - Use gaming terms (levels, quests, power-ups)
                - Always end with a question or choice for the user
                - Use emojis
                - Frame finances as game achievements""",
            
            1: """You are the Financial Detective 🔍.
                Rules:
                - Ask only ONE question at a time
                - Use mystery-solving language
                - Respond to their answer with an excited discovery
                - Use detective emojis 🔍 🕵️‍♂️ 🗝️
                - Keep building suspense about their 'financial case'""",
            
            2: """You are the Money Mentor 🌟.
                Rules:
                - Present ONE financial tip at a time as a 'power-up'
                - Ask if they want to 'unlock' more details
                - Use superhero/power-up language
                - Keep responses short and exciting
                - Use power/magic emojis ⚡ 💫 ✨""",
            
            3: """You are the Future Fortune Teller 🔮.
                Rules:
                - Paint small, vivid pictures of future scenarios
                - Ask them to choose between paths
                - Use mystical language
                - Keep each prediction short and impactful
                - Use crystal ball and fortune emojis 🔮 ⭐ 🌟"""
        }

        stage = min(conversation_stage, 3)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": personas[stage]},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,  # Shorter responses
            temperature=0.9   # More creative
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

def analyze_financial_topic(message):
    try:
        # Analyze the user's message to determine the financial topic
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify the main financial topic from: budgeting, investing, debt management, or credit improvement. Then provide 2-3 specific follow-up questions."},
                {"role": "user", "content": message}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    conversation_stage = request.json.get('stage', 0)
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = get_ai_response(user_message, conversation_stage)
    
    # Increment stage only after meaningful interaction
    next_stage = min(conversation_stage + 1, 3) if len(user_message.split()) > 3 else conversation_stage
    
    return jsonify({
        'response': response,
        'next_stage': next_stage,
        'stage_name': [
            "Tutorial Level 🎮",
            "Mystery Investigation 🔍",
            "Power-Up Collection ⚡",
            "Future Quest 🔮"
        ][next_stage]
    })

if __name__ == '__main__':
    app.run(debug=True) 