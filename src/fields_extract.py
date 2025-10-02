from pathlib import Path
import re
import yaml
from datetime import datetime
from dateutil import parser as dateparser
from text_extract import extract_text_safely


def parse_date_with_format(s: str, in_fmt: str | None):
	if in_fmt:
		return datetime.strptime(s, in_fmt)
	return dateparser.parse(s, dayfirst=True, fuzzy=True)


def extract_fields_for_types(tipos_dir: Path, patterns_yaml: Path, pendientes_dir: Path, renombradas_dir: Path):
	with open(patterns_yaml, "r", encoding="utf-8") as f:
		patterns = yaml.safe_load(f) or {}

	for tipo_path in sorted([p for p in tipos_dir.iterdir() if p.is_dir()], key=lambda x: x.name):
		pat = patterns.get(tipo_path.name)
		for f in tipo_path.glob("*"):
			txt = extract_text_safely(f)

			if not pat:
				target = pendientes_dir / f.name
				target.parent.mkdir(parents=True, exist_ok=True)
				target.write_bytes(f.read_bytes())
				continue

			proveedor = extract_first_group(txt, pat.get("proveedor_regex"))
			fecha_raw = extract_first_group(txt, pat.get("fecha_regex"))
			numero = extract_first_group(txt, pat.get("numero_regex"))

			if not (proveedor and fecha_raw and numero):
				target = pendientes_dir / f.name
				target.parent.mkdir(parents=True, exist_ok=True)
				target.write_bytes(f.read_bytes())
				continue

			dt = parse_date_with_format(fecha_raw, pat.get("fecha_out_format"))
			yyyymmdd = dt.strftime("%Y%m%d")
			proveedor_clean = clean_for_filename(proveedor)
			numero_clean = clean_for_filename(numero)

			new_name = f"{yyyymmdd}_{proveedor_clean}_{numero_clean}{f.suffix}"
			(renombradas_dir / new_name).parent.mkdir(parents=True, exist_ok=True)
			(renombradas_dir / new_name).write_bytes(f.read_bytes())


def extract_first_group(text: str, pattern: str | None):
	if not pattern:
		return None
	m = re.search(pattern, text, re.IGNORECASE)
	if m:
		return m.group(1) if m.groups() else m.group(0)
	return None


def clean_for_filename(s: str) -> str:
	s = re.sub(r"[\\/:*?\"<>|]", "-", s)
	s = re.sub(r"\s+", "_", s.strip())
	return s[:120]
