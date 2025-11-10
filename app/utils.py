import json
import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List, Tuple

import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q
from qrcode.image.svg import SvgImage


class QRCodeGenerationError(ValueError):
    """Raised when QR code generation fails due to invalid input or configuration."""


ERROR_CORRECTION_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

HISTORY_DIR = Path("app/data")
HISTORY_FILE = HISTORY_DIR / "history.json"


def generate_qr_code(
    data: str,
    output_dir: str,
    *,
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
    error_correction: str = "M",
    output_format: str = "png",
    logo_bytes: bytes | None = None,
) -> Tuple[str, str]:
    """
    Generate a QR code image from the provided data.

    Returns:
        A tuple of (file_name, absolute_file_path).

    Raises:
        QRCodeGenerationError: If input validation fails.
    """
    sanitized = (data or "").strip()
    if not sanitized:
        raise QRCodeGenerationError("Boş veri ile QR kodu oluşturulamaz.")

    box_size = _coerce_int(box_size, default=10, minimum=2, maximum=20, field_name="box_size")
    border = _coerce_int(border, default=4, minimum=1, maximum=10, field_name="border")

    if str(fill_color).strip().lower() == str(back_color).strip().lower():
        raise QRCodeGenerationError("Ön plan ve arka plan renkleri farklı olmalıdır.")

    error_correction = ERROR_CORRECTION_MAP.get(str(error_correction).upper(), ERROR_CORRECT_M)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    extension = "svg" if str(output_format).lower() == "svg" else "png"
    file_name = f"qr_{timestamp}.{extension}"
    file_path = os.path.join(output_dir, file_name)

    qr = qrcode.QRCode(box_size=box_size, border=border, error_correction=error_correction)
    qr.add_data(sanitized)
    qr.make(fit=True)

    if extension == "svg":
        img = qr.make_image(image_factory=SvgImage, fill_color=fill_color, back_color=back_color)
        with open(file_path, "w", encoding="utf-8") as fp:
            img.save(fp)
    else:
        qr_image = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
        if logo_bytes:
            qr_image = _embed_logo(qr_image, logo_bytes)
        qr_image.save(file_path)

    return file_name, file_path


def cleanup_old_qr_codes(directory: str, *, keep: int = 100) -> None:
    """
    Keep only the most recent `keep` QR images and delete older ones.
    """
    path = Path(directory)
    if not path.exists():
        return

    files = sorted(
        (p for p in path.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".svg"}),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old_file in files[keep:]:
        try:
            old_file.unlink()
        except OSError:
            # Ignore deletion errors to avoid crashing the request pipeline.
            continue


def append_history(entry: dict, *, max_items: int = 200) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.insert(0, entry)
    history = history[:max_items]
    with open(HISTORY_FILE, "w", encoding="utf-8") as fp:
        json.dump(history, fp, ensure_ascii=False, indent=2)


def load_history(limit: int | None = None) -> List[dict]:
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (json.JSONDecodeError, OSError):
        return []

    if limit is not None and limit > 0:
        return data[:limit]
    return data


def summarize_text(value: str, *, limit: int = 120) -> str:
    sanitized = (value or "").strip()
    if len(sanitized) <= limit:
        return sanitized
    return f"{sanitized[:limit]}..."


def _embed_logo(image: Image.Image, logo_bytes: bytes) -> Image.Image:
    try:
        logo = Image.open(BytesIO(logo_bytes)).convert("RGBA")
    except Exception as exc:
        raise QRCodeGenerationError("Logo resmi işlenemedi.") from exc

    max_logo_width = image.width // 3
    max_logo_height = image.height // 3
    resample_attr = getattr(Image, "Resampling", Image)
    resample_method = getattr(resample_attr, "LANCZOS", Image.BICUBIC)
    logo.thumbnail((max_logo_width, max_logo_height), resample_method)

    pos = ((image.width - logo.width) // 2, (image.height - logo.height) // 2)
    image.paste(logo, pos, mask=logo)
    return image


def _coerce_int(value, *, default: int, minimum: int, maximum: int, field_name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default

    return max(minimum, min(maximum, number))
