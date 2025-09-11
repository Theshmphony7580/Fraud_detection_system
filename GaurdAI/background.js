let isInspectorActive = false;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_INSPECTOR_STATE') {
    sendResponse({ isActive: isInspectorActive });
  } else if (message.type === 'SET_INSPECTOR_STATE') {
    isInspectorActive = message.isActive;
    sendResponse({ success: true });
  }
  // Return true to indicate async response if needed (not required here)
});