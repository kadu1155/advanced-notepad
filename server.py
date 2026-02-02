from fastapi import FastAPI, Body, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
import os
import json
import random
import time
import uuid
import base64
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = FastAPI()

# --- Real-Time Collaboration Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str, sender: WebSocket):
        for connection in self.active_connections:
            if connection != sender: # Don't send back to the person who typed it
                await connection.send_text(message)

manager = ConnectionManager()

# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class SaveRequest(BaseModel):
    content: str

class SecureRequest(BaseModel):
    content: str
    password: str

# --- Helper for Encryption ---
def get_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# API Endpoints
@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')

@app.get("/success")
def success_page(user: str, site: str, session_id: str = None):
    # Load the saved data for the specific session
    saved_data = "No data found"
    
    # Try loading from specific session file first (New Way)
    if session_id:
        file_name = f"login_data_{session_id}.json"
        if os.path.exists(file_name):
            try:
                with open(file_name, "r") as f:
                    saved_data = json.dumps(json.load(f), indent=4)
            except:
                pass
    
    # Fallback for old links (Legacy Way)
    if saved_data == "No data found":
        file_name = f"{user.lower()}_login_data.json"
        if os.path.exists(file_name):
            try:
                with open(file_name, "r") as f:
                    saved_data = json.dumps(json.load(f), indent=4)
            except:
                pass

    site_url = f"https://www.{site.lower()}.com"
    
    html_content = f"""
    <html>
        <head>
            <title>{site} - {user}'s Dashboard</title>
            <style>
                body {{ background: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; margin: 0; padding: 0; }}
                nav {{ background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(12px); padding: 15px 40px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; }}
                .brand {{ font-size: 1.5rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; }}
                .container {{ max-width: 1000px; margin: 40px auto; padding: 20px; }}
                .hero {{ background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 24px; padding: 40px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.05); text-align: center; }}
                h1 {{ font-size: 2.5rem; margin-bottom: 10px; color: #f1f5f9; }}
                .status-badge {{ background: #10b981; color: white; padding: 6px 12px; border-radius: 99px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 20px; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .card {{ background: #1e293b; padding: 25px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); }}
                .card h3 {{ color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }}
                .data-row {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.95rem; }}
                .data-label {{ color: #64748b; }}
                .data-value {{ color: #38bdf8; font-family: 'Mono', monospace; }}
                .btn {{ background: #38bdf8; color: #012; border: none; padding: 12px 24px; border-radius: 12px; cursor: pointer; text-decoration: none; font-weight: 700; transition: all 0.2s; display: inline-block; margin-top: 20px; }}
                .btn:hover {{ transform: scale(1.02); box-shadow: 0 0 20px rgba(56, 189, 248, 0.4); }}
                .btn-outline {{ background: transparent; border: 1px solid #38bdf8; color: #38bdf8; }}
            </style>
        </head>
        <body>
            <nav>
                <div class="brand">{site}</div>
                <div>Signed in as <strong>{user}</strong></div>
            </nav>
            <div class="container">
                <div class="hero">
                    <div class="status-badge">AUTO-LOGIN SUCCESSFUL</div>
                    <h1>Welcome back, {user}!</h1>
                    <p>Your {site} account has been automatically synchronized via MyPad PRO.</p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>Session Metadata</h3>
                        <div class="data-row"><span class="data-label">Email</span> <span class="data-value">{user.lower()}@{site.lower()}.com</span></div>
                        <div class="data-row"><span class="data-label">IP Address</span> <span class="data-value">192.168.{random.randint(1,254)}.{random.randint(1,254)}</span></div>
                        <div class="data-row"><span class="data-label">Timestamp</span> <span class="data-value">{time.strftime("%H:%M:%S")}</span></div>
                        <div class="data-row"><span class="data-label">Token</span> <span class="data-value">********</span></div>
                    </div>
                    
                    <div class="card">
                        <h3>Raw Login Data</h3>
                        <pre style="color: #10b981; font-size: 0.85rem; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; height: 120px; overflow: auto;">{saved_data}</pre>
                    </div>
                </div>

                <div style="text-align: center; margin-top: 40px;">
                    <a href="/" class="btn btn-outline">Back to Notepad</a>
                    <a href="https://www.{site.lower()}.com" target="_blank" class="btn">Go to Real {site}</a>
                </div>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/open")
async def open_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return {"status": "success", "content": content.decode('utf-8'), "filename": file.filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/save_secure")
def save_secure(data: SecureRequest):
    try:
        # Generate a random salt
        salt = os.urandom(16)
        key = get_key(data.password, salt)
        f = Fernet(key)
        encrypted_content = f.encrypt(data.content.encode())
        
        # Combine salt + encrypted content so we can decrypt later
        final_data = base64.b64encode(salt + encrypted_content).decode('utf-8')
        
        return {"status": "success", "encrypted_data": final_data, "filename": "secure_note.enc"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/open_secure")
def open_secure(data: SecureRequest):
    try:
        # Decode the file data
        raw_data = base64.b64decode(data.content)
        
        # Extract salt (first 16 bytes) and content
        salt = raw_data[:16]
        encrypted_content = raw_data[16:]
        
        key = get_key(data.password, salt)
        f = Fernet(key)
        
        decrypted_content = f.decrypt(encrypted_content).decode('utf-8')
        return {"status": "success", "content": decrypted_content}
    except Exception:
        # Generic error message to avoid leaking info
        return {"status": "error", "message": "Invalid password or corrupted file."}

@app.post("/api/login")
def login_user(data: dict = Body(...)):
    site = data.get("site")
    user = data.get("user")
    
    # Generate unique session ID for web isolation
    unique_session_id = str(uuid.uuid4())
    
    # Generate random metadata and MOCK CREDENTIALS
    login_info = {
        "user": user,
        "site": site,
        "email": f"{user.lower()}@{site.lower()}.com",
        "mock_password": f"{user[::-1].lower()}@2024",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": unique_session_id, # Use REAL unique ID
        "ip_address": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
        "access_token": f"at_{random.getrandbits(64):x}",
        "status": "active_session"
    }
    
    # Save to UNIQUE file to avoid collisions on web server
    file_name = f"login_data_{unique_session_id}.json"
    try:
        with open(file_name, "w") as f:
            json.dump(login_info, f, indent=4)
    except Exception as e:
        print(f"Failed to save login data: {e}")

    target_url = f"/success?user={user}&site={site}&session_id={unique_session_id}"
    return {"status": "success", "url": target_url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
