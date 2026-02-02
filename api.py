import os
import json
import webview
from tkinter import filedialog, Tk

class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def open_file(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        root.destroy()
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"status": "success", "content": content, "path": file_path}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "cancelled"}

    def save_file(self, content):
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            title="Save Text File",
            defaultextension=".txt",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        root.destroy()

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"status": "success", "path": file_path}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "cancelled"}
    
    def exit_app(self):
        if self._window:
            self._window.destroy()
    
    def login_user(self, site, user):
        # Simulate OAuth 2.0 redirection and backend storage
        print(f"Logging in user: {user} for site: {site}")
        
        # Store login info for John
        if user.lower() == "john":
            data = {"user": user, "site": site, "status": "logged_in"}
            try:
                with open("john_login_data.json", "w") as f:
                    json.dump(data, f)
            except Exception as e:
                print(f"Failed to save login data: {e}")

        # OAuth 2.0 Simulation URLs
        redirect_map = {
            "google": f"https://accounts.google.com/o/oauth2/v2/auth?client_id=SIMULATED_CLIENT_ID&redirect_uri=http://localhost&response_type=code&scope=profile&state={user}",
            "facebook": f"https://www.facebook.com/v12.0/dialog/oauth?client_id=SIMULATED_CLIENT_ID&redirect_uri=http://localhost&state={user}",
            "yahoo": f"https://api.login.yahoo.com/oauth2/request_auth?client_id=SIMULATED_CLIENT_ID&redirect_uri=http://localhost&response_type=code&state={user}",
            "reddit": f"https://www.reddit.com/api/v1/authorize?client_id=SIMULATED_CLIENT_ID&response_type=code&state={user}&redirect_uri=http://localhost&duration=permanent&scope=identity",
        }

        # Verification step: In a real app, we'd open a browser. 
        # Here we return the URL for the frontend to handle (e.g., open in system browser)
        target_url = redirect_map.get(site.lower())
        if not target_url:
            target_url = f"https://www.{site.lower()}.com"
        
        return {"status": "success", "url": target_url, "user": user}
