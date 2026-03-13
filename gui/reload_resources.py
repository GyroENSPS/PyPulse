import os
import subprocess
import sys


def compile_qrc(qrc_file, output_py="resources_rc.py"):
    """
    Compile un fichier .qrc en fichier .py pour PyQt5/PyQt6.
    """

    if not os.path.exists(qrc_file):
        print(f"❌ Le fichier {qrc_file} n'existe pas.")
        return

    # Détection automatique du compilateur
    commands = ["pyrcc5", "pyrcc6"]

    for cmd in commands:
        try:
            # Test si la commande existe
            subprocess.run([cmd, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print(f"➡️ Compilation avec : {cmd}")
            subprocess.run([cmd, qrc_file, "-o", output_py], check=True)

            print(f"✅ Fichier généré : {output_py}")
            return

        except Exception:
            continue

    print("❌ Aucun compilateur Qt Resource Compiler trouvé.")
    print("Installe PyQt5 ou PyQt6 ou ajoute pyrcc5/pyrcc6 au PATH.")


if __name__ == "__main__":


    compile_qrc("ui_files/resources.qrc", "ui_files/py_files/resources_rc.py")
