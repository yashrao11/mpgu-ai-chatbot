class MPGUChatbot {
    constructor() {
        this.backendBase = 'http://127.0.0.1:5000';
        this.chatEndpoint = `${this.backendBase}/api/v1/chat`;

        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusLabel = document.getElementById('statusLabel');
        this.backendUrl = document.getElementById('backendUrl');
        this.quickActions = document.querySelectorAll('.prompt-btn');
        this.roleSelect = document.getElementById('roleSelect');

        this.userId = this.getOrCreateUserId();
        this.isConnected = false;

        this.init();
    }

    init() {
        this.backendUrl.textContent = `Backend: ${this.backendBase}`;
        this.setupEventListeners();
        this.testConnection();
    }

    getOrCreateUserId() {
        const existing = localStorage.getItem('mpgu_user_id');
        if (existing) return existing;

        const created = `user_${Math.random().toString(36).slice(2, 10)}`;
        localStorage.setItem('mpgu_user_id', created);
        return created;
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.clearButton.addEventListener('click', () => this.clearHistory());

        this.messageInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.sendMessage();
            }
        });

        this.messageInput.addEventListener('input', () => {
            this.sendButton.disabled = !this.messageInput.value.trim();
        });

        this.quickActions.forEach((button) => {
            button.addEventListener('click', () => {
                this.messageInput.value = button.dataset.msg || '';
                this.sendButton.disabled = !this.messageInput.value.trim();
                this.messageInput.focus();
            });
        });
    }

    async testConnection() {
        this.setStatus('connecting', 'Connecting...');
        try {
            const response = await fetch(`${this.backendBase}/health`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.isConnected = true;
            this.setStatus('connected', data.ai_provider || 'Groq backend connected');
            this.addSystemMessage('✅ Backend connected. Groq demo mode is ready.');
        } catch (error) {
            this.isConnected = false;
            this.setStatus('error', 'Backend offline');
            this.addSystemMessage(`❌ Cannot connect to backend at ${this.backendBase}`);
        }
    }

    setStatus(status, label = '') {
        const map = {
            connected: { className: 'online', text: 'Connected' },
            connecting: { className: 'pending', text: 'Connecting' },
            error: { className: 'offline', text: 'Disconnected' }
        };

        const state = map[status] || map.error;
        this.statusIndicator.className = `status-dot ${state.className}`;
        this.statusLabel.textContent = label || state.text;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.sendButton.disabled = true;

        if (!this.isConnected) {
            this.addMessage(
                'Backend is offline. Start backend with `python run.py` inside `mpgu_chatbot/backend`.',
                'bot',
                { source: 'client', isError: true }
            );
            this.sendButton.disabled = false;
            this.messageInput.focus();
            return;
        }

        this.showTypingIndicator();

        try {
            const response = await fetch(this.chatEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    user_id: this.userId,
                    user_role: this.roleSelect.value
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const data = await response.json();

            this.addMessage(data.reply, 'bot', {
                source: data.source,
                intent: data.intent,
                language: data.language,
                confidence: data.confidence,
                providerStatus: data.provider_status,
                fallbackReason: data.fallback_reason
            });

            if (data.provider_status === 'quota_exceeded') {
                this.addSystemMessage('⚠️ Groq quota or rate limit reached. Knowledge fallback is active.');
            } else if (data.provider_status !== 'ok' && data.provider_attempted === 'groq') {
                this.addSystemMessage('⚠️ Groq was unavailable for this request. Showing fallback response.');
            }
        } catch (error) {
            this.addMessage(`Request failed: ${error.message}`, 'bot', {
                source: 'client',
                isError: true
            });
        } finally {
            this.hideTypingIndicator();
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }

    async clearHistory() {
        try {
            await fetch(`${this.backendBase}/api/v1/chat/history/${this.userId}`, {
                method: 'DELETE'
            });
        } catch {
            // UI should still clear even if backend history clear fails.
        }

        this.messagesContainer.innerHTML = '';
        this.addSystemMessage('🧹 Chat history cleared for this demo session.');
    }

    addSystemMessage(content) {
        this.addMessage(content, 'bot', { source: 'system' });
    }

    addMessage(content, sender, options = {}) {
        const {
            source = '',
            intent = '',
            language = '',
            confidence = null,
            providerStatus = '',
            fallbackReason = '',
            isError = false
        } = options;

        const wrapper = document.createElement('article');
        wrapper.className = `message ${sender}-message ${isError ? 'error-message' : ''}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? 'You' : 'AI';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.innerHTML = this.formatMessage(content);

        const metaEl = document.createElement('div');
        metaEl.className = 'message-meta';

        const badges = [];
        if (source) badges.push(`source: ${source}`);
        if (intent) badges.push(`intent: ${intent}`);
        if (language) badges.push(`lang: ${language}`);
        if (confidence !== null && confidence !== undefined) badges.push(`confidence: ${confidence}`);
        if (providerStatus) badges.push(`provider_status: ${providerStatus}`);
        if (fallbackReason) badges.push(`fallback_reason: ${fallbackReason}`);

        badges.forEach((text) => {
            const badge = document.createElement('span');
            badge.className = 'badge';
            badge.textContent = text;
            metaEl.appendChild(badge);
        });

        const timeEl = document.createElement('div');
        timeEl.className = 'message-time';
        timeEl.textContent = this.getCurrentTime();

        bubble.appendChild(contentEl);
        if (badges.length) bubble.appendChild(metaEl);
        bubble.appendChild(timeEl);

        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);

        this.messagesContainer.appendChild(wrapper);
        this.scrollToBottom();
    }

    formatMessage(content) {
        return String(content)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        const typingEl = document.createElement('article');
        typingEl.className = 'message bot-message typing-indicator';
        typingEl.id = 'typingIndicator';
        typingEl.innerHTML = `
            <div class="avatar">AI</div>
            <div class="bubble typing-bubble">
                <span>Assistant is thinking</span>
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
        `;
        this.messagesContainer.appendChild(typingEl);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const node = document.getElementById('typingIndicator');
        if (node) node.remove();
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

document.addEventListener('DOMContentLoaded', () => {
    new MPGUChatbot();
});