from PIL import Image
from io import BytesIO

def compress_image(image_bytes: bytes, max_side: int = 1024, quality: int = 80) -> BytesIO:
    image = Image.open(BytesIO(image_bytes))

    # Déterminer la nouvelle taille en gardant les proportions
    width, height = image.size
    ratio = max_side / max(width, height)
    new_size = (int(width * ratio), int(height * ratio))
    image = image.resize(new_size, Image.LANCZOS)

    # Réencoder l’image en JPEG dans un buffer mémoire
    output = BytesIO()
    image.convert("RGB").save(output, format="JPEG", quality=quality)
    output.seek(0)
    return output
