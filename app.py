from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = ('AIzaSyCAm1dOznzQ2yzAyXh2xlZOnFP-vV6GOhE')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

# Beauty consultant system prompt
BEAUTY_CONSULTANT_PROMPT = """You are Kyra, an expert beauty consultant with over 15 years of experience in skincare, makeup, haircare, and wellness. 

Your expertise includes:
- Skincare routines for different skin types (oily, dry, combination, sensitive)
- Makeup recommendations and tutorials
- Product recommendations based on skin concerns (acne, aging, pigmentation, etc.)
- Haircare advice for various hair types
- Beauty tips and tricks
- Wellness and self-care recommendations
- Ingredient analysis and product safety

Guidelines:
1. Always be friendly, supportive, and professional
2. Ask clarifying questions about skin type, concerns, and preferences before making recommendations
3. Provide personalized advice based on the user's specific needs
4. Recommend both affordable and luxury options when suggesting products
5. Always mention sun protection and patch testing when relevant
6. Be inclusive and consider diverse skin tones and types
7. Discourage harmful beauty practices
8. If medical concerns arise, advise consulting a dermatologist
9. Keep responses clear, organized, and actionable

Start every conversation by warmly greeting the user and asking how you can help with their beauty concerns today."""

# Conversation history storage (in production, use a proper database)
conversation_history = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Initialize conversation history for new sessions
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Get conversation history
        history = conversation_history[session_id]
        
        # Build conversation context
        context = BEAUTY_CONSULTANT_PROMPT + "\n\nConversation History:\n"
        for msg in history[-10:]:  # Keep last 10 messages for context
            context += f"{msg['role']}: {msg['content']}\n"
        
        context += f"\nUser: {user_message}\nKyra:"
        
        # Generate response using Gemini
        response = model.generate_content(context)
        bot_response = response.text
        
        # Update conversation history
        conversation_history[session_id].append({
            'role': 'User',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        conversation_history[session_id].append({
            'role': 'Bella',
            'content': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in conversation_history:
            conversation_history[session_id] = []
        
        return jsonify({'message': 'Conversation history cleared'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-tips', methods=['GET'])
def get_beauty_tips():
    """Get random beauty tips"""
    tips = [
        "Always remove makeup before bed to prevent clogged pores and breakouts.",
        "Apply sunscreen daily - it's the best anti-aging product you can use!",
        "Stay hydrated! Drinking water helps maintain skin elasticity and glow.",
        "Use a silk pillowcase to reduce hair breakage and prevent sleep wrinkles.",
        "Apply eye cream with your ring finger for gentle application.",
        "Exfoliate 2-3 times a week for smooth, radiant skin.",
        "Always patch test new products on your inner arm before using on your face.",
        "Apply skincare products from thinnest to thickest consistency.",
        "Don't forget to moisturize your neck - it shows aging signs too!",
        "Clean your makeup brushes weekly to prevent bacteria buildup."
    ]
    
    import random
    return jsonify({'tip': random.choice(tips)})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Beauty Consultant Bot'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
