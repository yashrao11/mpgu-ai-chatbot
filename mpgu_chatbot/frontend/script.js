class MPGUChatbot {
    constructor() {
        this.backendUrl = 'http://localhost:5000/api/v1/chat';
        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        
        this.userId = this.generateUserId();
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setWelcomeTime();
        this.testConnection();
    }
    
    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }
    
    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.messageInput.addEventListener('input', () => {
            this.sendButton.disabled = !this.messageInput.value.trim();
        });
    }
    
    setWelcomeTime() {
        const timeElement = document.getElementById('welcomeTime');
        if (timeElement) {
            timeElement.textContent = this.getCurrentTime();
        }
    }
    
    async testConnection() {
        try {
            console.log('🔍 Testing connection to MPGU Chatbot backend...');
            const response = await fetch('http://localhost:5000/health', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Backend health check:', data);
                this.setStatus('connected');
                this.isConnected = true;
                this.addSystemMessage('✅ Connected to MPGU Assistant (Hugging Face + smart fallback)');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Connection test failed:', error);
            this.setStatus('error');
            this.addSystemMessage('❌ Cannot connect to backend. Please make sure the server is running on port 5000.');
        }
    }
    
    setStatus(status) {
        const statusMap = {
            connected: { color: '#22c55e', tooltip: 'Connected to MPGU Assistant' },
            error: { color: '#ef4444', tooltip: 'Connection error - check backend server' },
            connecting: { color: '#eab308', tooltip: 'Connecting...' }
        };
        
        const statusInfo = statusMap[status] || statusMap.error;
        this.statusIndicator.style.background = statusInfo.color;
        this.statusIndicator.title = statusInfo.tooltip;
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.sendButton.disabled = true;
        
        // If backend is not connected, show error
        if (!this.isConnected) {
            this.addMessage("Backend server is not running. Please start the server with 'python run.py' in the backend directory.", 'bot', true);
            this.sendButton.disabled = false;
            return;
        }
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            console.log('🚀 Sending message to backend:', message);
            
            const response = await fetch(this.backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.userId
                })
            });
            
            console.log('📊 Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            console.log('✅ Response data:', data);
            
            this.hideTypingIndicator();
            this.addMessage(data.reply, 'bot');
            
        } catch (error) {
            this.hideTypingIndicator();
            console.error('❌ Chat error:', error);
            
            this.addMessage(
                `Sorry, I encountered an error: ${error.message}. Please check the console for details.`, 
                'bot', 
                true
            );
        } finally {
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    addMessage(content, sender, isError = false) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message ${isError ? 'error-message' : ''}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.getCurrentTime();
        
        messageElement.appendChild(messageContent);
        messageElement.appendChild(messageTime);
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    addSystemMessage(content) {
        const systemElement = document.createElement('div');
        systemElement.className = 'message bot-message';
        systemElement.style.backgroundColor = '#f1f5f9';
        systemElement.style.color = '#475569';
        systemElement.style.fontSize = '12px';
        systemElement.style.fontStyle = 'italic';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        systemElement.appendChild(messageContent);
        this.messagesContainer.appendChild(systemElement);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Simple formatting for URLs and basic markdown
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color: #3b82f6; text-decoration: underline;">$1</a>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'typing-indicator';
        typingElement.id = 'typingIndicator';
        
        typingElement.innerHTML = `
            <div>MPGU Assistant is thinking</div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        this.messagesContainer.appendChild(typingElement);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingElement = document.getElementById('typingIndicator');
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    getCurrentTime() {
        return new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    new MPGUChatbot();
});
