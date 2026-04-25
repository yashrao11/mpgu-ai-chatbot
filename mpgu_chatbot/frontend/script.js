class MPGUChatbot {
    constructor() {
        let host = window.location.hostname || '127.0.0.1';

        if (host === '::' || host === '::1' || host === '[::]' || host === '[::1]') {
        host = '127.0.0.1';
        }

        this.backendBase = `http://${host}:5000`;
        this.chatEndpoint = `${this.backendBase}/api/v1/chat`;

        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusLabel = document.getElementById('statusLabel');
        this.quickActions = document.getElementById('quickActions');

        this.userId = this.getOrCreateUserId();
        this.isConnected = false;

        this.init();
    }

    init() {
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

        this.quickActions.addEventListener('click', (event) => {
            if (event.target.classList.contains('chip')) {
                this.messageInput.value = event.target.dataset.msg || '';
                this.sendButton.disabled = !this.messageInput.value.trim();
                this.messageInput.focus();
            }
        });
    }

    async testConnection() {
        this.setStatus('connecting');
        try {
            const response = await fetch(`${this.backendBase}/health`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.isConnected = true;
            this.setStatus('connected', data.ai_provider || 'Connected');
            this.addSystemMessage('✅ Backend connected. Gemini mode is ready for demo.');
        } catch (error) {
            this.isConnected = false;
            this.setStatus('error', 'Backend offline');
            this.addSystemMessage(`❌ Cannot connect to backend at ${this.backendBase}`);
        }
    }

    setStatus(status, label = '') {
        const map = {
            connected: { color: '#16a34a', text: 'Connected' },
            connecting: { color: '#f59e0b', text: 'Connecting' },
            error: { color: '#dc2626', text: 'Disconnected' }
        };

        const state = map[status] || map.error;
        this.statusIndicator.style.background = state.color;
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
                'Backend is offline. Start backend with `python run.py` in `mpgu_chatbot/backend`.',
                'bot',
                {
                    source: 'client',
                    isError: true
                }
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
                body: JSON.stringify({ message, user_id: this.userId })
            });

            if (!response.ok) {
                const err = await response.text();
                throw new Error(`HTTP ${response.status}: ${err}`);
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
                this.addSystemMessage('⚠️ Gemini quota exhausted. Fallback mode is active right now.');
            } else if (data.provider_status !== 'ok' && data.provider_attempted === 'gemini') {
                this.addSystemMessage('⚠️ Gemini temporarily unavailable. Showing fallback response.');
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
            // Keep UI clear action working even if network call fails.
        }

        this.messagesContainer.innerHTML = '';
        this.addSystemMessage('🧹 Chat history cleared for this demo session.');
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

        const message = document.createElement('article');
        message.className = `message ${sender}-message ${isError ? 'error-message' : ''}`;

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

        message.appendChild(contentEl);
        if (badges.length) message.appendChild(metaEl);
        message.appendChild(timeEl);

        this.messagesContainer.appendChild(message);
        this.scrollToBottom();
    }

    addSystemMessage(content) {
        this.addMessage(content, 'bot', { source: 'system' });
    }

    formatMessage(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        const typingEl = document.createElement('article');
        typingEl.className = 'typing-indicator';
        typingEl.id = 'typingIndicator';
        typingEl.innerHTML = `
            <span>Assistant is thinking</span>
            <div class="typing-dots">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
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