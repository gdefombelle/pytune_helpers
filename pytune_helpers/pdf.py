from io import BytesIO
import uuid
from pytune_data.minio_client import minio_client, PIANO_SESSIONS_PDF_BUCKET
from datetime import timedelta

async def upload_pdf_and_get_url(pdf_buffer: BytesIO, filename_prefix="piano_report") -> str:
    """
    Upload le PDF dans MinIO et retourne une URL publique ou presignée
    """
    
    minio_client.ensure_bucket_exists()  # just in case

    pdf_buffer.seek(0)
    object_name = f"{filename_prefix}_{uuid.uuid4().hex}.pdf"

    # Upload dans MinIO
    minio_client.client.put_object(
        bucket_name=PIANO_SESSIONS_PDF_BUCKET,
        object_name=object_name,
        data=pdf_buffer,
        length=-1,  # on utilise les chunks
        part_size=10 * 1024 * 1024,  # 10 Mo
        content_type="application/pdf"
    )

    # Génère une URL presignée (valable 7 jours ici)
    url = minio_client.client.presigned_get_object(
        bucket_name=PIANO_SESSIONS_PDF_BUCKET,
        object_name=object_name,
        expires=timedelta(days=7)
    )

    return url
