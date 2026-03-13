from PIL import Image

def convert_png_to_ico(input_png, output_ico, size):
    """
    Convertit un PNG en ICO avec UNE SEULE résolution exacte.
    """

    img = Image.open(input_png).convert("RGBA")

    # Redimensionner exactement à la taille choisie
    img = img.resize((size, size), Image.LANCZOS)

    # Sauvegarder l'ICO avec *uniquement* cette résolution
    img.save(output_ico, format="ICO", sizes=[(size, size)])

    print(f"✓ Fichier ICO généré : {output_ico} ({size}x{size}) strict")


if __name__ == "__main__":
    print("=== Convertisseur PNG → ICO ===")
    input_png = input("Chemin du fichier PNG : ")
    output_ico = input("Chemin de sortie (ex: icone.ico) : ")

    print("\nChoisir la résolution :")
    print("1 : 16x16")
    print("2 : 32x32")
    print("3 : 48x48")
    print("4 : 64x64")
    print("5 : 128x128")
    print("6 : 256x256")

    choices = {
        "1": 16,
        "2": 32,
        "3": 48,
        "4": 64,
        "5": 128,
        "6": 256,
    }

    choice = input("\nVotre choix : ")

    if choice not in choices:
        print("❌ Choix invalide.")
    else:
        size = choices[choice]
        convert_png_to_ico(input_png, output_ico, size)
