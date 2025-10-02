from pathlib import Path
import fitz
import pytesseract
from PIL import Image


def extract_text_safely(path: Path) -> str:
	text = ""
	if path.suffix.lower() == ".pdf":
		text = extract_text_pdf(path)
	else:
		text = extract_text_image(path)
	text = " ".join(text.split())
	return text


def extract_text_pdf(pdf_path: Path) -> str:
	doc = fitz.open(pdf_path)
	text = []
	for page in doc:
		t = page.get_text("text")
		if t and len(t.strip()) > 20:
			text.append(t)
		else:
			pix = page.get_pixmap(dpi=200)
			img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
			t_ocr = pytesseract.image_to_string(img, lang="spa")
			text.append(t_ocr)
	doc.close()
	return "\n".join(text)


def extract_text_image(img_path: Path) -> str:
	img = Image.open(img_path).convert("RGB")
	return pytesseract.image_to_string(img, lang="spa")
