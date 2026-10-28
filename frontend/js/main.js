initAuth();
initIssues();
initChatbot();
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeLayer();
    if (typeof closeAiChat === 'function') closeAiChat();
  }
});
show();
