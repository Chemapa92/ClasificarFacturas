from pathlib import Path
import pandas as pd
import re
from text_extract import extract_text_safely


def normalize(s: str) -> str:
	return re.sub(r"\s+", " ", s.strip().upper())


def link_types_to_providers(tipos_dir: Path, proveedores_xlsx: Path):
	df = pd.read_excel(proveedores_xlsx, sheet_name="Proveedores")
	df["Proveedor_norm"] = df["Proveedor"].apply(normalize)
	df["CIF_norm"] = df["CIF"].astype(str).apply(lambda x: normalize(x))

	assignments = []  # [(tipo, proveedor)]

	for tipo_path in sorted([p for p in tipos_dir.iterdir() if p.is_dir()], key=lambda x: x.name):
		hits = {}
		for f in tipo_path.glob("*"):
			txt = normalize(extract_text_safely(f))
			for _, row in df.iterrows():
				score = 0
				if row["Proveedor_norm"] and row["Proveedor_norm"] in txt:
					score += 2
				if row["CIF_norm"] and row["CIF_norm"] in txt:
					score += 3
				if score:
					hits[row["Proveedor"]] = hits.get(row["Proveedor"], 0) + score
		proveedor = max(hits, key=hits.get) if hits else None
		assignments.append((tipo_path.name, proveedor))
		print(f"{tipo_path.name} -> {proveedor or 'SIN VINCULAR'}")

	out_csv = tipos_dir.parent / "tipo_proveedor_map.csv"
	pd.DataFrame(assignments, columns=["Tipo", "Proveedor"]).to_csv(out_csv, index=False)
	print(f"Guardado: {out_csv}")
