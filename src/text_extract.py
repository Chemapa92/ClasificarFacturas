from pathlib import Path
from pypdf import PdfReader
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


def extract_text_safely(path: Path) -> str:
	text = ""
	if path.suffix.lower() == ".pdf":
		text = extract_text_pdf(path)
	else:
		text = extract_text_image(path)
	text = " ".join(text.split())
	return text


def extract_text_pdf(pdf_path: Path) -> str:
	# Try native text via pypdf
	try:
		reader = PdfReader(str(pdf_path))
		buf = []
		for page in reader.pages:
			content = page.extract_text() or ""
			buf.append(content)
		text = "\n".join(buf).strip()
		if len(text) >= 20:
			return text
	except Exception:
		pass
	# OCR fallback: rasterize pages with pdf2image (Poppler required on Windows)
	images = convert_from_path(str(pdf_path), dpi=200)
	ocr_text = []
	for img in images:
		ocr_text.append(pytesseract.image_to_string(img, lang="spa"))
	return "\n".join(ocr_text)


def extract_text_image(img_path: Path) -> str:
	img = Image.open(img_path).convert("RGB")
	return pytesseract.image_to_string(img, lang="spa")
