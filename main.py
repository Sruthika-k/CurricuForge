from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from services.ai_service import generate_curriculum


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="CurricuForge")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class CurriculumRequest(BaseModel):
  subject: str
  level: str
  duration: str
  goals: str = ""


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
  except Exception:
    return JSONResponse({"result": "Unable to generate curriculum at this time."})

  return JSONResponse({"result": curriculum})


@app.post("/download-pdf")
async def download_pdf(
  subject: str = Form("Curriculum"),
  curriculum: str = Form(...),
):
  buffer = BytesIO()
  c = canvas.Canvas(buffer, pagesize=A4)
  width, height = A4

  text_object = c.beginText()
  text_object.setTextOrigin(2 * cm, height - 2.5 * cm)
  text_object.setLeading(14)

  title = subject.strip() or "Curriculum"
  text_object.setFont("Helvetica-Bold", 14)
  text_object.textLine(title)
  text_object.moveCursor(0, 10)

  text_object.setFont("Helvetica", 11)
  for line in curriculum.splitlines():
    if not line.strip():
      text_object.textLine("")
      continue

    for chunk in _wrap_line(line, max_chars=90):
      if text_object.getY() <= 2 * cm:
        c.drawText(text_object)
        c.showPage()
        text_object = c.beginText()
        text_object.setTextOrigin(2 * cm, height - 2.5 * cm)
        text_object.setLeading(14)
        text_object.setFont("Helvetica", 11)
      text_object.textLine(chunk)

  c.drawText(text_object)
  c.showPage()
  c.save()

  buffer.seek(0)
  filename = f"{title.replace(' ', '_')}.pdf"
  return StreamingResponse(
    buffer,
    media_type="application/pdf",
    headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
  )


def _wrap_line(line: str, max_chars: int) -> list[str]:
  words = line.split()
  if not words:
    return [""]

  lines: list[str] = []
  current = words[0]

  for word in words[1:]:
    if len(current) + 1 + len(word) <= max_chars:
      current += " " + word
    else:
      lines.append(current)
      current = word

  lines.append(current)
  return lines
