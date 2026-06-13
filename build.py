import os
import subprocess
import shutil

def main():
    print("--- Compilation de l'application principale ---")
    app_cmd = [
        "py", "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--icon", "logo.ico",
        "--name", "Extracteur_3DMark",
        "--collect-data", "tkinterdnd2",
        "app.py"
    ]
    subprocess.run(app_cmd, check=True)
    
    print("--- Compilation de l'installateur avec Inno Setup ---")
    iscc_path = r"C:\Users\brunp\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    
    if os.path.exists(iscc_path):
        installer_cmd = [iscc_path, "installer.iss"]
        try:
            subprocess.run(installer_cmd, check=True)
            print("--- Terminé ! ---")
            print("L'installateur se trouve dans le dossier 'dist' : Install_Extracteur_3DMark.exe")
        except Exception as e:
            print(f"Erreur lors de la compilation de l'installateur: {e}")
    else:
        print("Erreur: Inno Setup (ISCC.exe) introuvable à l'emplacement par défaut.")

    # Cleanup intermediate files
    shutil.rmtree("build", ignore_errors=True)
    if os.path.exists("Extracteur_3DMark.spec"): os.remove("Extracteur_3DMark.spec")

if __name__ == "__main__":
    main()
