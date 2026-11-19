
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.editor.video_engine import get_video_info

app = FastAPI(
    title="Cloud Video Editor",
    description="Free cloud-based AI video editing workspace",
    version="0.2.0"
)

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def home():
    return {
        "project": "Cloud Video Editor",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "Cloud Video Editor"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    extension = Path(file.filename).suffix.lower()
    allowed = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

    if extension not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported video format")

    destination = UPLOAD_DIR / f"uploaded_video{extension}"

    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        info = get_video_info(str(destination))

        return {
            "status": "uploaded",
            "filename": file.filename,
            "video_info": info
        }

    except Exception as error:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(error))

    finally:
        await file.close()
