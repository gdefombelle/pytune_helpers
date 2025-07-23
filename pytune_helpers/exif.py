# exif.py

import exifread
from io import BytesIO
from typing import Optional


def extract_exif_with_exifread(image_bytes: bytes) -> dict:
    """
    Extrait les métadonnées EXIF lisibles depuis un fichier image, en évitant les objets non sérialisables.
    Retourne un dictionnaire avec des clés de type "EXIF FocalLength", "GPS GPSLatitude", etc.
    """
    tags = {}
    try:
        stream = BytesIO(image_bytes)
        tags_raw = exifread.process_file(stream, details=False)
        for tag, value in tags_raw.items():
            try:
                tags[tag] = str(value)
            except Exception:
                tags[tag] = repr(value)
    except Exception as e:
        tags["error"] = str(e)
    return tags


def extract_gps_from_exifread(tags: dict) -> Optional[dict]:
    """
    Extrait la latitude et la longitude (en décimal) si disponibles dans les tags EXIF GPS.
    """
    try:
        lat = tags.get("GPS GPSLatitude")
        lat_ref = tags.get("GPS GPSLatitudeRef")
        lon = tags.get("GPS GPSLongitude")
        lon_ref = tags.get("GPS GPSLongitudeRef")

        if not all([lat, lat_ref, lon, lon_ref]):
            return None

        def _dms_to_decimal(dms_str, ref):
            parts = [eval(x.strip()) for x in dms_str.strip("[]").split(",")]
            degrees, minutes, seconds = parts
            decimal = degrees + minutes / 60 + seconds / 3600
            return -decimal if ref in ["S", "W"] else decimal

        return {
            "latitude": _dms_to_decimal(lat, lat_ref),
            "longitude": _dms_to_decimal(lon, lon_ref),
            "method": "EXIFREAD"
        }
    except Exception:
        return None
