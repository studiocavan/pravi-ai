// Configuration
// Auto-detect API URL based on environment
const API_BASE_URL = window.location.hostname === 'localhost' && window.location.port === ''
    ? 'http://localhost:8000'  // Direct file access
    : window.location.port === '3000'
    ? '/api'  // Docker/nginx proxy
    : 'http://localhost:8000';  // Development server

// State
let chatHistory = [];

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat');
const useRagCheckbox = document.getElementById('use-rag');
const useMcpCheckbox = document.getElementById('use-mcp');
const viewDocsBtn = document.getElementById('view-docs');
const addDocBtn = document.getElementById('add-doc');
const docsModal = document.getElementById('docs-modal');
const addDocModal = document.getElementById('add-doc-modal');
const submitDocBtn = document.getElementById('submit-doc');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadKBStats();
    setupEventListeners();
    setInterval(checkHealth, 30000); // Check health every 30s
});

// Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    clearChatBtn.addEventListener('click', clearChat);
    viewDocsBtn.addEventListener('click', () => openModal('docs-modal'));
    addDocBtn.addEventListener('click', () => openModal('add-doc-modal'));
    submitDocBtn.addEventListener('click', addDocument);

    // Enter to send (Shift+Enter for new line)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Example question buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.textContent;
            sendMessage();
        });
    });

    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.remove('active');
        });
    });

    // Close modal on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

// Check backend health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        updateStatusIndicator('status-llm', data.llm_available);
        updateStatusIndicator('status-rag', data.rag_available);
        updateStatusIndicator('status-mcp', data.mcp_available);
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatusIndicator('status-llm', false);
        updateStatusIndicator('status-rag', false);
        updateStatusIndicator('status-mcp', false);
    }
}

function updateStatusIndicator(id, isOnline) {
    const indicator = document.getElementById(id);
    const dot = indicator.querySelector('.status-dot');

    if (isOnline) {
        dot.classList.add('online');
    } else {
        dot.classList.remove('online');
    }
}

// Load knowledge base stats
async function loadKBStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/documents`);
        const data = await response.json();
        document.getElementById('doc-count').textContent = data.documents.length;
    } catch (error) {
        console.error('Failed to load KB stats:', error);
    }
}

// Send message
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Clear input
    userInput.value = '';

    // Remove welcome message if present
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    // Add user message
    addMessageToChat('user', message);

    // Show loading indicator
    const loadingId = showLoading();

    // Disable send button
    sendBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                use_rag: useRagCheckbox.checked,
                use_mcp: useMcpCheckbox.checked
            })
        });

        const data = await response.json();

        // Remove loading indicator
        removeLoading(loadingId);

        // Add assistant response
        addMessageToChat('assistant', data.response, {
            sources: data.sources,
            mcp_tools_used: data.mcp_tools_used
        });

        // Update chat history
        chatHistory.push({
            user: message,
            assistant: data.response
        });

    } catch (error) {
        removeLoading(loadingId);
        addMessageToChat('assistant', `Error: ${error.message}. Make sure the backend is running.`);
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Add message to chat
function addMessageToChat(role, content, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    // Add metadata if present
    if (metadata.sources && metadata.sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        sourcesDiv.innerHTML = `<strong>Sources:</strong> ${metadata.sources.join(', ')}`;
        contentDiv.appendChild(sourcesDiv);
    }

    if (metadata.mcp_tools_used && metadata.mcp_tools_used.length > 0) {
        const toolsDiv = document.createElement('div');
        toolsDiv.className = 'message-metadata';
        toolsDiv.innerHTML = `MCP Tools: ${metadata.mcp_tools_used.join(', ')}`;
        contentDiv.appendChild(toolsDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show loading indicator
function showLoading() {
    const loadingDiv = document.createElement('div');
    const id = 'loading-' + Date.now();
    loadingDiv.id = id;
    loadingDiv.className = 'message assistant-message';

    loadingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="loading">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;

    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

function removeLoading(id) {
    const loadingDiv = document.getElementById(id);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Clear chat
function clearChat() {
    if (confirm('Clear chat history?')) {
        chatHistory = [];
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>👋 Welcome to Pravi AI</h2>
                <p>Ask me anything! I use a local LLM with RAG for enhanced responses.</p>
                <div class="example-questions">
                    <p><strong>Try asking:</strong></p>
                    <button class="example-btn">What is Python?</button>
                    <button class="example-btn">Explain machine learning</button>
                    <button class="example-btn">What is RAG?</button>
                </div>
            </div>
        `;

        // Re-attach event listeners to example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                userInput.value = btn.textContent;
                sendMessage();
            });
        });
    }
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');

    if (modalId === 'docs-modal') {
        loadDocuments();
    }
}

async function loadDocuments() {
    const docsList = document.getElementById('docs-list');
    docsList.innerHTML = 'Loading...';

    try {
        const response = await fetch(`${API_BASE_URL}/documents`);
        const data = await response.json();

        if (data.documents.length === 0) {
            docsList.innerHTML = '<p>No documents in knowledge base.</p>';
            return;
        }

        docsList.innerHTML = data.documents.map(doc => `
            <div class="document-item">
                <strong>${doc.metadata.source || 'Unknown Source'}</strong>
                <p>${doc.content}</p>
                <small>ID: ${doc.id}</small>
            </div>
        `).join('');

    } catch (error) {
        docsList.innerHTML = `<p>Error loading documents: ${error.message}</p>`;
    }
}

async function addDocument() {
    const content = document.getElementById('new-doc-content').value.trim();
    const source = document.getElementById('new-doc-source').value.trim();

    if (!content) {
        alert('Please enter document content');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/documents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                metadata: {
                    source: source || 'User Added',
                    category: 'custom'
                }
            })
        });

        const data = await response.json();

        alert('Document added successfully!');

        // Clear form
        document.getElementById('new-doc-content').value = '';
        document.getElementById('new-doc-source').value = '';

        // Close modal
        document.getElementById('add-doc-modal').classList.remove('active');

        // Reload stats
        loadKBStats();

    } catch (error) {
        alert(`Error adding document: ${error.message}`);
    }
}
