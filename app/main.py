import os
from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.utils import (
    QRCodeGenerationError,
    append_history,
    cleanup_old_qr_codes,
    generate_qr_code,
    load_history,
    summarize_text,
)

app = FastAPI(title="QR Code Generator")

# Statik dosyalar (görseller)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Template motoru
templates = Jinja2Templates(directory="app/templates")

# QR kayıt klasörü
OUTPUT_DIR = "app/static/qrcodes"
os.makedirs(OUTPUT_DIR, exist_ok=True)
MAX_QR_HISTORY = 100
MAX_LOGO_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_LOGO_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "qr_path": None,
            "message": None,
            "message_type": None,
            "input_data": "",
            "fill_color": "#000000",
            "back_color": "#ffffff",
            "box_size": 10,
            "border": 4,
            "error_correction": "M",
            "output_format": "png",
            "with_logo": False,
            "qr_download_url": None,
        },
    )


@app.post("/generate", response_class=HTMLResponse)
def generate_qr(
    request: Request,
    data: str = Form(...),
    fill_color: str = Form("#000000"),
    back_color: str = Form("#ffffff"),
    box_size: int = Form(10),
    border: int = Form(4),
    error_correction: str = Form("M"),
    output_format: str = Form("png"),
    logo: UploadFile | None = File(None),
):
    """Formdan gelen veriden QR üret"""
    context = {
        "request": request,
        "input_data": data,
        "fill_color": fill_color,
        "back_color": back_color,
        "box_size": box_size,
        "border": border,
        "error_correction": error_correction,
        "output_format": output_format,
        "with_logo": bool(logo and logo.filename),
        "qr_path": None,
        "qr_download_url": None,
        "message": None,
        "message_type": None,
    }

    logo_bytes = None
    if logo and logo.filename:
        if logo.content_type not in ALLOWED_LOGO_CONTENT_TYPES:
            context.update(
                {"message": "Logo yalnızca PNG veya JPEG formatında olmalıdır.", "message_type": "error"}
            )
            return templates.TemplateResponse("index.html", context, status_code=400)

        logo.file.seek(0, os.SEEK_END)
        size = logo.file.tell()
        logo.file.seek(0)
        if size > MAX_LOGO_SIZE_BYTES:
            context.update({"message": "Logo boyutu 2 MB'ı aşmamalıdır.", "message_type": "error"})
            return templates.TemplateResponse("index.html", context, status_code=400)

        if output_format.lower() != "png":
            context.update(
                {
                    "message": "Logo yalnızca PNG çıktılar için eklenebilir.",
                    "message_type": "error",
                }
            )
            return templates.TemplateResponse("index.html", context, status_code=400)

        logo_bytes = logo.file.read()

    try:
        file_name, _ = generate_qr_code(
            data,
            OUTPUT_DIR,
            box_size=box_size,
            border=border,
            fill_color=fill_color,
            back_color=back_color,
            error_correction=error_correction,
            output_format=output_format,
            logo_bytes=logo_bytes,
        )
    except QRCodeGenerationError as exc:
        context.update({"message": str(exc), "message_type": "error"})
        return templates.TemplateResponse("index.html", context, status_code=400)

    cleanup_old_qr_codes(OUTPUT_DIR, keep=MAX_QR_HISTORY)

    context.update(
        {
            "qr_path": f"/static/qrcodes/{file_name}",
            "qr_download_url": f"/download/{file_name}",
            "message": "QR kodu başarıyla oluşturuldu.",
            "message_type": "success",
        }
    )

    append_history(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "file_name": file_name,
            "relative_path": f"/static/qrcodes/{file_name}",
            "preview_text": summarize_text(data),
            "fill_color": fill_color,
            "back_color": back_color,
            "box_size": box_size,
            "border": border,
            "error_correction": error_correction.upper(),
            "output_format": output_format.lower(),
            "with_logo": bool(logo_bytes),
        }
    )

    return templates.TemplateResponse("index.html", context)


@app.get("/download/{file_name}")
def download_qr(file_name: str):
    file_path = os.path.join(OUTPUT_DIR, file_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="QR kodu bulunamadı.")

    media_type = "image/svg+xml" if file_name.lower().endswith(".svg") else "image/png"
    return FileResponse(file_path, media_type=media_type, filename=file_name)


@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    items = load_history(limit=50)
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "history": items},
    )
