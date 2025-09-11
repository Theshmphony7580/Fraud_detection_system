document.addEventListener('DOMContentLoaded', () => {
  const activateBtn = document.getElementById('activateBtn');
  const status = document.getElementById('status');

  // Check current inspector state from background
  chrome.runtime.sendMessage({ type: 'GET_INSPECTOR_STATE' }, (response) => {
    if (chrome.runtime.lastError) {
      // Ignore background errors (rare)
      console.warn('Background state check failed:', chrome.runtime.lastError);
    } else if (response && response.isActive) {
      activateBtn.textContent = 'Deactivate Inspector';
      status.textContent = 'Inspector is active. Click to deactivate.';
    }
  });

  activateBtn.addEventListener('click', async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Skip if restricted URL (no content script)
      if (tab.url && (tab.url.startsWith('chrome://') || tab.url.startsWith('about:') || tab.url.startsWith('file://'))) {
        status.textContent = 'Error: Inspector not supported on this page (e.g., chrome:// URLs).';
        return;
      }

      const isActive = activateBtn.textContent === 'Deactivate Inspector';

      // Send message to content script with error handling
      const result = await chrome.tabs.sendMessage(tab.id, {
        type: isActive ? 'DEACTIVATE_INSPECTOR' : 'ACTIVATE_INSPECTOR'
      }).catch((error) => {
        if (error.message.includes('Receiving end does not exist')) {
          status.textContent = 'Error: Refresh the page and try again (content script not loaded).';
        } else {
          status.textContent = `Error: ${error.message}`;
        }
        console.error('Send message failed:', error);
        throw error; // Re-throw to prevent UI update
      });

      // Update UI based on new state (only if no error)
      if (isActive) {
        activateBtn.textContent = 'Activate Inspector';
        status.textContent = 'Inspector deactivated.';
        chrome.runtime.sendMessage({ type: 'SET_INSPECTOR_STATE', isActive: false });
      } else {
        activateBtn.textContent = 'Deactivate Inspector';
        status.textContent = 'Inspector activated! Hover and click elements.';
        chrome.runtime.sendMessage({ type: 'SET_INSPECTOR_STATE', isActive: true });
      }

      // Close popup after 1 second
      setTimeout(() => window.close(), 1000);
    } catch (error) {
      // Catch-all for any other errors
      status.textContent = 'Error: Could not toggle inspector. Try refreshing the page.';
      console.error('Toggle failed:', error);
    }
  });
});