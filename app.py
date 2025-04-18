"""
Web Interface for Interactive AI System

This module provides a Flask-based web interface for the interactive AI system.
"""

from flask import Flask, render_template, request, jsonify, session
import os
import uuid
import json
from datetime import datetime

# Import our custom modules
from claude_api import ClaudeAPI
from conversation import Conversation, ConversationManager
from ambiguity import AmbiguityDetector
from follow_up import FollowUpQuestionGenerator

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize our components
claude_api = ClaudeAPI(api_key="dummy")  # Use dummy mode for development
conversation_manager = ConversationManager(storage_dir="conversations")
ambiguity_detector = AmbiguityDetector(threshold=0.5)
follow_up_generator = FollowUpQuestionGenerator()

# System prompt for Claude
SYSTEM_PROMPT = """
You are an interactive AI assistant designed to provide helpful, accurate, and thoughtful responses.
When a user's question is ambiguous or lacks necessary details, ask follow-up questions to clarify.
Continue asking questions until you have enough information to provide a specific, helpful answer.
Be conversational and friendly in your tone.
"""

@app.route('/')
def index():
    """Render the main page of the application."""
    # Create a new conversation if one doesn't exist in the session
    if 'conversation_id' not in session:
        conversation = conversation_manager.create_conversation()
        session['conversation_id'] = conversation.conversation_id
    
    return render_template('index.html')

@app.route('/api/message', methods=['POST'])
def process_message():
    """Process a message from the user and generate a response."""
    # Get the user message from the request
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get or create conversation
    conversation_id = session.get('conversation_id')
    if not conversation_id:
        conversation = conversation_manager.create_conversation()
        session['conversation_id'] = conversation.conversation_id
    else:
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            conversation = conversation_manager.create_conversation()
            session['conversation_id'] = conversation.conversation_id
    
    # Add user message to conversation
    conversation.add_message("user", user_message)
    
    # Prepare conversation context for ambiguity detection
    conversation_context = {
        "recent_messages": conversation.get_messages(limit=5),
        "recent_topics": conversation.get_context("recent_topics", [])
    }
    
    # Detect ambiguity in the user message
    ambiguity_details = ambiguity_detector.get_ambiguity_details(user_message, conversation_context)
    
    # Determine if we need to ask a follow-up question
    if ambiguity_details["is_ambiguous"]:
        # Generate a follow-up question
        follow_up = follow_up_generator.generate_follow_up_question(
            user_message, 
            ambiguity_details,
            conversation_context
        )
        
        # Mark that ambiguity was detected
        conversation.mark_ambiguity_detected()
        
        # Add the follow-up question to the conversation
        conversation.add_message("assistant", follow_up)
        
        # Return the follow-up question
        return jsonify({
            'response': follow_up,
            'conversation_id': conversation.conversation_id,
            'timestamp': datetime.now().isoformat(),
            'is_follow_up': True
        })
    
    # If not ambiguous, generate a direct response using Claude API
    messages = conversation.get_messages_for_api()
    
    # Get response from Claude API
    response = claude_api.generate_response(
        messages=messages,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Add the response to the conversation
    conversation.add_message("assistant", response["content"])
    
    # Update conversation context with potential topics
    # This is a simple implementation - in a real system, you might use NLP to extract topics
    words = user_message.lower().split()
    potential_topics = [word for word in words if len(word) > 4]  # Simple heuristic
    if potential_topics:
        current_topics = conversation.get_context("recent_topics", [])
        updated_topics = [potential_topics[0]] + current_topics
        updated_topics = updated_topics[:5]  # Keep only the 5 most recent topics
        conversation.update_context("recent_topics", updated_topics)
    
    # Save the conversation
    conversation_manager.save_all_conversations()
    
    # Return the response
    return jsonify({
        'response': response["content"],
        'conversation_id': conversation.conversation_id,
        'timestamp': datetime.now().isoformat(),
        'is_follow_up': False
    })

@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    """Get the current conversation history."""
    conversation_id = session.get('conversation_id')
    if not conversation_id:
        return jsonify({'error': 'No active conversation'}), 404
    
    conversation = conversation_manager.get_conversation(conversation_id)
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify({
        'conversation_id': conversation.conversation_id,
        'messages': conversation.messages,
        'metadata': conversation.metadata
    })

@app.route('/api/conversation/new', methods=['POST'])
def new_conversation():
    """Start a new conversation."""
    conversation = conversation_manager.create_conversation()
    session['conversation_id'] = conversation.conversation_id
    
    return jsonify({
        'conversation_id': conversation.conversation_id,
        'message': 'New conversation started'
    })

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('conversations', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
