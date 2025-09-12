🛡️ Fraud Message Detection Extension
<p align="center"> <img src="GuardAI/icons/icon128.png" alt="Extension Banner" width="800"/> </p> <p align="center"> A browser extension that helps you **detect fraudulent or scam messages instantly**. Select suspicious text, and let the AI-powered system analyze it for you. </p>
✨ Features

✅ One-click Activation – Activate directly from the extension popup.
✅ Text Extraction – Simply click on any text to capture it.
✅ Real-time Analysis – Sends the text via a POST request to the backend AI.
✅ Sidebar Report – Instantly see if the text is Legit ✅ or a Scam 🚨.
✅ Clean & Intuitive UI – Easy-to-use sidebar interface.

<p align="center"> <img src="images/demo1.png" alt="Demo Screenshot" width="700"/> </p>
🚀 How It Works

Open the Extension
Click the extension icon in your browser.

<p align="center"> <img src="images/open-extension.png" alt="Open Extension" width="600"/> </p>

Activate Inspector Mode
Press the Activate button to enable text selection.

<p align="center"> <img src="images/activate.png" alt="Activate Extension" width="600"/> </p>

Select Suspicious Text
Just click on the message you want to analyze. The extension will automatically extract it.

<p align="center"> <img src="images/select-text.png" alt="Select Text" width="600"/> </p>

Get Instant Results
The sidebar will slide in with the analysis result:

✅ Legit message

🚨 Scam detected

<p align="center"> <img src="images/sidebar.png" alt="Sidebar Result" width="600"/> </p>
🛠️ Installation
1. Clone the Repo
git clone https://github.com/your-username/fraud-message-detection.git

2. Load Extension in Browser

Open Chrome / Edge and go to:

chrome://extensions/


Enable Developer Mode (top right).

Click Load unpacked.

Select the project folder.

That’s it! 🎉 Your extension is ready.

📂 Project Structure
fraud-message-detection/
│── background.js       # Handles background logic
│── content.js          # Injected into web pages for text extraction
│── popup.html          # Extension popup UI
│── popup.js            # Popup logic
│── sidebar.html        # Sidebar UI
│── sidebar.js          # Sidebar logic
│── manifest.json       # Extension manifest
│── styles/             # CSS files
│── images/             # Placeholder for icons/screenshots

📸 Screenshots

Extension Popup
<img src="images/popup.png" alt="Popup UI" width="600"/>

Sidebar Analysis
<img src="images/sidebar.png" alt="Sidebar UI" width="600"/>

Scam Detection Example
<img src="images/example-scam.png" alt="Scam Example" width="600"/>

🔮 Future Improvements

🌍 Multi-language support

📊 Detailed scam probability score

🧠 Offline ML model integration

🎨 Customizable sidebar theme

🤝 Contributing

Contributions are welcome! 🎉

Fork this repo

Create a new branch

Submit a PR
