
import subprocess
import os


def get_video_info(video_path: str):
    """Extract basic video information using FFmpeg."""

    if not os.path.exists(video_path):
        raise FileNotFoundError("Video file not found")

    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,size",
        "-of", "json",
        video_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout

def trim_video(input_path: str, output_path: str, start: float, duration: float):
    """Trim a video using FFmpeg."""

    if not os.path.isfile(input_path):
        raise FileNotFoundError("Input video not found")

    if start < 0 or duration <= 0:
        raise ValueError("Invalid start time or duration")

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_path
    ]

    subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return output_path
