import os
import sys
import subprocess
import webview

def get_game_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

GAME_DIR = get_game_dir()
EXE_PATH = os.path.join(GAME_DIR, "halo.exe")
D3D9_DLL = os.path.join(GAME_DIR, "d3d9.dll")
D3D9_BAK = os.path.join(GAME_DIR, "d3d9.old.dll")

class LauncherApi:
    def cancel(self):
        webview.windows[0].destroy()
        sys.exit(0)

    def set_vr_mode(self):
        try:
            if os.path.exists(D3D9_BAK):
                if os.path.exists(D3D9_DLL):
                    os.remove(D3D9_DLL)
                os.rename(D3D9_BAK, D3D9_DLL)
            self.run_game()
        except PermissionError:
            webview.windows[0].evaluate_js('showError("Permission Error: Run as Administrator or move the game out of Program Files.")')
        except Exception as e:
            escaped_error = str(e).replace('"', '\\"')
            webview.windows[0].evaluate_js(f'showError("Error: {escaped_error}")')

    def set_original_mode(self):
        try:
            if os.path.exists(D3D9_DLL):
                if os.path.exists(D3D9_BAK):
                    os.remove(D3D9_BAK)
                os.rename(D3D9_DLL, D3D9_BAK)
            self.run_game()
        except PermissionError:
            webview.windows[0].evaluate_js('showError("Permission Error: Run as Administrator or move the game out of Program Files.")')
        except Exception as e:
            escaped_error = str(e).replace('"', '\\"')
            webview.windows[0].evaluate_js(f'showError("Error: {escaped_error}")')

    def run_game(self):
        if not os.path.exists(EXE_PATH):
            escaped_path = EXE_PATH.replace("\\", "\\\\")
            webview.windows[0].evaluate_js(f'showError("halo.exe not found at: {escaped_path}")')
            return
        
        # Run the game and close the launcher
        subprocess.Popen([EXE_PATH], cwd=GAME_DIR)
        self.cancel()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Halo Launcher</title>
    <style>
        :root {
            --bg-color: #050505;
            --text-main: #ffffff;
            --text-muted: rgba(255, 255, 255, 0.3);
            --vr-color: #a8ffaa;
            --vr-color-dim: rgba(168, 255, 170, 0.3);
            --vr-color-bg: rgba(168, 255, 170, 0.1);
            --vr-color-glow: rgba(168, 255, 170, 0.2);
            --flat-color: #ffffff;
            --flat-color-dim: rgba(255, 255, 255, 0.3);
            --flat-color-bg: rgba(255, 255, 255, 0.1);
            --flat-color-glow: rgba(255, 255, 255, 0.2);
            --cancel-color: #ff5555;
            --cancel-color-dim: rgba(255, 85, 85, 0.3);
            --cancel-color-bg: rgba(255, 85, 85, 0.1);
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        body { 
            background-color: var(--bg-color); 
            color: var(--text-main); 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            overflow: hidden; 
            user-select: none;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-sizing: border-box;
        }

        .drag-area { -webkit-app-region: drag; height: 40px; width: 100%; position: absolute; top: 0; left: 0; z-index: 50; }
        .no-drag { -webkit-app-region: no-drag; position: relative; z-index: 60; }
        
        .bg-circle {
            position: absolute;
            width: 250px;
            height: 250px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 50%;
            animation: spin 40s linear infinite;
            pointer-events: none;
        }

        .container {
            z-index: 10;
            width: 100%;
            padding: 0 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 1rem;
            box-sizing: border-box;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 0.75rem;
            letter-spacing: 0.4em;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
        }

        .title {
            font-size: 1.5rem;
            font-weight: bold;
            letter-spacing: 0.1em;
            margin-bottom: 2rem;
            margin-top: 0;
            text-align: center;
            color: var(--text-main);
            filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
        }

        .button-group {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            width: 100%;
            margin-bottom: 1.5rem;
        }

        .btn { 
            width: 100%; 
            padding: 0.8rem; 
            font-family: inherit;
            font-weight: 700; 
            font-size: 1rem; 
            text-transform: uppercase; 
            letter-spacing: 0.1em; 
            cursor: pointer; 
            transition: all 0.2s; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px); 
            box-sizing: border-box;
        }
        
        .btn-vr { background: #101010; color: var(--vr-color); border: 1px solid var(--vr-color-dim); }
        .btn-vr:hover { background: var(--vr-color-bg); border-color: var(--vr-color); transform: scale(1.02); box-shadow: 0 0 15px var(--vr-color-glow); }
        
        .btn-flat { background: #101010; color: var(--flat-color); border: 1px solid var(--flat-color-dim); }
        .btn-flat:hover { background: var(--flat-color-bg); border-color: var(--flat-color); transform: scale(1.02); box-shadow: 0 0 15px var(--flat-color-glow); }
        
        .btn-cancel { 
            background: transparent; 
            color: var(--cancel-color); 
            font-size: 0.8rem; 
            padding: 0.5rem; 
            border: 1px solid transparent; 
            clip-path: none; 
            max-width: 200px;
            margin-top: 0.5rem;
        }
        .btn-cancel:hover { background: var(--cancel-color-bg); border-color: var(--cancel-color-dim); transform: scale(1.02); }

        #error-box {
            display: none;
            margin-top: 1rem;
            color: var(--cancel-color);
            font-size: 0.75rem;
            text-align: center;
            border: 1px solid var(--cancel-color-dim);
            background-color: var(--cancel-color-bg);
            padding: 0.5rem;
            width: 100%;
            box-sizing: border-box;
        }
    </style>
</head>
<body>
    <div class="drag-area pywebview-drag-region"></div>
    <div class="bg-circle"></div>
    
    <div class="container">
        <div class="subtitle">UNSC // SYSTEM</div>
        <h1 class="title">HALO LAUNCHER</h1>
        
        <div class="button-group no-drag">
            <button onclick="callApi('set_vr_mode')" class="btn btn-vr">
                START VR MODE
            </button>
            <button onclick="callApi('set_original_mode')" class="btn btn-flat">
                ORIGINAL MODE (FLAT)
            </button>
        </div>
        
        <button onclick="callApi('cancel')" class="btn btn-cancel no-drag">
            CANCEL
        </button>
        
        <div id="error-box"></div>
    </div>

    <script>
        function callApi(method) {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api[method]();
            } else {
                setTimeout(() => callApi(method), 50);
            }
        }
        
        function showError(msg) {
            const box = document.getElementById('error-box');
            box.innerText = msg;
            box.style.display = 'block';
            
            // Hide the error after 5 seconds
            setTimeout(() => {
                box.style.display = 'none';
            }, 5000);
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    webview.create_window(
        title='Halo Launcher',
        html=HTML_CONTENT,
        js_api=LauncherApi(),
        width=350,
        height=450,
        frameless=True,
        resizable=False,
        background_color='#050505',
        easy_drag=False
    )
    webview.start()