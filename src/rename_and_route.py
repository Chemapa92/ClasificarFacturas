from pathlib import Path
import shutil
import pandas as pd


def rename_and_route_all(renombradas_dir: Path, proveedores_xlsx: Path, estaciones_root: Path, pendientes_dir: Path):
	df = pd.read_excel(proveedores_xlsx, sheet_name="Proveedores")
	providers = {row["Proveedor"].upper(): row["EstacionDestino"] for _, row in df.iterrows()}

	for f in renombradas_dir.glob("*"):
		parts = f.stem.split("_")
		if len(parts) < 3:
			shutil.copy2(f, pendientes_dir / f.name)
			continue
		proveedor = parts[1].replace("-", " ").upper()
		destino = providers.get(proveedor)
		if not destino:
			destino = fuzzy_provider(providers, proveedor)
		if destino:
			target_dir = estaciones_root / destino
			target_dir.mkdir(parents=True, exist_ok=True)
			shutil.copy2(f, target_dir / f.name)
		else:
			shutil.copy2(f, pendientes_dir / f.name)


def fuzzy_provider(providers: dict, prov: str):
	for k, v in providers.items():
		if k in prov or prov in k:
			return v
	return None
