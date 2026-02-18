import logging
import os
import re
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from services.ai_service import generate_curriculum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="CurricuForge", debug=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class CurriculumRequest(BaseModel):
    subject: str
    level: str
    duration: str
    goals: str = ""


@app.on_event("startup")
async def startup_event():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        raise RuntimeError("GEMINI_API_KEY must be set in environment variables or .env file")
    logger.info("CurricuForge started successfully")


@app.get("/")
async def get_landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/generate")
async def get_generate(request: Request):
    return templates.TemplateResponse("generate.html", {"request": request})


@app.post("/generate")
async def post_generate(data: CurriculumRequest):
    try:
        curriculum = await generate_curriculum(
            subject=data.subject,
            level=data.level,
            duration=data.duration,
            goals=data.goals,
        )
        return JSONResponse({"result": curriculum})
    except Exception as e:
        logger.error(f"Error generating curriculum: {str(e)}")
        return JSONResponse(
            {"result": "Unable to generate curriculum at this time. Please try again later."},
            status_code=500,
        )


@app.post("/download-pdf")
async def download_pdf(
    subject: str = Form("Curriculum"),
    curriculum: str = Form(...),
):
    try:
        # Strip any residual HTML tags before PDF generation
        clean_text = re.sub(r"<[^>]+>", "", curriculum)
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text).strip()

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        left = 2.2 * cm
        right_margin = width - 2.2 * cm
        max_width = right_margin - left
        y = height - 2.5 * cm

        title = subject.strip() or "Curriculum"

        # Draw title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(left, y, title)
        y -= 0.8 * cm
        c.setStrokeColorRGB(0.23, 0.47, 0.93)
        c.setLineWidth(1.5)
        c.line(left, y, right_margin, y)
        y -= 0.6 * cm

        def new_page():
            nonlocal y
            c.showPage()
            y = height - 2.5 * cm

        def draw_line(text: str, font: str, size: int, leading: float = 0.55):
            nonlocal y
            if y < 2.5 * cm:
                new_page()
                if font != "Helvetica":
                    c.setFont(font, size)
            c.setFont(font, size)
            c.drawString(left, y, text)
            y -= size * leading

        for line in clean_text.splitlines():
            stripped = line.strip()

            if not stripped:
                y -= 0.25 * cm
                continue

            # Detect UPPERCASE section headings
            if stripped.isupper() and len(stripped) > 3:
                y -= 0.2 * cm
                if y < 3 * cm:
                    new_page()
                c.setFont("Helvetica-Bold", 13)
                c.setFillColorRGB(0.12, 0.23, 0.38)
                c.drawString(left, y, stripped)
                y -= 0.35 * cm
                c.setStrokeColorRGB(0.23, 0.47, 0.93)
                c.setLineWidth(0.5)
                c.line(left, y, right_margin, y)
                y -= 0.45 * cm
                c.setFillColorRGB(0, 0, 0)
                continue

            # Detect week headings like "Week 1:" or "WEEK 1"
            if re.match(r"^(Week|WEEK)\s+\d+", stripped):
                y -= 0.1 * cm
                if y < 3 * cm:
                    new_page()
                c.setFont("Helvetica-Bold", 11)
                c.setFillColorRGB(0.15, 0.35, 0.65)
                c.drawString(left, y, stripped)
                y -= 0.45 * cm
                c.setFillColorRGB(0, 0, 0)
                continue

            # Bullet points
            if stripped.startswith("- ") or stripped.startswith("• "):
                bullet_text = stripped[2:].strip()
                for chunk in _wrap(bullet_text, max_width - 0.5 * cm, "Helvetica", 10):
                    if y < 2.5 * cm:
                        new_page()
                    c.setFont("Helvetica", 10)
                    c.drawString(left + 0.4 * cm, y, f"• {chunk}" if chunk == bullet_text.split()[0:len(chunk.split())] else f"  {chunk}")
                    y -= 0.42 * cm
                continue

            # Regular body text — wrap long lines
            for chunk in _wrap(stripped, max_width, "Helvetica", 10):
                if y < 2.5 * cm:
                    new_page()
                c.setFont("Helvetica", 10)
                c.drawString(left, y, chunk)
                y -= 0.42 * cm

        c.showPage()
        c.save()

        buffer.seek(0)
        filename = f"{title.replace(' ', '_')}.pdf"
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return JSONResponse({"error": "Unable to generate PDF at this time."}, status_code=500)


def _wrap(text: str, max_width: float, font_name: str, font_size: int) -> list[str]:
    """Wrap text to fit within max_width points using character estimation."""
    avg_char_width = font_size * 0.55  # rough estimate for Helvetica
    max_chars = int(max_width / avg_char_width)
    words = text.split()
    if not words:
        return [""]
    lines, current = [], words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_chars:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
