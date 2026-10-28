// CampusFix AI Assistant Client
let aiChatInitialized = false;
let aiChatOpen = false;
let aiIsSending = false;

function formatAiText(text) {
  // 1. Escape HTML for security
  let safe = esc(text);
  
  // 2. Bold text **text** -> <strong>text</strong>
  safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // 3. Bullet points • or - at start of line
  safe = safe.replace(/^[•\-]\s+(.*)$/gm, '<li>$1</li>');
  safe = safe.replace(/(<li>.*<\/li>)/gs, '<ul style="margin:6px 0;padding-left:18px">$1</ul>');
  
  // 4. Linebreaks
  safe = safe.replace(/\n/g, '<br>');
  
  // Clean double <br> inside/after <ul>
  safe = safe.replace(/<\/ul><br>/g, '</ul>');
  
  return safe;
}

function appendAiMessage(role, text, toolUsed = null) {
  const container = $('#aiMessages');
  if (!container) return;

  const msgEl = document.createElement('div');
  msgEl.className = `ai-msg ${role}`;

  let contentHtml = '';
  if (role === 'bot' && toolUsed) {
    const toolLabels = {
      count_unresolved_issues: '⚡ Live Issue Count',
      get_system_statistics: '📊 System Overview',
      get_recent_issues: '🔍 Live Issues',
      get_user_reported_issues: '📋 Your Account Records',
      get_issue_by_id: '🎯 Issue Details',
      get_issue_audit_history: '⏱️ Audit History'
    };
    const tools = toolUsed.split(',').map(t => t.trim()).filter(Boolean);
    contentHtml += `<div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:6px">`;
    tools.forEach(t => {
      const pillLabel = toolLabels[t] || `⚡ DB Tool: ${t}`;
      contentHtml += `<div class="ai-tool-pill">${esc(pillLabel)}</div>`;
    });
    contentHtml += `</div>`;
  }

  contentHtml += `<div class="ai-msg-text">${formatAiText(text)}</div>`;
  msgEl.innerHTML = contentHtml;

  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

function setAiTyping(isTyping) {
  aiIsSending = isTyping;
  const container = $('#aiMessages');
  const sendBtn = $('#aiSendBtn');
  const input = $('#aiInput');
  
  if (sendBtn) sendBtn.disabled = isTyping;
  if (input) input.disabled = isTyping;

  const existingTyping = $('#aiTypingIndicator');
  if (isTyping) {
    if (!existingTyping && container) {
      const typingEl = document.createElement('div');
      typingEl.id = 'aiTypingIndicator';
      typingEl.className = 'ai-typing';
      typingEl.innerHTML = `
        <span class="ai-typing-dot"></span>
        <span class="ai-typing-dot"></span>
        <span class="ai-typing-dot"></span>
      `;
      container.appendChild(typingEl);
      container.scrollTop = container.scrollHeight;
    }
  } else {
    if (existingTyping) existingTyping.remove();
    if (input) input.focus();
  }
}

async function sendAiMessage(messageText) {
  const text = (messageText || '').trim();
  if (!text || aiIsSending) return;

  // Clear input
  const input = $('#aiInput');
  if (input) input.value = '';

  // Render User Message
  appendAiMessage('user', text);
  setAiTyping(true);

  try {
    const res = await api('/chat/', {
      method: 'POST',
      json: { message: text }
    });

    setAiTyping(false);
    if (res && res.answer) {
      appendAiMessage('bot', res.answer, res.tool_used);
    } else {
      appendAiMessage('bot', "I couldn't process that response. Please try again.");
    }
  } catch (err) {
    setAiTyping(false);
    appendAiMessage('bot', `⚠️ ${err.message || 'Error communicating with AI assistant'}`);
  }
}

function showAiWelcome() {
  const container = $('#aiMessages');
  if (!container) return;
  container.innerHTML = '';
  appendAiMessage(
    'bot',
    "👋 Hello! I am your **CampusFix AI Assistant**.\n" +
    "I can look up live campus issue counts, summarize maintenance updates, or answer questions about your reported issues."
  );
}

function toggleAiChat(open) {
  aiChatOpen = typeof open === 'boolean' ? open : !aiChatOpen;
  const panel = $('#aiChatPanel');
  const fab = $('#aiFab');
  if (!panel) return;

  panel.classList.toggle('hide', !aiChatOpen);
  if (fab) fab.classList.toggle('active', aiChatOpen);

  if (aiChatOpen) {
    const container = $('#aiMessages');
    if (container && container.children.length === 0) {
      showAiWelcome();
    }
    setTimeout(() => $('#aiInput')?.focus(), 150);
  }
}

function closeAiChat() {
  toggleAiChat(false);
}

function initChatbot() {
  if (aiChatInitialized) return;
  aiChatInitialized = true;

  // 1. Floating button toggle
  const fab = $('#aiFab');
  if (fab) fab.onclick = () => toggleAiChat();

  // 2. Close & Clear buttons
  const closeBtn = $('#aiCloseBtn');
  if (closeBtn) closeBtn.onclick = closeAiChat;

  const clearBtn = $('#aiClearBtn');
  if (clearBtn) clearBtn.onclick = () => {
    showAiWelcome();
    toast('Chat history cleared');
  };

  // 3. Message submission form
  const form = $('#aiForm');
  if (form) {
    form.onsubmit = e => {
      e.preventDefault();
      const input = $('#aiInput');
      if (input && input.value) {
        sendAiMessage(input.value);
      }
    };
  }

  // 4. Suggestions Chips
  document.querySelectorAll('.ai-chip').forEach(chip => {
    chip.onclick = () => {
      const q = chip.dataset.q;
      if (q) sendAiMessage(q);
    };
  });
}
