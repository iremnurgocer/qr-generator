# QR Code Generator

The **QR Code Generator** is a simple and modern web application built with **FastAPI**.  
It allows users to easily generate QR codes from any text or URL directly in the browser.  
Each QR code is created instantly and displayed on the page with the option to save it locally.

---

## Features

- Generate QR codes instantly from any text or URL
- Customize foreground/background colors, box size, border and error correction level
- Upload a logo to embed inside PNG QR codes or export to SVG for vector workflows
- Download generated QR codes directly from the browser and revisit the last 50 creations
- Automatic cleanup keeps the latest 100 QR codes for convenience
- Dedicated history view for reusing your previous designs

---

## Installation & Setup

### Windows (recommended)

1. Double-click `kurulum.bat` to create the virtual environment and install dependencies.
2. After the setup completes, run `baslat.bat` to start the development server.
3. Open your browser and navigate to: http://127.0.0.1:8000

### Manual Setup

```bash
git clone https://github.com/iremnurgocer/qr-generator.git
cd qr-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000 and start generating QR codes.

## Usage Tips

- Use the customization panel to adjust colors, size and correction level to fit your brand.
- PNG exports support logo overlays (PNG/JPG up to 2 MB). SVG exports give scalable output without a logo.
- Click **Geçmişi Gör** to browse the most recent 50 QR codes, download them again or open in a new tab.

---

## Contact

LinkedIn: https://linkedin.com/in/iremnurgocer  
GitHub: https://github.com/iremnurgocer  
Email: iremnurgocer99@gmail.com
