import os
import sys
import threading
import time
import requests
import zipfile
import shutil
import subprocess
import webview
import webbrowser
import win32com.client
from tkinter import Tk, filedialog

# --- RESOURCE CONFIGURATION ---
URL_HALO_VR = "https://github.com/LivingFray/HaloCEVR/releases/download/1.4.0/HaloCEVR.zip"
URL_CHIMERA = "https://github.com/SnowyMouse/chimera/releases/download/1.0.0r1200/chimera-1.0.0r1200.7z"
URL_DSOAL = "https://github.com/ThreeDeeJay/dsoal/releases/download/0.9.6/DSOAL+HRTF.zip"
URL_REFINED = "https://www.proxeninc.net/Halo/Refined/Refined%20V5%20Download/halo_refined_retail_en_v5.01.7z"

# Expected local filenames
PATCH_EXE_NAME = "halopc-patch-1.0.10.exe"
LOCAL_LAA_EXE = "halo.exe" 
LAUNCHER_EXE_NAME = "HaloLauncher.exe"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_install_files")
INTERFACE_PATH = os.path.join(BASE_DIR, "HALOCEVR_Installer.html")

class Api:
    def __init__(self):
        self.game_path = None
        self.installed_mods = []
        if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)

    def select_folder(self):
        """Native folder selection dialog."""
        root = Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory(title="Select Halo CE Root Folder / Seleccionar Carpeta Raíz")
        root.destroy()
        
        if folder_selected:
            if not os.path.exists(os.path.join(folder_selected, "halo.exe")) and \
               not os.path.exists(os.path.join(folder_selected, "halo.old.exe")):
                self.log("WARNING: halo.exe not found in target directory.")
            
            self.game_path = folder_selected
            return folder_selected
        return None

    def quit_app(self):
        self.log("Closing installer...")
        if 'window' in globals() and window:
            window.destroy()
        # Kill process to ensure threads don't hang
        os._exit(0)

    def open_url(self, url):
        webbrowser.open(url)

    def generate_log(self, lang):
        if not self.game_path: return
        try:
            log_path = os.path.join(self.game_path, "HaloVR_Install_Log.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                if lang == 'es':
                    f.write("=== REGISTRO DE INSTALACIÓN DE HALO CE VR ===\n")
                    f.write("=============================================\n\n")
                    f.write("El instalador ha modificado tu juego con los siguientes complementos:\n\n")
                    if 'core' in self.installed_mods:
                        f.write("- Núcleo VR: Parche 1.0.10 aplicado y motor HaloCEVR copiado.\n")
                    if 'chimera' in self.installed_mods:
                        f.write("- Chimera: Motor de interpolación integrado y archivo chimera.ini ajustado para VR.\n")
                    if 'laa' in self.installed_mods:
                        f.write("- Parche LAA: Ejecutable halo.exe actualizado para aprovechar 4GB de RAM.\n")
                    if 'audio' in self.installed_mods:
                        f.write("- Audio 3D (DSOAL): Bibliotecas HRTF espaciales configuradas con alsoft.ini.\n")
                    if 'refined' in self.installed_mods:
                        f.write("- Halo Refined: Mapas originales respaldados, campaña actualizada y HUD adaptado para VR.\n")
                    if 'shortcut' in self.installed_mods:
                        f.write("- Launcher Integrado: Se ha copiado 'Halo Launcher.exe' y creado un acceso directo en el escritorio.\n")
                    f.write("\n¡El proceso ha finalizado correctamente! Ya puedes ejecutar el juego.\n")
                else:
                    f.write("=== HALO CE VR INSTALLATION LOG ===\n")
                    f.write("===================================\n\n")
                    f.write("The installer modified your game directory with the following components:\n\n")
                    if 'core' in self.installed_mods:
                        f.write("- VR Core: Patch 1.0.10 applied and HaloCEVR engine copied.\n")
                    if 'chimera' in self.installed_mods:
                        f.write("- Chimera: Interpolation engine integrated and chimera.ini adjusted for VR.\n")
                    if 'laa' in self.installed_mods:
                        f.write("- LAA Patch: halo.exe updated to access 4GB of RAM.\n")
                    if 'audio' in self.installed_mods:
                        f.write("- 3D Audio (DSOAL): HRTF spatial libraries configured alongside alsoft.ini.\n")
                    if 'refined' in self.installed_mods:
                        f.write("- Halo Refined: Original maps backed up, campaign upgraded and VR HUD scaled.\n")
                    if 'shortcut' in self.installed_mods:
                        f.write("- Custom Launcher: 'Halo Launcher.exe' copied and desktop shortcut generated.\n")
                    f.write("\nProcess completed successfully! You can now launch the game.\n")
            self.log(f"Install log generated successfully at: {log_path}")
        except Exception as e:
            self.log(f"Error generating install log: {str(e)}")

    def log(self, message):
        print(f"[LOG] {message}")
        if 'window' in globals() and window:
            safe_msg = message.replace("\\", "\\\\").replace("'", "").replace('"', "")
            window.evaluate_js(f'updateConsole("{safe_msg}")')

    def update_progress_bar(self, percent):
        if 'window' in globals() and window:
            window.evaluate_js(f'updateProgress({percent})')

    def run_stage(self, stage_num):
        if not self.game_path:
            self.log("Error: Path not defined.")
            return
        thread = threading.Thread(target=self._execute_stage, args=(stage_num,))
        thread.start()

    def _execute_stage(self, stage_num):
        start_time = time.time()
        try:
            if stage_num == 1: self._stage_1_core_vr()
            elif stage_num == 2: self._stage_2_chimera()
            elif stage_num == 3: self._stage_3_laa()
            elif stage_num == 4: self._stage_4_audio()
            elif stage_num == 5: self._stage_5_refined()
            elif stage_num == 6: self._stage_6_shortcut()
            
            elapsed = time.time() - start_time
            if elapsed < 1.0: time.sleep(1.0 - elapsed)
            
            self.update_progress_bar(100)
            self.log("Module installed successfully.")
            time.sleep(0.5)

            if 'window' in globals() and window:
                window.evaluate_js(f'phaseComplete({stage_num})')

        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")
            if 'window' in globals() and window:
                clean_err = str(e).replace('"', "'").replace('\n', ' ')
                window.evaluate_js(f'installationError("{clean_err}")')

        finally:
            # Always ensure loader is hidden after failure or success
            if 'window' in globals() and window:
                window.evaluate_js('showExtractionLoader(false)')

    # --- FILE UTILITIES ---
    def _download_file(self, url, dest_path):
        self.log(f"Downloading: {os.path.basename(dest_path)}")
        try:
            r = requests.get(url, stream=True)
            total_length = r.headers.get('content-length')
            
            with open(dest_path, 'wb') as f:
                if total_length is None:
                    f.write(r.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for chunk in r.iter_content(chunk_size=8192):
                        dl += len(chunk)
                        f.write(chunk)
                        percent = int(100 * dl / total_length)
                        self.update_progress_bar(percent)
        except Exception as e:
            raise Exception(f"Download failed: {e}")

    def _extract_zip(self, archive, dest):
        self.log(f"Unzipping {os.path.basename(archive)}...")
        if 'window' in globals() and window:
            window.evaluate_js('showExtractionLoader(true)')
        try:
            with zipfile.ZipFile(archive, 'r') as z: 
                z.extractall(dest)
        finally:
            if 'window' in globals() and window:
                window.evaluate_js('showExtractionLoader(false)')

    def _extract_7z_robust(self, archive, dest):
        self.log("Extracting archive (7z) using local 7z.exe...")
        seven_zip_path = os.path.join(BASE_DIR, "7z.exe")
        
        if not os.path.exists(seven_zip_path):
            raise Exception("7z.exe not found in installer directory.")

        if 'window' in globals() and window:
            window.evaluate_js('showExtractionLoader(true)')
        try:
            subprocess.run([seven_zip_path, 'x', archive, f'-o{dest}', '-y'], 
                           check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            raise Exception(f"7z Extraction failed. Error: {str(e)}")
        finally:
            if 'window' in globals() and window:
                window.evaluate_js('showExtractionLoader(false)')

    def _backup_file(self, filename):
        target = os.path.join(self.game_path, filename)
        backup = os.path.join(self.game_path, filename.replace(".", ".old.", 1))
        
        if os.path.exists(target):
            if not os.path.exists(backup):
                try:
                    os.rename(target, backup)
                    self.log(f"Backup created: {filename} -> .old")
                    return True
                except:
                    pass
        return False

    # --- INSTALLATION PHASES ---

    def _stage_1_core_vr(self):
        self.log("--- MODULE 1: CORE VR ---")
        
        patch_path = os.path.join(BASE_DIR, PATCH_EXE_NAME)
        if os.path.exists(patch_path):
            self.log("Running Patch 1.0.10...")
            try:
                cmd = ["powershell", "Start-Process", f'"{patch_path}"', "-Wait"]
                subprocess.run(cmd, shell=True, check=True)
            except Exception as e:
                self.log(f"Patch 1.0.10 cancelled or failed: {str(e)}")
        else:
            self.log("Info: Patch 1.0.10 not found (skipping).")

        vr_zip = os.path.join(TEMP_DIR, "HaloCEVR.zip")
        if not os.path.exists(vr_zip): self._download_file(URL_HALO_VR, vr_zip)
        
        extract_path = os.path.join(TEMP_DIR, "HaloVR_Extracted")
        if os.path.exists(extract_path): shutil.rmtree(extract_path)
        
        self._extract_zip(vr_zip, extract_path)
        
        self.log("Installing files to directory...")
        shutil.copytree(extract_path, self.game_path, dirs_exist_ok=True)
        self.installed_mods.append('core')

    def _stage_2_chimera(self):
        self.log("--- MODULE 2: CHIMERA ENGINE ---")
        
        chimera_7z = os.path.join(TEMP_DIR, "chimera.7z")
        if not os.path.exists(chimera_7z): self._download_file(URL_CHIMERA, chimera_7z)
        
        ext_chimera = os.path.join(TEMP_DIR, "Chimera_Extracted")
        if os.path.exists(ext_chimera): shutil.rmtree(ext_chimera)
        
        self._extract_7z_robust(chimera_7z, ext_chimera)

        source_folder = ext_chimera
        items = os.listdir(ext_chimera)
        if len(items) == 1 and os.path.isdir(os.path.join(ext_chimera, items[0])):
            source_folder = os.path.join(ext_chimera, items[0])

        self._backup_file("strings.dll") 
        
        self.log("Copying Chimera libraries...")
        for item in os.listdir(source_folder):
            s = os.path.join(source_folder, item)
            d = os.path.join(self.game_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                if "readme" not in item.lower():
                    shutil.copy2(s, d)

        if not os.path.exists(os.path.join(self.game_path, "MODS")):
            os.makedirs(os.path.join(self.game_path, "MODS"))

        self.log("Configuring chimera.ini for VR...")
        self._configure_chimera_ini()
        self.installed_mods.append('chimera')

    def _configure_chimera_ini(self):
        ini_path = os.path.join(self.game_path, "chimera.ini")
        if not os.path.exists(ini_path): return

        with open(ini_path, "r", encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        new_lines = []
        in_font_override = False
        
        for line in lines:
            clean_line = line.strip()
            if clean_line == "[font_override]":
                in_font_override = True
                new_lines.append(line)
                continue
            if clean_line.startswith("[") and clean_line != "[font_override]":
                in_font_override = False

            if in_font_override and clean_line.startswith("enabled"):
                new_lines.append("enabled=0 ; Disabled by VR Installer\n")
            elif clean_line.startswith("enable_map_memory_buffer"):
                new_lines.append("enable_map_memory_buffer=1\n")
            else:
                new_lines.append(line)

        new_lines.append("\n; --- VR OPTIMIZATIONS ---\n")
        new_lines.append("chimera_block_mipmaps=1\n")
        new_lines.append("chimera_interpolation=1\n")
        new_lines.append("chimera_vsync=1\n")
        
        with open(ini_path, "w", encoding='utf-8') as f:
            f.writelines(new_lines)

    def _stage_3_laa(self):
        self.log("--- MODULE 3: LAA PATCH ---")
        local_laa_path = os.path.join(BASE_DIR, LOCAL_LAA_EXE)

        if os.path.exists(local_laa_path):
            self.log("Applying patched executable...")
            self._backup_file("halo.exe")
            shutil.copy2(local_laa_path, os.path.join(self.game_path, "halo.exe"))
            self.installed_mods.append('laa')
        else:
            self.log(f"ERROR: '{LOCAL_LAA_EXE}' not found locally.")

    def _stage_4_audio(self):
        self.log("--- MODULE 4: SPATIAL AUDIO ---")
        dsoal_zip = os.path.join(TEMP_DIR, "DSOAL_HRTF.zip")
        if not os.path.exists(dsoal_zip): self._download_file(URL_DSOAL, dsoal_zip)
        
        ext_audio = os.path.join(TEMP_DIR, "DSOAL_Extracted")
        self._extract_zip(dsoal_zip, ext_audio)

        self.log("Installing DSOAL libraries...")
        source_dir = ext_audio
        for root, dirs, files in os.walk(ext_audio):
            if "dsound.dll" in files:
                source_dir = root
                break

        files_needed = ['alsoft.ini', 'dsoal-aldrv.dll', 'dsound.dll']
        for file in files_needed:
            src = os.path.join(source_dir, file)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(self.game_path, file))

        self.log("Writing HRTF configuration...")
        alsoft_content = """[general]\nchannels=stereo\nfrequency=48000\nstereo-mode=headphones\ncf_level=0\nsources=512\nsample-type=float32\nhrtf=true\nhrtf-mode=full\nperiod_size=960\n\n[reverb]\nboost=-6"""
        
        with open(os.path.join(self.game_path, "alsoft.ini"), "w") as f:
            f.write(alsoft_content)
        self.installed_mods.append('audio')

    def _stage_5_refined(self):
        self.log("--- MODULE 5: HALO REFINED ---")
        
        refined_7z = os.path.join(TEMP_DIR, "halo_refined.7z")
        if not os.path.exists(refined_7z): 
            self._download_file(URL_REFINED, refined_7z)
        
        ext_refined = os.path.join(TEMP_DIR, "Refined_Extracted")
        if os.path.exists(ext_refined): 
            shutil.rmtree(ext_refined)
            
        self._extract_7z_robust(refined_7z, ext_refined)

        # 1. Backup original MAPS folder
        maps_dir = os.path.join(self.game_path, "MAPS")
        maps_backup = os.path.join(self.game_path, "MAPS_original")
        
        if os.path.exists(maps_dir) and not os.path.exists(maps_backup):
            self.log("Creating backup of MAPS folder (MAPS -> MAPS_original)...")
            shutil.copytree(maps_dir, maps_backup)
        else:
            self.log("MAPS_original backup exists or MAPS not found. Skipping.")

        # 2. Copy mod files over MAPS
        self.log("Installing Halo Refined maps...")
        source_maps = None
        for root, dirs, files in os.walk(ext_refined):
            if any(f.lower().endswith(".map") for f in files):
                source_maps = root
                break
                
        if source_maps:
            shutil.copytree(source_maps, maps_dir, dirs_exist_ok=True)
            self.log("Refined MAPS copied successfully.")
        else:
            self.log("WARNING: No .map files found in Refined download.")

        # 3. Apply HUD/Crosshair Fix for VR
        vr_config_path = os.path.join(self.game_path, "VR", "config.txt")
        if os.path.exists(vr_config_path):
            self.log("Adjusting UIOverlay in VR config...")
            try:
                with open(vr_config_path, "a", encoding="utf-8") as f:
                    f.write("\n\n//[Int] Width of the UI overlay in pixels (Default Value: 600)\n")
                    f.write("UIOverlayWidth = 1800\n")
                    f.write("//[Int] Height of the UI overlay in pixels (Default Value: 600)\n")
                    f.write("UIOverlayHeight = 1800\n")
                self.log("HUD fix applied correctly.")
            except Exception as e:
                self.log(f"Error writing to VR/config.txt: {str(e)}")
        else:
            self.log("WARNING: VR/config.txt not found. HUD fix skipped.")

        self.installed_mods.append('refined')

    def _stage_6_shortcut(self):
        self.log("--- MODULE 6: LAUNCHER & SHORTCUT ---")
        
        launcher_src = os.path.join(BASE_DIR, LAUNCHER_EXE_NAME)
        launcher_dst = os.path.join(self.game_path, LAUNCHER_EXE_NAME)
        
        if os.path.exists(launcher_src):
            self.log(f"Copying {LAUNCHER_EXE_NAME} to game directory...")
            try:
                shutil.copy2(launcher_src, launcher_dst)
            except Exception as e:
                self.log(f"Error copying launcher: {str(e)}")
        else:
            self.log(f"WARNING: '{LAUNCHER_EXE_NAME}' not found.")
            launcher_dst = None
            
        if not launcher_dst:
            self.log("Skipping shortcut creation: Source launcher not found.")
            return

        self.log("Generating Desktop Shortcut...")
        try:
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            shortcut_path = os.path.join(desktop, 'Halo CE Launcher.lnk')
            icon_path = os.path.join(self.game_path, "halo.exe")
            
            shell = win32com.client.Dispatch("WScript.Shell")
            acceso_directo = shell.CreateShortCut(shortcut_path)
            
            acceso_directo.TargetPath = launcher_dst
            acceso_directo.WorkingDirectory = self.game_path
            acceso_directo.IconLocation = f"{icon_path}, 0"
            acceso_directo.Save()
            
            self.installed_mods.append('shortcut')
            self.log("Shortcut created successfully.")
        except Exception as e:
            self.log(f"Error creating shortcut: {str(e)}")


if __name__ == '__main__':
    if not os.path.exists(INTERFACE_PATH):
        print(f"CRITICAL: {INTERFACE_PATH} not found.")
        sys.exit(1)

    api = Api()
    window = webview.create_window('UNSC | INSTALLER', url=f'file://{INTERFACE_PATH}', js_api=api, width=1200, height=800, resizable=False, background_color='#050505', frameless=True)
    webview.start()