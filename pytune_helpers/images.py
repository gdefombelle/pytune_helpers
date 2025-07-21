from typing import Dict, Optional
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener  # 👈 nécessaire
from io import BytesIO

register_heif_opener()  # 👈 active le support des fichiers HEIC

def compress_image(image_bytes: bytes, max_side: int = 1024, quality: int = 80) -> BytesIO:
    image = Image.open(BytesIO(image_bytes))

    width, height = image.size
    ratio = max_side / max(width, height)
    new_size = (int(width * ratio), int(height * ratio))
    image = image.resize(new_size, Image.LANCZOS)

    output = BytesIO()
    image.convert("RGB").save(output, format="JPEG", quality=quality)
    output.seek(0)
    return output
def extract_gps_from_exif(exif_data: Dict) -> Optional[dict]:
    gps_info = exif_data.get("GPSInfo")
    if not gps_info:
        return None

    def _get(tag):
        for key, val in ExifTags.GPSTAGS.items():
            if val == tag:
                return gps_info.get(key)

    lat = _get("GPSLatitude")
    lat_ref = _get("GPSLatitudeRef")
    lon = _get("GPSLongitude")
    lon_ref = _get("GPSLongitudeRef")

    if lat and lon and lat_ref and lon_ref:
        def dms_to_decimal(dms, ref):
            d, m, s = [float(x) for x in dms]
            dec = d + m / 60 + s / 3600
            return -dec if ref in ["S", "W"] else dec

        return {
            "latitude": dms_to_decimal(lat, lat_ref),
            "longitude": dms_to_decimal(lon, lon_ref),
            "method": "EXIF"
        }

    return None


def compress_image_and_extract_metadata(image_bytes: bytes, max_side: int = 1024, quality: int = 80) -> tuple[BytesIO, dict]:
    image = Image.open(BytesIO(image_bytes))
    format_original = image.format
    width_original, height_original = image.size

    # Redimensionnement
    ratio = max_side / max(width_original, height_original)
    new_size = (int(width_original * ratio), int(height_original * ratio))
    image_resized = image.resize(new_size, Image.LANCZOS)

    # Compression JPEG
    output = BytesIO()
    image_resized.convert("RGB").save(output, format="JPEG", quality=quality)
    output.seek(0)

    # Extraction EXIF + GPS + optique
    exif_data_raw = {}
    optical_metadata = {}
    location = None

    try:
        exif_raw = image._getexif()
        if exif_raw:
            exif_data_raw = {
                ExifTags.TAGS.get(tag, tag): value
                for tag, value in exif_raw.items()
                if tag in ExifTags.TAGS
            }

            location = extract_gps_from_exif(exif_raw)

            focal_35 = exif_data_raw.get("FocalLengthIn35mmFilm")
            focal_native = exif_data_raw.get("FocalLength")
            camera_make = exif_data_raw.get("Make")
            camera_model = exif_data_raw.get("Model")

            optical_metadata = {
                "make": camera_make,
                "model": camera_model,
                "focal_length_mm": float(focal_native) if focal_native else None,
                "focal_length_35mm": int(focal_35) if focal_35 else None,
                "orientation": exif_data_raw.get("Orientation"),
                "exif_width": exif_data_raw.get("ExifImageWidth"),
                "exif_height": exif_data_raw.get("ExifImageHeight"),
            }

    except Exception:
        pass

    metadata = {
        "format_original": format_original,
        "size_original": {"width": width_original, "height": height_original},
        "size_compressed": {"width": new_size[0], "height": new_size[1]},
        "compression_ratio": ratio,
        "optics": optical_metadata,
        "exif": exif_data_raw
    }

    if location:
        metadata["location"] = location

    return output, metadata