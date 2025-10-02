from pathlib import Path
import json
import re
from text_extract import extract_text_safely


def normalize(s: str) -> str:
	return re.sub(r"\s+", " ", s.strip().upper())


def link_types_to_providers(tipos_dir: Path, providers_json: Path):
	with open(providers_json, "r", encoding="utf-8") as f:
		providers = json.load(f)

	assignments = []  # [(tipo, proveedor)]

	for tipo_path in sorted([p for p in tipos_dir.iterdir() if p.is_dir()], key=lambda x: x.name):
		hits = {}
		for f in tipo_path.glob("*"):
			txt = normalize(extract_text_safely(f))
			for row in providers:
				prov_norm = row.get("Proveedor_norm", "")
				cif_norm = normalize(str(row.get("CIF", "")))
				score = 0
				if prov_norm and prov_norm in txt:
					score += 2
				if cif_norm and cif_norm in txt:
					score += 3
				if score:
					hits[row["Proveedor"]] = hits.get(row["Proveedor"], 0) + score
		proveedor = max(hits, key=hits.get) if hits else None
		assignments.append((tipo_path.name, proveedor))
		print(f"{tipo_path.name} -> {proveedor or 'SIN VINCULAR'}")

	out_csv = tipos_dir.parent / "tipo_proveedor_map.csv"
	import pandas as pd
	pd.DataFrame(assignments, columns=["Tipo", "Proveedor"]).to_csv(out_csv, index=False)
	print(f"Guardado: {out_csv}")
