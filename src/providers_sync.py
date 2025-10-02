from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

PROVIDERS_SHEET = "Proveedores"


def normalize_string(value: str) -> str:
	return " ".join((value or "").strip().split()).upper()


def read_providers_from_excel(excel_dir: Path) -> list[dict]:
	# Find first .xlsx under excel_dir; prefer exact 'Proveedores.xlsx' if present
	candidate = excel_dir / "Proveedores.xlsx"
	if not candidate.exists():
		xlsx_files = list(excel_dir.glob("*.xlsx"))
		if not xlsx_files:
			raise FileNotFoundError(f"No Excel files found in {excel_dir}")
		candidate = xlsx_files[0]

	df = pd.read_excel(candidate, sheet_name=PROVIDERS_SHEET)
	required_cols = {"Proveedor", "CIF", "EstacionDestino"}
	missing = required_cols - set(df.columns)
	if missing:
		raise ValueError(f"Missing required columns in Excel: {missing}")

	records = []
	for _, row in df.iterrows():
		records.append({
			"Proveedor": str(row["Proveedor"]).strip(),
			"CIF": ("" if pd.isna(row["CIF"]) else str(row["CIF"]).strip()),
			"EstacionDestino": str(row["EstacionDestino"]).strip(),
			"Proveedor_norm": normalize_string(str(row["Proveedor"]))
		})
	return records


def write_providers_json(records: list[dict], json_path: Path) -> None:
	json_path.parent.mkdir(parents=True, exist_ok=True)
	with open(json_path, "w", encoding="utf-8") as f:
		json.dump(records, f, ensure_ascii=False, indent=2)


def sync_providers(excel_dir: Path, json_path: Path) -> Path:
	records = read_providers_from_excel(excel_dir)
	write_providers_json(records, json_path)
	return json_path


if __name__ == "__main__":
	# manual run: python -m src.providers_sync
	excel_dir = Path("data/Proveedores")
	json_path = Path("data/providers.json")
	out = sync_providers(excel_dir, json_path)
	print(f"Providers JSON written to: {out}")
