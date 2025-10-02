from pathlib import Path
import shutil
import fitz  # PyMuPDF
from PIL import Image
import imagehash
from tqdm import tqdm


def pdf_first_page_image(pdf_path: Path) -> Image.Image:
	doc = fitz.open(pdf_path)
	page = doc[0]
	pix = page.get_pixmap(dpi=150)
	img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
	doc.close()
	return img


def file_to_phash(path: Path):
	if path.suffix.lower() == ".pdf":
		img = pdf_first_page_image(path)
	else:
		img = Image.open(path).convert("RGB")
	return imagehash.phash(img)


def cluster_by_template(samples_dir: Path, tipos_dir: Path, max_hamming: int = 5):
	tipos = []  # [(hash, dir_path)]
	tipos_count = 0

	files = [
		p
		for p in samples_dir.glob("**/*")
		if p.is_file() and p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"}
	]

	for f in tqdm(files, desc="Clustering por pHash"):
		h = file_to_phash(f)
		assigned = False
		for idx, (hash_ref, tipo_path) in enumerate(tipos, start=1):
			if h - hash_ref <= max_hamming:
				assigned = True
				dest = tipo_path / f.name
				dest.parent.mkdir(parents=True, exist_ok=True)
				shutil.copy2(f, dest)
				break
		if not assigned:
			tipos_count += 1
			tipo_path = tipos_dir / f"Tipo_{tipos_count}"
			tipo_path.mkdir(parents=True, exist_ok=True)
			shutil.copy2(f, tipo_path / f.name)
			tipos.append((h, tipo_path))
