from fastapi import FastAPI, Body, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
import os
import json
import random
import time

app = FastAPI()

# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class SaveRequest(BaseModel):
    content: str

# API Endpoints
@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')

@app.get("/success")
def success_page(user: str, site: str):
    # Load the saved data for the specific user
    saved_data = "No data found"
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

@app.post("/api/login")
def login_user(data: dict = Body(...)):
    site = data.get("site")
    user = data.get("user")
    
    # Generate random metadata and MOCK CREDENTIALS
    login_info = {
        "user": user,
        "site": site,
        "email": f"{user.lower()}@{site.lower()}.com",
        "mock_password": f"{user[::-1].lower()}@2024",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": f"sess_{random.randint(10000, 99999)}",
        "ip_address": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
        "access_token": f"at_{random.getrandbits(64):x}",
        "status": "active_session"
    }
    
    file_name = f"{user.lower()}_login_data.json"
    try:
        with open(file_name, "w") as f:
            json.dump(login_info, f, indent=4)
    except Exception as e:
        print(f"Failed to save login data: {e}")

    target_url = f"/success?user={user}&site={site}"
    return {"status": "success", "url": target_url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
