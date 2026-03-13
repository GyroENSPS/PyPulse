import subprocess
import os

# === Paramètres à personnaliser ===
ui_file = 'ui_files/PS_main.ui'
py_file = 'ui_files/py_files/UI_PS_main.py'

# === Commande pyuic5 ===
command = f"pyuic5 -x {ui_file} -o {py_file}"

# === Exécution ===
try:
    subprocess.run(command, check=True, shell=True)
    print(f"✅ Fichier .ui converti avec succès : {py_file}")

except subprocess.CalledProcessError as e:
    print("❌ Erreur lors de la conversion du fichier .ui")
    print(e)

# end not necessary if ressources.py is in the same folder as the ui.py

try:
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remplacement de l’import
    content = content.replace(
        "import resources_rc",
        "from gui.ui_files.py_files import resources_rc"
    )

    with open(py_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("🔧 Import 'resources_rc' corrigé automatiquement.")

except Exception as e:
    print("❌ Erreur lors de la modification du fichier généré")
    print(e)

