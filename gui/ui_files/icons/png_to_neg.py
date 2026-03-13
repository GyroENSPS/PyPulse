import os
from PIL import Image, ImageOps

def main():
    # Récupérer le dossier où se trouve le script
    folder = os.path.dirname(os.path.abspath(__file__))

    # Lister les fichiers du dossier
    for filename in os.listdir(folder):
        if filename.lower().endswith(".png"):
            filepath = os.path.join(folder, filename)

            # Ouvrir l'image
            img = Image.open(filepath)

            # Convertir en RGB si nécessaire (certaines PNG sont en mode 'RGBA' ou 'P')
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # Appliquer le négatif
            if img.mode == "RGBA":
                # Séparer les canaux pour préserver l'alpha
                r, g, b, a = img.split()
                rgb = Image.merge("RGB", (r, g, b))
                neg_rgb = ImageOps.invert(rgb)
                img_neg = Image.merge("RGBA", (*neg_rgb.split(), a))
            else:
                img_neg = ImageOps.invert(img)

            # Construire le nom du nouveau fichier
            name, ext = os.path.splitext(filename)
            new_name = f"{name}_neg.png"
            new_path = os.path.join(folder, new_name)

            # Sauvegarder l'image
            img_neg.save(new_path)

            print(f"✔ Image traitée : {filename} → {new_name}")

if __name__ == "__main__":
    main()