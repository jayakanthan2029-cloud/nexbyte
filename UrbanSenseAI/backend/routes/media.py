from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.config import settings, BASE_DIR
from backend import models, schemas

router = APIRouter(prefix="/media", tags=["Media"])

MEDIA_ROOT = (BASE_DIR / settings.MEDIA_DIR).resolve()

@router.get("/{media_id}", response_model=schemas.MediaResponse)
def get_media_metadata(media_id: int, db: Session = Depends(get_db)):
    """Retrieve metadata record for a media item."""
    media_item = db.query(models.Media).filter(models.Media.id == media_id).first()
    if not media_item:
        raise HTTPException(status_code=404, detail="Media not found")
    return media_item

@router.get("/file/{subpath:path}")
def stream_media_file(subpath: str):
    """Safely stream media files (images/videos) preventing path traversal."""
    # Resolve safe path inside MEDIA_ROOT
    safe_path = (MEDIA_ROOT / subpath).resolve()

    # Path traversal check
    if not str(safe_path).startswith(str(MEDIA_ROOT)):
        raise HTTPException(status_code=403, detail="Access denied: invalid file path")

    if not safe_path.exists() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail=f"Media file '{subpath}' not found")

    # Determine media mime type
    suffix = safe_path.suffix.lower()
    media_type = "application/octet-stream"
    if suffix in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"
    elif suffix == ".png":
        media_type = "image/png"
    elif suffix == ".mp4":
        media_type = "video/mp4"
    elif suffix == ".webm":
        media_type = "video/webm"

    return FileResponse(path=safe_path, media_type=media_type, filename=safe_path.name)
