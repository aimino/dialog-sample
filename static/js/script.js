/**
 * Interactive AI Chat System - Frontend JavaScript
 * Handles user interactions, message sending, and UI updates
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const newConversationButton = document.getElementById('new-conversation');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // State variables
    let isWaitingForResponse = false;
    
    // Initialize
    userInput.focus();
    
    // Auto-resize textarea as user types
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        
        // Enable/disable send button based on input
        if (this.value.trim() === '') {
            sendButton.disabled = true;
        } else {
            sendButton.disabled = false;
        }
    });
    
    // Handle Enter key to send message (Shift+Enter for new line)
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isWaitingForResponse && this.value.trim() !== '') {
                sendMessage();
            }
        }
    });
    
    // Send button click handler
    sendButton.addEventListener('click', function() {
        if (!isWaitingForResponse && userInput.value.trim() !== '') {
            sendMessage();
        }
    });
    
    // New conversation button click handler
    newConversationButton.addEventListener('click', function() {
        if (confirm('新しい会話を開始しますか？現在の会話は保存されます。')) {
            startNewConversation();
        }
    });
    
    /**
     * Send user message to the server and handle response
     */
    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;
        
        // Disable input while waiting for response
        isWaitingForResponse = true;
        sendButton.disabled = true;
        
        // Add user message to chat
        addMessageToChat('user', userMessage);
        
        // Clear input
        userInput.value = '';
        userInput.style.height = 'auto';
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        
        // Send message to server
        fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Add assistant response to chat
            addMessageToChat('assistant', data.response);
            
            // Re-enable input
            isWaitingForResponse = false;
            userInput.focus();
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Add error message
            addMessageToChat('assistant', 'すみません、エラーが発生しました。もう一度お試しください。');
            
            // Re-enable input
            isWaitingForResponse = false;
            userInput.focus();
        });
    }
    
    /**
     * Add a message to the chat display
     * @param {string} role - 'user' or 'assistant'
     * @param {string} content - Message content
     */
    function addMessageToChat(role, content) {
        // Create message elements
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process message content (handle markdown, links, etc.)
        const processedContent = processMessageContent(content);
        contentDiv.innerHTML = processedContent;
        
        // Assemble and add to chat
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    /**
     * Process message content to handle formatting
     * @param {string} content - Raw message content
     * @returns {string} Processed HTML content
     */
    function processMessageContent(content) {
        // Convert newlines to <br>
        let processed = content.replace(/\n/g, '<br>');
        
        // Simple link detection
        processed = processed.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return `<p>${processed}</p>`;
    }
    
    /**
     * Scroll chat to the bottom
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Start a new conversation
     */
    function startNewConversation() {
        fetch('/api/conversation/new', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            // Clear chat messages except for the first welcome message
            while (chatMessages.children.length > 1) {
                chatMessages.removeChild(chatMessages.lastChild);
            }
            
            // Add system message about new conversation
            addMessageToChat('assistant', 'こんにちは！新しい会話を開始しました。質問があればお気軽にどうぞ。');
            
            // Reset state
            isWaitingForResponse = false;
            userInput.focus();
        })
        .catch(error => {
            console.error('Error starting new conversation:', error);
        });
    }
    
    /**
     * Load conversation history
     */
    function loadConversationHistory() {
        fetch('/api/conversation')
        .then(response => {
            if (!response.ok) {
                // If no conversation exists, that's fine
                if (response.status === 404) {
                    return null;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data && data.messages && data.messages.length > 0) {
                // Clear default welcome message
                chatMessages.innerHTML = '';
                
                // Add messages to chat
                data.messages.forEach(msg => {
                    addMessageToChat(msg.role, msg.content);
                });
            }
        })
        .catch(error => {
            console.error('Error loading conversation:', error);
        });
    }
    
    // Load conversation history on startup
    loadConversationHistory();
});
