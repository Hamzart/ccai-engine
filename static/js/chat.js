/**
 * CCAI Chatbot JavaScript
 * Handles chat functionality, WebSocket connection, and UI interactions
 */

// DOM Elements
const chatBody = document.getElementById('chatBody');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const settingsButton = document.getElementById('settingsButton');
const sidebar = document.getElementById('sidebar');
const learnModeToggle = document.getElementById('learnModeToggle');
const learnModeIndicator = document.getElementById('learnModeIndicator');
const savePreferencesButton = document.getElementById('savePreferences');

// User state
const userId = 'user_' + Math.random().toString(36).substring(2, 10);
let learnMode = false;
let webSocket = null;
let useWebSocket = true; // Set to false to use REST API instead

// Update user ID display
document.getElementById('userId').textContent = userId;

/**
 * Initialize the chat interface
 */
function initChat() {
    // Initialize WebSocket if enabled
    if (useWebSocket) {
        connectWebSocket();
    }
    
    // Add event listeners
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    settingsButton.addEventListener('click', () => {
        sidebar.classList.toggle('d-none');
        fetchUserPreferences();
        fetchUserProfile();
    });
    
    learnModeToggle.addEventListener('click', () => {
        learnMode = !learnMode;
        learnModeIndicator.classList.toggle('d-none', !learnMode);
        learnModeToggle.classList.toggle('btn-outline-light', !learnMode);
        learnModeToggle.classList.toggle('btn-success', learnMode);
    });
    
    savePreferencesButton.addEventListener('click', saveUserPreferences);
    
    // Initialize preferences and profile
    fetchUserPreferences();
    fetchUserProfile();
    
    // Focus on input
    messageInput.focus();
}

/**
 * Connect to WebSocket for real-time chat
 */
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${userId}`;
    
    webSocket = new WebSocket(wsUrl);
    
    webSocket.onopen = () => {
        console.log('WebSocket connected');
    };
    
    webSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        hideTypingIndicator();
        addMessage(data.text);
        fetchUserProfile(); // Update profile after each message
    };
    
    webSocket.onclose = () => {
        console.log('WebSocket disconnected');
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 3000);
    };
    
    webSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        webSocket.close();
    };
}

/**
 * Add a message to the chat
 * @param {string} text - Message text
 * @param {boolean} isUser - Whether the message is from the user
 */
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'user-message message' : 'bot-message message';
    
    // Process markdown if it's a bot message
    if (!isUser && text.includes('```') || text.includes('#') || text.includes('*')) {
        messageDiv.classList.add('markdown');
        messageDiv.innerHTML = markdownToHtml(text);
    } else {
        const messageText = document.createElement('div');
        messageText.textContent = text;
        messageDiv.appendChild(messageText);
    }
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    messageDiv.appendChild(messageTime);
    
    // Insert before typing indicator
    chatBody.insertBefore(messageDiv, typingIndicator);
    
    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    chatBody.scrollTop = chatBody.scrollHeight;
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

/**
 * Send a message
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, true);
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Add loading animation to send button
    sendButton.classList.add('loading');
    
    if (useWebSocket && webSocket && webSocket.readyState === WebSocket.OPEN) {
        // Send via WebSocket
        webSocket.send(JSON.stringify({
            text: message,
            user_id: userId,
            learn_mode: learnMode
        }));
    } else {
        // Send via REST API
        try {
            // Determine endpoint based on learn mode
            const endpoint = learnMode ? '/api/learn' : '/api/chat';
            
            // Send message to server
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: message,
                    user_id: userId
                })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            hideTypingIndicator();
            
            // Add bot response to chat
            if (learnMode) {
                addMessage("I've learned this information. Thank you!");
            } else {
                addMessage(data.text);
            }
            
            // Update user profile
            fetchUserProfile();
        } catch (error) {
            console.error('Error sending message:', error);
            hideTypingIndicator();
            addMessage('Sorry, there was an error processing your message. Please try again.');
        }
    }
    
    // Remove loading animation
    sendButton.classList.remove('loading');
}

/**
 * Fetch user preferences
 */
async function fetchUserPreferences() {
    try {
        const response = await fetch(`/api/user/${userId}/preferences`);
        const preferences = await response.json();
        
        // Update UI
        document.getElementById('responseStyle').value = preferences.response_style || 'balanced';
        document.getElementById('formalityLevel').value = preferences.formality_level || 'neutral';
        document.getElementById('technicalLevel').value = preferences.technical_level || 'medium';
        document.getElementById('humorLevel').value = preferences.humor_level || 'medium';
    } catch (error) {
        console.error('Error fetching preferences:', error);
    }
}

/**
 * Save user preferences
 */
async function saveUserPreferences() {
    const preferences = {
        response_style: document.getElementById('responseStyle').value,
        formality_level: document.getElementById('formalityLevel').value,
        technical_level: document.getElementById('technicalLevel').value,
        humor_level: document.getElementById('humorLevel').value
    };
    
    for (const [key, value] of Object.entries(preferences)) {
        try {
            await fetch(`/api/user/${userId}/preferences`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    preference: key,
                    value: value
                })
            });
        } catch (error) {
            console.error(`Error saving preference ${key}:`, error);
        }
    }
    
    // Show success message
    const saveButton = document.getElementById('savePreferences');
    const originalText = saveButton.textContent;
    saveButton.textContent = 'Saved!';
    saveButton.classList.add('btn-success');
    saveButton.classList.remove('btn-primary');
    
    setTimeout(() => {
        saveButton.textContent = originalText;
        saveButton.classList.remove('btn-success');
        saveButton.classList.add('btn-primary');
    }, 2000);
}

/**
 * Fetch user profile
 */
async function fetchUserProfile() {
    try {
        const response = await fetch(`/api/user/${userId}/profile`);
        const profile = await response.json();
        
        // Update UI
        document.getElementById('sessionCount').textContent = profile.session_count;
        document.getElementById('topTopics').textContent = profile.top_topics.length > 0 ? 
            profile.top_topics.join(', ') : 'None yet';
        document.getElementById('topEntities').textContent = profile.top_entities.length > 0 ? 
            profile.top_entities.join(', ') : 'None yet';
    } catch (error) {
        console.error('Error fetching profile:', error);
    }
}

/**
 * Convert markdown to HTML
 * @param {string} markdown - Markdown text
 * @returns {string} HTML
 */
function markdownToHtml(markdown) {
    // This is a simple implementation - in a real app, use a proper markdown library
    let html = markdown;
    
    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<div class="code-block">$1</div>');
    
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Headers
    html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Lists
    html = html.replace(/^\s*\- (.*$)/gm, '<ul><li>$1</li></ul>');
    html = html.replace(/^\s*\d+\. (.*$)/gm, '<ol><li>$1</li></ol>');
    
    // Fix nested lists
    html = html.replace(/<\/ul>\s*<ul>/g, '');
    html = html.replace(/<\/ol>\s*<ol>/g, '');
    
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Paragraphs
    html = html.replace(/^(?!<[a-z])(.*$)/gm, '<p>$1</p>');
    
    // Fix empty paragraphs
    html = html.replace(/<p><\/p>/g, '');
    
    return html;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initChat);

// Handle page visibility changes to reconnect WebSocket if needed
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && useWebSocket) {
        if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
            connectWebSocket();
        }
    }
});