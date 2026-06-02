#!/usr/bin/env python3
"""Extract and format image metadata for format-post skill."""

import subprocess
import json
import sys
import re
from pathlib import Path

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def natural_sort_key(path):
    """Sort by leading integer in filename, then alphabetically."""
    m = re.match(r"^(\d+)", path.name)
    return (int(m.group(1)) if m else float("inf"), path.name)


def format_shutter(seconds):
    if seconds is None:
        return ""
    if seconds >= 1:
        return f"{seconds:.1f}"
    denom = round(1 / seconds)
    return f"1/{denom}"


def format_aperture(fnum):
    if fnum is None:
        return ""
    if fnum == int(fnum):
        return str(int(fnum))
    # Keep one decimal place, strip trailing zero
    return f"{fnum:.1f}".rstrip("0")


def format_date(raw):
    if not raw:
        return ""
    try:
        date_part = raw.split(" ")[0]
        y, m, d = date_part.split(":")
        return f"{int(d)} {MONTHS[int(m) - 1]} {int(y)}"
    except Exception:
        return raw


def normalize_camera(model):
    """LEICA M11-P -> Leica M11-P"""
    if not model:
        return ""
    if model.upper().startswith("LEICA "):
        return "Leica " + model[6:]
    return model


def normalize_leica_lens(raw):
    """
    Convert Leica EXIF lens model strings to formatted names.

    "Apo-Summicron-M 1:2/50 ASPH."  -> "Leica APO-Summicron-M 50 ƒ/2 ASPH."
    "Summicron-M 1:2/35 ASPH."      -> "Leica Summicron-M 35 ƒ/2 ASPH."
    "Summilux-M 1:1.4/50 ASPH."     -> "Leica Summilux-M 50 ƒ/1.4 ASPH."
    "Apo-Summicron-M 1:2/35 ASPH."  -> "Leica APO-Summicron-M 35 ƒ/2 ASPH."
    """
    if not raw:
        return ""
    m = re.match(
        r"^(Apo-|Super-)?([\w]+-M)\s+1:([\d.]+)/([\d]+)\s*(.*?)\.?\s*$",
        raw,
        re.IGNORECASE,
    )
    if not m:
        return raw

    prefix, name, apt, focal, suffix = m.groups()

    if prefix and prefix.lower() == "apo-":
        full_name = f"APO-{name}"
    elif prefix and prefix.lower() == "super-":
        full_name = f"Super-{name}"
    else:
        full_name = name

    apt_str = apt.rstrip("0").rstrip(".") if "." in apt else apt
    suffix_str = (" " + suffix.strip().rstrip(".")) if suffix.strip() else ""

    return f"Leica {full_name} {focal} ƒ/{apt_str}{suffix_str}."


def extract(folder_path):
    folder = Path(folder_path).expanduser().resolve()

    result = subprocess.run(
        [
            "exiftool", "-json", "-n",
            "-ext", "jpg", "-ext", "jpeg",
            "-ImageWidth", "-ImageHeight",
            "-Model", "-LensModel", "-Lens",
            "-ExposureTime", "-FNumber", "-FocalLength", "-ISO",
            "-DateTimeOriginal",
            "-GPSLatitude", "-GPSLatitudeRef",
            "-GPSLongitude", "-GPSLongitudeRef",
            str(folder),
        ],
        capture_output=True,
        text=True,
    )

    try:
        raw_list = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        raw_list = []

    raw_list.sort(key=lambda x: natural_sort_key(Path(x.get("SourceFile", ""))))

    images = []
    for item in raw_list:
        width = item.get("ImageWidth", 0)
        height = item.get("ImageHeight", 0)
        lens_raw = item.get("LensModel") or item.get("Lens") or ""

        gps = None
        lat = item.get("GPSLatitude")
        lon = item.get("GPSLongitude")
        if lat is not None and lon is not None:
            lat_ref = item.get("GPSLatitudeRef", "N")
            lon_ref = item.get("GPSLongitudeRef", "E")
            # GPSLatitudeRef is "N"/"S" as a string even with -n
            if isinstance(lat_ref, str):
                lat_sign = -1 if lat_ref.upper().startswith("S") else 1
                lon_sign = -1 if lon_ref.upper().startswith("W") else 1
            else:
                lat_sign = 1 if lat_ref >= 0 else -1
                lon_sign = 1 if lon_ref >= 0 else -1
            gps = {
                "lat": round(lat * lat_sign, 6),
                "lon": round(lon * lon_sign, 6),
            }

        images.append(
            {
                "file": Path(item["SourceFile"]).name,
                "path": item["SourceFile"],
                "orientation": "landscape" if width >= height else "portrait",
                "camera": normalize_camera(item.get("Model", "")),
                "lens_raw": lens_raw,
                "lens": normalize_leica_lens(lens_raw),
                "focal_length": f"{int(round(item['FocalLength']))} mm" if item.get("FocalLength") else "",
                "shutter": format_shutter(item.get("ExposureTime")),
                "aperture": format_aperture(item.get("FNumber")),
                "iso": item.get("ISO"),
                "date": format_date(item.get("DateTimeOriginal", "")),
                "gps": gps,
            }
        )

    return images


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: extract_images.py <image-folder>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(extract(sys.argv[1]), indent=2))
