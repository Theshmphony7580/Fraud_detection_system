let isInspectorActive = false;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_INSPECTOR_STATE') {
    sendResponse({ isActive: isInspectorActive });
  } else if (message.type === 'SET_INSPECTOR_STATE') {
    isInspectorActive = message.isActive;
    sendResponse({ success: true });
  } else if (message.type === 'SEND_POST_REQUEST') {
    // Handle POST request in background script to avoid CORS in content script
    fetch('https://aegisai-291s.onrender.com/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: message.text })
    })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        sendResponse({ success: true, response: JSON.stringify(data, null, 2) });
        console.log('POST request successful in background:', data);
      })
      .catch(error => {
        sendResponse({ success: false, error: `Failed to send POST request: ${error.message}` });
        console.error('POST request failed in background:', error);
      });
    // Return true to keep the message channel open for async response
    return true;
  }
});