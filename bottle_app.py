"""
Doqurix Web - ChatGPT-Style Interface
A modern web interface for document Q&A with conversation history
"""

from bottle import Bottle, request, response, static_file, template, abort
import os
import sys
from pathlib import Path
import json
import base64
import io
import threading

# Initialize Bottle app
app = Bottle()

# Global variables
llm = None
embedder = None
reranker = None
collection = None
chroma_client = None
bm25 = None
bm25_corpus = []

# Professional Modern UI - ChatGPT/Claude/Gemini Quality
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doqurix - AI Document Intelligence</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --bg-tertiary: #2a2a2a;
            --bg-chat-user: #2f2f2f;
            --bg-chat-assistant: #1a1a1a;
            --accent-primary: #10a37f;
            --accent-gradient: linear-gradient(135deg, #10a37f 0%, #1bc9a0 100%);
            --accent-orange: #ff6b35;
            --text-primary: #ececf1;
            --text-secondary: #b4b4b4;
            --text-muted: #6e6e80;
            --border-color: #3f3f46;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
            --shadow-lg: 0 10px 40px rgba(0,0,0,0.5);
            --shadow-glow: 0 0 20px rgba(16,163,127,0.3);
            --transition-fast: 0.15s ease;
            --transition-normal: 0.25s ease;
            --transition-slow: 0.4s ease;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        
        /* Animated gradient background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 50%, rgba(16,163,127,0.05) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(255,107,53,0.03) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        
        /* Header */
        .header {
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(20px);
            padding: 14px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            z-index: 100;
            box-shadow: var(--shadow-sm);
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .logo-icon {
            font-size: 24px;
            filter: drop-shadow(0 0 8px rgba(16,163,127,0.5));
        }
        
        .upload-btn {
            background: var(--accent-gradient);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all var(--transition-normal);
            box-shadow: var(--shadow-md);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .upload-btn:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: var(--shadow-glow), var(--shadow-lg);
        }
        
        .upload-btn:active {
            transform: translateY(0) scale(0.98);
        }
        
        /* Sidebar */
        .sidebar {
            position: fixed;
            left: 0;
            top: 63px;
            bottom: 0;
            width: 280px;
            background: rgba(26, 26, 26, 0.8);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border-color);
            padding: 16px;
            overflow-y: auto;
            z-index: 50;
            transition: transform var(--transition-normal);
        }
        
        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }
        
        .sidebar h3 {
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .doc-count {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }
        
        .doc-item {
            background: var(--bg-tertiary);
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 10px;
            font-size: 13px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all var(--transition-fast);
            border: 1px solid transparent;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .doc-item:hover {
            background: var(--bg-chat-user);
            border-color: var(--accent-primary);
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }
        
        .doc-name {
            display: flex;
            align-items: center;
            gap: 8px;
            flex: 1;
            overflow: hidden;
        }
        
        .doc-icon {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .doc-text {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: var(--text-secondary);
        }
        
        .delete-btn {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 600;
            transition: all var(--transition-fast);
            opacity: 0;
        }
        
        .doc-item:hover .delete-btn {
            opacity: 1;
        }
        
        .delete-btn:hover {
            background: rgba(239, 68, 68, 0.2);
            border-color: #ef4444;
            transform: scale(1.05);
        }
        
        /* Main chat area */
        .chat-container {
            margin-left: 280px;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 63px);
            position: relative;
            z-index: 1;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 32px 24px;
            scroll-behavior: smooth;
        }
        
        .message {
            margin-bottom: 32px;
            opacity: 0;
            animation: fadeInUp 0.4s ease forwards;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .message.assistant {
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .message-wrapper {
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }
        
        .message.user .message-wrapper {
            flex-direction: row-reverse;
        }
        
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
            box-shadow: var(--shadow-md);
        }
        
        .avatar.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .avatar.assistant {
            background: var(--accent-gradient);
        }
        
        .message-content {
            flex: 1;
            background: var(--bg-chat-assistant);
            padding: 16px 20px;
            border-radius: 16px;
            line-height: 1.7;
            font-size: 15px;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
        }
        
        .message.user .message-content {
            background: var(--bg-chat-user);
            border-color: rgba(102, 126, 234, 0.2);
        }
        
        .loading-dots {
            display: inline-flex;
            gap: 4px;
            align-items: center;
        }
        
        .loading-dots span {
            width: 8px;
            height: 8px;
            background: var(--accent-primary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1.2); opacity: 1; }
        }
        
        .source {
            cursor: pointer;
            color: var(--accent-primary);
            text-decoration: none;
            padding: 10px 14px;
            background: rgba(16, 163, 127, 0.08);
            border: 1px solid rgba(16, 163, 127, 0.2);
            border-radius: 8px;
            margin: 10px 0;
            display: block;
            transition: all var(--transition-fast);
            font-size: 13px;
        }
        
        .source:hover {
            background: rgba(16, 163, 127, 0.15);
            border-color: var(--accent-primary);
            transform: translateX(4px);
        }
        
        .source-content {
            display: none;
            margin-top: 10px;
            padding: 14px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 13px;
            line-height: 1.6;
            max-height: 300px;
            overflow-y: auto;
            border-left: 3px solid var(--accent-primary);
        }
        
        .source-content.expanded {
            display: block;
            animation: expandDown 0.3s ease;
        }
        
        @keyframes expandDown {
            from {
                opacity: 0;
                max-height: 0;
            }
            to {
                opacity: 1;
                max-height: 300px;
            }
        }
        
        /* Welcome screen */
        .welcome {
            text-align: center;
            padding: 60px 24px;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .welcome h2 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 16px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .welcome p {
            color: var(--text-secondary);
            font-size: 16px;
            line-height: 1.6;
        }
        
        /* Input area */
        .input-area {
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(20px);
            padding: 24px;
            border-top: 1px solid var(--border-color);
            box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
        }
        
        .input-wrapper {
            max-width: 900px;
            margin: 0 auto;
            position: relative;
        }
        
        .input-container {
            background: var(--bg-tertiary);
            border: 2px solid var(--border-color);
            border-radius: 16px;
            display: flex;
            align-items: flex-end;
            gap: 8px;
            padding: 8px;
            transition: all var(--transition-fast);
            box-shadow: var(--shadow-md);
        }
        
        .input-container:focus-within {
            border-color: var(--accent-primary);
            box-shadow: var(--shadow-glow), var(--shadow-md);
        }
        
        .attach-btn {
            background: transparent;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--transition-fast);
            flex-shrink: 0;
        }
        
        .attach-btn:hover {
            background: var(--bg-chat-user);
            transform: scale(1.1) rotate(10deg);
        }
        
        textarea {
            flex: 1;
            background: transparent;
            border: none;
            padding: 10px 12px;
            color: var(--text-primary);
            font-size: 15px;
            font-family: inherit;
            resize: none;
            min-height: 24px;
            max-height: 200px;
            line-height: 1.5;
        }
        
        textarea:focus {
            outline: none;
        }
        
        textarea::placeholder {
            color: var(--text-muted);
        }
        
        .send-btn {
            background: var(--accent-gradient);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--transition-fast);
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
        }
        
        .send-btn:hover:not(:disabled) {
            transform: scale(1.1) rotate(-5deg);
            box-shadow: var(--shadow-glow);
        }
        
        .send-btn:active:not(:disabled) {
            transform: scale(0.95);
        }
        
        .send-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--bg-tertiary);
            border-radius: 5px;
            border: 2px solid var(--bg-secondary);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--border-color);
        }
        
        /* Drag and drop */
        .drag-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(16, 163, 127, 0.1);
            border: 4px dashed var(--accent-primary);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
        
        .drag-overlay.active {
            display: flex;
        }
        
        .drag-content {
            text-align: center;
            color: var(--accent-primary);
        }
        
        .drag-content svg {
            width: 64px;
            height: 64px;
            margin-bottom: 16px;
            animation: float 2s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .drag-content h3 {
            font-size: 24px;
            margin-bottom: 8px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .chat-container {
                margin-left: 0;
            }
            
            .message {
                margin-bottom: 20px;
            }
            
            .avatar {
                width: 30px;
                height: 30px;
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <!-- Drag and Drop Overlay -->
    <div class="drag-overlay" id="dragOverlay">
        <div class="drag-content">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
            </svg>
            <h3>Drop PDF file here</h3>
            <p>Release to upload</p>
        </div>
    </div>

    <!-- Header -->
    <div class="header">
        <div class="header-left">
            <div class="logo">
                <span class="logo-icon">◆</span>
                <span>DOQURIX</span>
            </div>
        </div>
        <input type="file" id="file-input" accept=".pdf" style="display: none;" onchange="uploadFile()">
        <button class="upload-btn" onclick="document.getElementById('file-input').click()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
            </svg>
            Upload PDF
        </button>
    </div>
    
    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h3>Documents</h3>
            <span class="doc-count" id="docCount">0</span>
        </div>
        <div id="documents"></div>
    </div>
    
    <!-- Chat Container -->
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="welcome">
                <h2>Welcome to Doqurix</h2>
                <p>Your AI-powered document assistant. Upload PDF documents and start asking intelligent questions to extract insights instantly.</p>
            </div>
        </div>
        
        <!-- Input Area -->
        <div class="input-area">
            <div class="input-wrapper">
                <input type="file" id="input-file" accept=".pdf" style="display: none;" onchange="uploadFileFromInput()">
                <div class="input-container">
                    <button class="attach-btn" onclick="document.getElementById('input-file').click()" title="Attach file">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#8e8ea0" stroke-width="2">
                            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                        </svg>
                    </button>
                    <textarea id="question" placeholder="Ask me anything about your documents..." rows="1" 
                              oninput="auto_grow(this)" onkeydown="handleKeyPress(event)"></textarea>
                    <button class="send-btn" id="sendBtn" onclick="askQuestion()" disabled title="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let documents = [];
        let dragCounter = 0;
        
        // Auto-grow textarea
        function auto_grow(element) {
            element.style.height = "24px";
            element.style.height = (element.scrollHeight) + "px";
            
            // Enable/disable send button
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = !element.value.trim();
        }
        
        // Handle keyboard shortcuts
        function handleKeyPress(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                askQuestion();
            }
        }
        
        // Drag and drop handlers
        document.body.addEventListener('dragenter', (e) => {
            e.preventDefault();
            dragCounter++;
            if (e.dataTransfer.types.includes('Files')) {
                document.getElementById('dragOverlay').classList.add('active');
            }
        });
        
        document.body.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) {
                document.getElementById('dragOverlay').classList.remove('active');
            }
        });
        
        document.body.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        document.body.addEventListener('drop', (e) => {
            e.preventDefault();
            dragCounter = 0;
            document.getElementById('dragOverlay').classList.remove('active');
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                processUpload(files[0]);
            }
        });
        
        // File upload from button
        async function uploadFile() {
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0];
            if (!file) return;
            
            await processUpload(file);
            fileInput.value = '';
        }
        
        async function uploadFileFromInput() {
            const fileInput = document.getElementById('input-file');
            const file = fileInput.files[0];
            if (!file) return;
            
            await processUpload(file);
            fileInput.value = '';
        }
        
        // Process file upload
        async function processUpload(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            const loadingId = addMessage(
                `<div style="display: flex; align-items: center; gap: 12px;">
                    <div class="loading-dots">
                        <span></span><span></span><span></span>
                    </div>
                    <span>Uploading ${file.name}...</span>
                </div>`, 
                'assistant', 
                true
            );
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                // Remove loading message
                const loadingMsg = document.getElementById(loadingId);
                if (loadingMsg) loadingMsg.remove();
                
                if (result.success) {
                    documents.push(result.filename);
                    updateDocumentList();
                    addMessage(`✅ Successfully uploaded <strong>${file.name}</strong>`, 'assistant');
                } else {
                    addMessage(`❌ Error uploading file: ${result.error}`, 'assistant');
                }
            } catch (error) {
                const loadingMsg = document.getElementById(loadingId);
                if (loadingMsg) loadingMsg.remove();
                addMessage(`❌ Upload failed: ${error.message}`, 'assistant');
            }
        }
        
        // Update document list in sidebar
        function updateDocumentList() {
            const docList = document.getElementById('documents');
            const docCount = document.getElementById('docCount');
            
            docCount.textContent = documents.length;
            
            if (documents.length === 0) {
                docList.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; padding: 16px; text-align: center;">No documents uploaded</div>';
                return;
            }
            
            docList.innerHTML = documents.map((doc, idx) => `
                <div class="doc-item">
                    <div class="doc-name">
                        <span class="doc-icon">📄</span>
                        <span class="doc-text" title="${doc}">${doc}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteDocument(${idx})" title="Delete document">
                        Delete
                    </button>
                </div>
            `).join('');
        }
        
        // Delete document
        async function deleteDocument(index) {
            const filename = documents[index];
            
            if (!confirm(`Delete "${filename}"?`)) return;
            
            try {
                const response = await fetch('/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({filename: filename})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    documents.splice(index, 1);
                    updateDocumentList();
                    addMessage(`🗑️ Deleted <strong>${filename}</strong>`, 'assistant');
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Delete failed: ' + error.message);
            }
        }
        
        // Ask question
        async function askQuestion() {
            const questionInput = document.getElementById('question');
            const question = questionInput.value.trim();
            
            if (!question) return;
            if (documents.length === 0) {
                alert('⚠️ Please upload documents first');
                return;
            }
            
            // Add user message
            addMessage(question, 'user');
            questionInput.value = '';
            questionInput.style.height = "24px";
            document.getElementById('sendBtn').disabled = true;
            
            // Add loading message
            const loadingId = addMessage(
                `<div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>`, 
                'assistant', 
                true
            );
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                
                const result = await response.json();
                
                // Remove loading message
                const loadingMsg = document.getElementById(loadingId);
                if (loadingMsg) loadingMsg.remove();
                
                if (result.success) {
                    addMessage(result.answer, 'assistant');
                } else {
                    addMessage(`❌ Error: ${result.error}`, 'assistant');
                }
            } catch (error) {
                const loadingMsg = document.getElementById(loadingId);
                if (loadingMsg) loadingMsg.remove();
                addMessage(`❌ Request failed: ${error.message}`, 'assistant');
            }
        }
        
        // Add message to chat
        function addMessage(content, role, isLoading = false) {
            const messagesDiv = document.getElementById('messages');
            const messageId = 'msg-' + Date.now() + '-' + Math.random();
            
            // Remove welcome screen if exists
            const welcome = messagesDiv.querySelector('.welcome');
            if (welcome) welcome.remove();
            
            const avatar = role === 'user' ? '👤' : '🤖';
            
            const messageDiv = document.createElement('div');
            messageDiv.id = messageId;
            messageDiv.className = `message ${role}`;
            messageDiv.innerHTML = `
                <div class="message-wrapper">
                    <div class="avatar ${role}">${avatar}</div>
                    <div class="message-content">
                        ${content}
                    </div>
                </div>
            `;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            return messageId;
        }
        
        // Toggle source expansion
        function toggleSource(element) {
            const content = element.querySelector('.source-content');
            content.classList.toggle('expanded');
        }
        
        // Initialize
        updateDocumentList();
    </script>
