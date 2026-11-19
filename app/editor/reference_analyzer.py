import json
import subprocess
from pathlib import Path
from fractions import Fraction


def analyze_reference_video(video_path: str) -> dict:
    path = Path(video_path)

    if not path.is_file():
        raise FileNotFoundError(f"Video not found: {video_path}")

    command = [
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json", str(path)
    ]

    result = subprocess.run(
        command, capture_output=True, text=True, check=True
    )

    data = json.loads(result.stdout)

    video = next(
        (s for s in data.get("streams", [])
         if s.get("codec_type") == "video"),
        None
    )

    audio = next(
        (s for s in data.get("streams", [])
         if s.get("codec_type") == "audio"),
        None
    )

    if video is None:
        raise ValueError("No video stream found")

    try:
        fps = float(Fraction(video.get("avg_frame_rate", "0/1")))
    except (ValueError, ZeroDivisionError):
        fps = 0.0

    width = video.get("width")
    height = video.get("height")

    return {
        "filename": path.name,
        "duration_seconds": float(data.get("format", {}).get("duration", 0)),
        "file_size_bytes": path.stat().st_size,
        "width": width,
        "height": height,
        "resolution": f"{width}x{height}",
        "fps": round(fps, 3),
        "frame_count": video.get("nb_frames"),
        "video_codec": video.get("codec_name"),
        "audio_present": audio is not None,
        "audio_codec": audio.get("codec_name") if audio else None,
        "analysis_status": "completed"
    }


def detect_scenes(video_path: str, threshold: float = 0.35) -> list:
    import re

    path = Path(video_path)

    if not path.is_file():
        raise FileNotFoundError(f"Video not found: {video_path}")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-i", str(path),
        "-an",
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])

    timestamps = re.findall(
        r"pts_time:([0-9]+(?:\.[0-9]+)?)",
        result.stderr
    )

    return [
        {
            "scene_number": index + 1,
            "timestamp_seconds": float(timestamp)
        }
        for index, timestamp in enumerate(timestamps)
    ]
