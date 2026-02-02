const editor = document.getElementById('editor');
const statusBar = document.getElementById('statusBar');

// --- Real-Time Collaboration Logic ---
const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
const ws = new WebSocket(`${proto}://${window.location.host}/ws`);

ws.onopen = () => {
    console.log("Connected to Real-Time Server");
    showMessage("Live Sync: Online 🟢");
};

ws.onmessage = (event) => {
    // Determine cursor position to try and preserve it
    const cursorPosition = editor.selectionStart;
    editor.value = event.data;
    // Simple cursor handling - putting it back might be tricky if text length changed significantly
    // but better than resetting to 0.
    if (cursorPosition <= editor.value.length) {
        editor.setSelectionRange(cursorPosition, cursorPosition);
    }
};

ws.onclose = () => {
    showMessage("Live Sync: Offline 🔴");
};

// Send updates when typing
editor.addEventListener('input', () => {
    ws.send(editor.value);
});
// -------------------------------------

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

    // CHECK SECURE MODE
    const isSecure = document.getElementById('secureMode').checked;

    if (isSecure) {
        const password = prompt("Enter password to decrypt:");
        if (!password) return; // Cancelled

        const reader = new FileReader();
        reader.onload = async (e) => {
            const fileContent = e.target.result; // This is the encrypted string
            try {
                const response = await fetch('/api/open_secure', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: fileContent, password: password })
                });
                const data = await response.json();

                if (data.status === 'success') {
                    editor.value = data.content;
                    showMessage(`Decrypted: ${file.name}`);
                } else {
                    showMessage(`Error: ${data.message}`);
                }
            } catch (error) {
                showMessage(`Decryption Error: ${error}`);
            }
        };
        reader.readAsText(file);

    } else {
        // NORMAL OPEN
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
    }
    // Reset input
    event.target.value = '';
}

function saveFile() {
    // CHECK SECURE MODE
    const isSecure = document.getElementById('secureMode').checked;
    const content = editor.value;

    if (isSecure) {
        const password = prompt("Set a password for this file:");
        if (!password) return;

        showMessage("Encrypting...");
        fetch('/api/save_secure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content, password: password })
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    downloadString(data.encrypted_data, data.filename);
                    showMessage("Encrypted File Downloaded!");
                } else {
                    showMessage("Encryption Failed.");
                }
            });

    } else {
        // NORMAL SAVE
        showMessage("Downloading file...");
        downloadString(content, 'notepad_content.txt');
        showMessage("File downloaded!");
    }
}

function downloadString(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
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
    let user = document.getElementById('userSelect').value;

    if (!site || !user) {
        alert("Please select both a Site and a User.");
        return;
    }

    // Handle Custom User
    if (user === "Custom") {
        user = prompt("Enter your Name or Username to simulate:");
        if (!user) return; // Stop if cancelled or empty
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
