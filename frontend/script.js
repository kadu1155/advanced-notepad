// DOM Elements
const editor = document.getElementById('editor');
const statusBar = document.getElementById('statusBar');

// Undo/Redo Management 
function undo() {
    editor.focus();
    document.execCommand('undo');
}

function redo() {
    editor.focus();
    document.execCommand('redo');
}

function fillRandomData() {
    editor.focus();
    const randomTexts = [
        "In a hole in the ground there lived a hobbit.",
        "The quick brown fox jumps over the lazy dog.",
        "To be or not to be, that is the question.",
        "The only thing we have to fear is fear itself.",
        "Coding is the language of the future.",
        "Innovation distinguishes between a leader and a follower."
    ];
    const randomText = randomTexts[Math.floor(Math.random() * randomTexts.length)];
    editor.value += (editor.value ? "\n" : "") + randomText;
    showMessage("Added random text!");
}

// API Calls to Backend via Fetch
function openFile() {
    document.getElementById('fileInput').click();
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showMessage(`Reading ${file.name}...`);
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/open', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.status === 'success') {
            editor.value = data.content;
            showMessage(`Loaded: ${data.filename}`);
        } else {
            showMessage(`Error: ${data.message}`);
        }
    } catch (error) {
        showMessage(`Upload Error: ${error}`);
    }
    // Reset input
    event.target.value = '';
}

function saveFile() {
    showMessage("Downloading file...");
    const content = editor.value;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'notepad_content.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    showMessage("File downloaded!");
}

async function exitApp() {
    if (confirm("Are you sure you want to close the server?")) {
        fetch('/api/exit', { method: 'POST' });
        window.close();
        document.body.innerHTML = "<h1>Server Stopped. You can close this tab.</h1>";
    }
}

async function handleLogin() {
    const site = document.getElementById('siteSelect').value;
    const user = document.getElementById('userSelect').value;

    if (!site || !user) {
        alert("Please select both a Site and a User.");
        return;
    }

    showMessage(`Logging in ${user} to ${site}...`);
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ site: site, user: user })
        });
        const data = await response.json();

        if (data.status === 'success') {
            showMessage(`Redirecting...`);
            window.location.href = data.url;
        }
    } catch (error) {
        showMessage(`Login Error: ${error}`);
    }
}

function showMessage(msg) {
    statusBar.textContent = msg;
    setTimeout(() => {
        if (statusBar.textContent === msg) {
            statusBar.textContent = "Ready";
        }
    }, 3000);
}
