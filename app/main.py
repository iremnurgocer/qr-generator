from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import qrcode
import os
from datetime import datetime

app = FastAPI(title="QR Code Generator")

# Statik dosyalar (görseller)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Template motoru
templates = Jinja2Templates(directory="app/templates")

# QR kayıt klasörü
OUTPUT_DIR = "app/static/qrcodes"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse("index.html", {"request": request, "qr_path": None})


@app.post("/generate", response_class=HTMLResponse)
def generate_qr(request: Request, data: str = Form(...)):
    """Formdan gelen veriden QR üret"""
    file_name = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = os.path.join(OUTPUT_DIR, file_name)

    # QR kod oluştur
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

    # Sayfayı QR ile birlikte render et
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "qr_path": f"/static/qrcodes/{file_name}", "input_data": data}
    )
