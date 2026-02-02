import webview
import os
import sys
from api import Api

if __name__ == '__main__':
    api = Api()
    
    # Get absolute path to frontend/index.html
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(current_dir, 'frontend', 'index.html')
    
    if not os.path.exists(frontend_path):
        print(f"Error: Frontend file not found at {frontend_path}")
        # Create a dummy file if it doesn't exist to prevent crash loop during dev
        if not os.path.exists(os.path.join(current_dir, 'frontend')):
            os.makedirs(os.path.join(current_dir, 'frontend'))
        with open(frontend_path, 'w') as f:
            f.write("<h1>Frontend loading...</h1>")

    window = webview.create_window(
        'Advanced Notepad', 
        url=f'file:///{frontend_path}',
        js_api=api,
        width=1000,
        height=700,
        resizable=True,
        background_color='#1E1E1E'
    )
    
    api.set_window(window)
    webview.start(debug=True)