</body>
</html>
"""


@app.route('/')
def index():

    """Serve main page"""
    return INDEX_HTML


@app.route('/upload', method='POST')
def upload():
    """Handle PDF upload"""
    try:
        upload_file = request.files.get('file')
        if not upload_file:
            return json.dumps({'success': False, 'error': 'No file provided'})
        
        filename = upload_file.filename
        if not filename.endswith('.pdf'):
            return json.dumps({'success': False, 'error': 'Only PDF files allowed'})
        
        file_content = upload_file.file.read()
        
        # Extract text
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # Chunk and add to vector store
        chunks = smart_chunk_text(text)
        for i, chunk in enumerate(chunks):
            embedding = embedder.encode(chunk).tolist()
            collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "source": filename,
                    "chunk_id": i,
                    "page": i // 3
                }],
                ids=[f"{filename}_{i}"]
            )
        
        rebuild_bm25_index()
        
        response.content_type = 'application/json'
        return json.dumps({'success': True, 'filename': filename})
        
    except Exception as e:
        response.content_type = 'application/json'
        return json.dumps({'success': False, 'error': str(e)})


@app.route('/delete', method='POST')
def delete():
    """Handle document deletion"""
    try:
        data = request.json
        filename = data.get('filename', '')
        
        if not filename:
            return json.dumps({'success': False, 'error': 'No filename provided'})
        
        # Get all documents from collection
        all_docs = collection.get()
        
        # Find IDs to delete
        ids_to_delete = []
        for i, metadata in enumerate(all_docs['metadatas']):
            if metadata['source'] == filename:
                ids_to_delete.append(all_docs['ids'][i])
        
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            rebuild_bm25_index()
        
        response.content_type = 'application/json'
        return json.dumps({'success': True, 'deleted': len(ids_to_delete)})
        
    except Exception as e:
        response.content_type = 'application/json'
        return json.dumps({'success': False, 'error': str(e)})


@app.route('/query', method='POST')
def query():
    """Handle question query"""
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return json.dumps({'success': False, 'error': 'No question provided'})
        
        # Search documents - use same parameters as desktop
        doc_results = advanced_hybrid_search(question, n_results=15)
        
        if not doc_results:
            return json.dumps({'success': False, 'error': 'No relevant documents found'})
        
        # Rerank - use same top_k as desktop
        reranked = rerank_documents(question, doc_results, top_k=5)
        
        # Generate answer
        answer = generate_answer(question, reranked)
        
        response.content_type = 'application/json'
        return json.dumps({'success': True, 'answer': answer})
        
    except Exception as e:
        response.content_type = 'application/json'
        return json.dumps({'success': False, 'error': str(e)})


def smart_chunk_text(text, chunk_size=600, overlap=200):
    """Smart chunking with overlap - matches desktop implementation"""
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        words = sentence.split()
        sentence_length = len(words)
        
        if current_length + sentence_length > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text.strip()) > 100:
                chunks.append(chunk_text)
            
            # Create overlap
            overlap_sentences = []
            overlap_length = 0
            for s in reversed(current_chunk):
                if overlap_length + len(s.split()) <= overlap:
                    overlap_sentences.insert(0, s)
                    overlap_length += len(s.split())
                else:
                    break
            
            current_chunk = overlap_sentences
            current_length = overlap_length
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        if len(chunk_text.strip()) > 100:
            chunks.append(chunk_text)
    
    return chunks


def advanced_hybrid_search(question, n_results=15):
    """Advanced hybrid search - matches desktop implementation"""
    global bm25, bm25_corpus
    
    # Check if collection has documents
    collection_data = collection.get()
    if not collection_data['documents'] or len(collection_data['documents']) == 0:
        return []
    
    question_embedding = embedder.encode(question).tolist()
    vector_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )
    
    combined_docs = {}
    k = 60
    
    # Use doc content as key (first 150 chars) to match desktop
    for rank, (doc, metadata) in enumerate(zip(vector_results['documents'][0], 
                                                 vector_results['metadatas'][0])):
        doc_key = doc[:150]
        if doc_key not in combined_docs:
            combined_docs[doc_key] = {
                'doc': doc, 
                'metadata': metadata, 
                'score': 0
            }
        combined_docs[doc_key]['score'] += 1 / (k + rank)
    
    if bm25 and bm25_corpus:
        import numpy as np
        tokenized_query = question.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        top_bm25_indices = np.argsort(bm25_scores)[-n_results:][::-1]
        
        for rank, idx in enumerate(top_bm25_indices):
            if idx < len(bm25_corpus):
                doc = bm25_corpus[idx]
                doc_key = doc[:150]
                
                if doc_key not in combined_docs:
                    all_docs = collection.get()
                    if idx < len(all_docs['metadatas']):
                        metadata = all_docs['metadatas'][idx]
                        combined_docs[doc_key] = {
                            'doc': doc, 
                            'metadata': metadata, 
                            'score': 0
                        }
                
                if doc_key in combined_docs:
                    combined_docs[doc_key]['score'] += 1 / (k + rank)
    
    sorted_docs = sorted(combined_docs.values(), key=lambda x: x['score'], reverse=True)
    return sorted_docs[:n_results]


def rerank_documents(question, doc_results, top_k=5):
    """Rerank documents - matches desktop implementation"""
    if not doc_results:
        return []
    
    documents = [d['doc'] for d in doc_results]
    pairs = [[question, doc] for doc in documents]
    scores = reranker.predict(pairs)
    
    for i, doc_result in enumerate(doc_results):
        doc_result['rerank_score'] = float(scores[i])
        doc_result['final_score'] = (
            0.3 * doc_result['score'] +
            0.7 * doc_result['rerank_score']
        )
    
    reranked = sorted(doc_results, key=lambda x: x['final_score'], reverse=True)
    return reranked[:top_k]


def detect_language(text):
    """Detect primary language from text sample"""
    # Simple heuristic based on character ranges
    sample = text[:500]  # Check first 500 chars
    
    # Count Arabic characters
    arabic_chars = sum(1 for c in sample if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F')
    # Count German-specific characters
    german_chars = sum(1 for c in sample if c in 'äöüßÄÖÜ')
    # Count Cyrillic (Russian, etc.)
    cyrillic_chars = sum(1 for c in sample if '\u0400' <= c <= '\u04FF')
    # Count Chinese/Japanese
    cjk_chars = sum(1 for c in sample if '\u4E00' <= c <= '\u9FFF' or '\u3040' <= c <= '\u30FF')
    
    total_chars = len(sample)
    if total_chars == 0:
        return 'english'
    
    # If > 20% Arabic, it's Arabic
    if arabic_chars / total_chars > 0.2:
        return 'arabic'
    # If has German chars and Latin script, likely German
    if german_chars > 0:
        return 'german'
    # If > 20% Cyrillic, it's Russian/Slavic
    if cyrillic_chars / total_chars > 0.2:
        return 'russian'
    # If > 20% CJK, it's Chinese/Japanese
    if cjk_chars / total_chars > 0.2:
        return 'chinese'
    
    # Default to English
    return 'english'


def generate_answer(question, contexts):
    """Generate answer using LLM with intelligent context management and language preservation"""
    # Estimate tokens (rough estimate: 1 token ≈ 4 characters)
    # Context window: 3072 tokens
    # Reserve: 500 tokens for answer, 200 for system/question
    # Available for context: ~2300 tokens ≈ 9200 characters
    
    max_context_chars = 9000  # Conservative limit
    
    # Build context text, stopping when we approach limit
    context_parts = []
    current_chars = 0
    
    for ctx in contexts:
        doc_text = ctx['doc']
        # Add context with source info
        ctx_text = f"[Source: {ctx['metadata']['source']}]\n{doc_text}\n"
        
        if current_chars + len(ctx_text) > max_context_chars:
            # If we have at least 2 contexts, stop here
            if len(context_parts) >= 2:
                break
            # Otherwise, truncate this context to fit
            remaining = max_context_chars - current_chars
            if remaining > 500:  # Only add if meaningful amount remains
                ctx_text = ctx_text[:remaining] + "..."
            else:
                break
        
        context_parts.append(ctx_text)
        current_chars += len(ctx_text)
    
    context_text = "\n\n".join(context_parts)
    
    # Detect language from context
    detected_lang = detect_language(context_text)
    
    # Create language-specific instruction
    lang_instructions = {
        'arabic': 'IMPORTANT: The documents are in Arabic. You MUST answer in Arabic only. Do not translate to English.',
        'german': 'IMPORTANT: The documents are in German. You MUST answer in German only. Do not translate to English.',
        'russian': 'IMPORTANT: The documents are in Russian. You MUST answer in Russian only. Do not translate to English.',
        'chinese': 'IMPORTANT: The documents are in Chinese. You MUST answer in Chinese only. Do not translate to English.',
        'english': 'Answer clearly and concisely in English.'
    }
    
    lang_instruction = lang_instructions.get(detected_lang, lang_instructions['english'])
    
    prompt = f"""<|im_start|>system
