let isInspectorActive = false;
let highlightedElement = null;
let previewBox = null;
let sidebar = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'ACTIVATE_INSPECTOR') {
    if (!isInspectorActive) activateInspector();
    sendResponse({ success: true });
  } else if (message.type === 'DEACTIVATE_INSPECTOR') {
    if (isInspectorActive) deactivateInspector();
    sendResponse({ success: true });
  }
});

function activateInspector() {
  isInspectorActive = true;
  document.body.style.cursor = 'crosshair';
  document.body.style.userSelect = 'none';
  document.addEventListener('mouseover', handleMouseOver);
  document.addEventListener('mouseout', handleMouseOut);
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('click', handleClick, true);
  console.log('Inspector activated');
}

function deactivateInspector() {
  isInspectorActive = false;
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  document.removeEventListener('mouseover', handleMouseOver);
  document.removeEventListener('mouseout', handleMouseOut);
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('click', handleClick, true);
  if (highlightedElement) {
    highlightedElement.style.outline = '';
    highlightedElement = null;
  }
  removePreview();
  console.log('Inspector deactivated');
}

function handleMouseOver(e) {
  if (!isInspectorActive) return;
  e.preventDefault();
  e.stopPropagation();
  if (highlightedElement) {
    highlightedElement.style.outline = '';
  }
  highlightedElement = e.target;
  highlightedElement.style.outline = '2px solid #007bff !important';
  showPreview(extractText(e.target), e.pageX, e.pageY);
}

function handleMouseOut(e) {
  if (!isInspectorActive || e.target !== highlightedElement) return;
  highlightedElement.style.outline = '';
  highlightedElement = null;
  removePreview();
}

function handleMouseMove(e) {
  if (!isInspectorActive || !previewBox) return;
  previewBox.style.left = (e.pageX + 5) + 'px';
  previewBox.style.top = (e.pageY + 5) + 'px';
}

async function handleClick(e) {
  if (!isInspectorActive) return;
  e.preventDefault();
  e.stopPropagation();
  const text = extractText(e.target);
  
  // Send text to background script for POST request (avoids CORS in content script)
  let postResponse = 'Pending...';
  chrome.runtime.sendMessage({
    type: 'SEND_POST_REQUEST',
    text: text
  }, (response) => {
    if (chrome.runtime.lastError) {
      postResponse = `Failed to send POST request: ${chrome.runtime.lastError.message}`;
      console.error('Message to background failed:', chrome.runtime.lastError);
    } else if (response.success) {
      postResponse = response.response
      postResponse = JSON.stringify(response.response, null, 2);

    } else {
      postResponse = response.error;
      
    }
    showSidebar(text, postResponse);
    deactivateInspector(); // Disable inspector mode after opening sidebar
  });
}

function extractText(element) {
  return (element.innerText || element.textContent || element.value || '').trim();
}

function showPreview(text, x, y) {
  removePreview();
  previewBox = document.createElement('div');
  previewBox.id = 'element-inspector-preview';
  previewBox.style.cssText = `
    position: fixed;
    background: #ffffff;
    border: 1px solid #cccccc;
    padding: 8px;
    z-index: 1000000;
    max-width: 300px;
    max-height: 100px;
    overflow: hidden;
    font-size: 12px;
    font-family: Arial, sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    pointer-events: none;
    white-space: nowrap;
    text-overflow: ellipsis;
    color: #000000;
    left: ${x + 5}px;
    top: ${y + 5}px;
  `;
  previewBox.textContent = text || '[No text content]';
  document.body.appendChild(previewBox);
}

function removePreview() {
  if (previewBox) {
    previewBox.remove();
    previewBox = null;
  }
}

function showSidebar(text, postResponse) {
  removeSidebar();
  sidebar = document.createElement('div');
  sidebar.id = 'element-inspector-sidebar';
  sidebar.style.cssText = `
    position: fixed;
    right: 0;
    top: 0;
    width: 300px;
    height: 100vh;
    background: #ffffff;
    border-left: 2px solid #007bff;
    z-index: 1000000;
    padding: 15px;
    box-shadow: -2px 0 8px rgba(0,0,0,0.1);
    font-family: Arial, sans-serif;
    box-sizing: border-box;
    overflow-y: auto;
  `;
  sidebar.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
      <h3 style="margin: 0; font-size: 16px; color: #333;">Element Inspector</h3>
      <button id="close-sidebar" style="background: #f0f0f0; border: 1px solid #ccc; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">Close</button>
    </div>
    <div style="margin-bottom: 15px;">
      <h4 style="margin: 0 0 5px; font-size: 14px; color: #333;">Selected Text</h4>
      <textarea id="inspector-textarea" style="width: 101%; height: 150px; padding: 8px; border: 1px solid #000000ff;color: #000000ff; border-radius: 4px; font-size: 14px; resize: vertical;" readonly>${text}</textarea>
    </div>
    <div>
      <h4 style="margin: 0 0 5px; font-size: 14px; color: #333;">API Response</h4>
      <pre style="background: #f5f5f5; padding: 8px; border: 1px solid #000000ff; border-radius: 4px; font-size: 12px;color: #000000; max-height: 150px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word;">${postResponse}</pre>
    </div>
    <p style="font-size: 12px; color: #666; margin-top: 10px;">Text extracted and sent to API.</p>
  `;
  document.body.appendChild(sidebar);

  sidebar.querySelector('#close-sidebar').addEventListener('click', () => {
    removeSidebar();
    chrome.runtime.sendMessage({ type: 'SET_INSPECTOR_STATE', isActive: false });
  });
}

function removeSidebar() {
  if (sidebar) {
    sidebar.remove();
    sidebar = null;
  }
}

window.addEventListener('beforeunload', () => {
  if (isInspectorActive) {
    deactivateInspector();
    chrome.runtime.sendMessage({ type: 'SET_INSPECTOR_STATE', isActive: false });
  }
});