You are a helpful AI assistant that answers questions based on provided documents.
{lang_instruction}
Be concise and accurate. Cite sources when possible.<|im_end|>
<|im_start|>user
Context:
{context_text}

Question: {question}

Answer:<|im_end|>
<|im_start|>assistant
"""
    
    output = llm(
        prompt,
        max_tokens=500,
        temperature=0.7,
        top_p=0.9,
        repeat_penalty=1.1,
        stop=["<|im_end|>", "<|im_start|>"],
        top_k=40
    )
    
    answer = output['choices'][0]['text'].strip()
    
    # Format answer with expandable sources
    answer += "\n\n📚 Sources:\n"
    for i, ctx in enumerate(contexts[:len(context_parts)], 1):
        source = ctx['metadata']['source']
        page = ctx['metadata']['page']
        content = ctx['doc']
        
        # Create expandable source with content
        answer += f"""\n<div class="source" onclick="toggleSource(this)">
  [{i}] {source} (Page {page}) ▼
  <div class="source-content">{content}</div>
</div>"""
    
    return answer


def rebuild_bm25_index():
    """Rebuild BM25 index"""
    global bm25, bm25_corpus
    from rank_bm25 import BM25Okapi
    
    all_docs = collection.get()
    if all_docs['documents']:
        bm25_corpus = all_docs['documents']
        tokenized_corpus = [doc.lower().split() for doc in bm25_corpus]
        bm25 = BM25Okapi(tokenized_corpus)


def init_models(desktop_app):
    """Initialize models from desktop app"""
    global llm, embedder, reranker, collection, chroma_client
    
    # Share the expensive models (LLM, embedder, reranker)
    llm = desktop_app.llm
    embedder = desktop_app.embedder
    reranker = desktop_app.reranker
    chroma_client = desktop_app.chroma_client
    
    # Create SEPARATE collection for web version
    try:
        collection = chroma_client.get_collection("web_documents")
    except:
        collection = chroma_client.create_collection("web_documents")
    
    rebuild_bm25_index()


def run_server(desktop_app, port=8502):
    """Run Bottle server"""
    init_models(desktop_app)
    app.run(host='localhost', port=port, quiet=True, debug=False)


if __name__ == '__main__':
    print("Starting Doqurix Web Server...")
    app.run(host='localhost', port=8502, quiet=False)
