from pathlib import Path
import argparse

from cluster import cluster_by_template
from link_providers import link_types_to_providers
from fields_extract import extract_fields_for_types
from rename_and_route import rename_and_route_all
from providers_sync import sync_providers

DATA_DIR = Path("data")
SAMPLES = DATA_DIR / "samples"
OUT = DATA_DIR / "out"
TIPOS_DIR = OUT / "tipos"
PENDIENTES = OUT / "Pendientes_de_identificar"
PROVEEDORES_EXCEL_DIR = DATA_DIR / "Proveedores"
PROVIDERS_JSON = DATA_DIR / "providers.json"
PATTERNS_YAML = Path("patterns") / "patterns.yaml"


def ensure_dirs():
	for p in [OUT, TIPOS_DIR, PENDIENTES, OUT / "renombradas", OUT / "estaciones"]:
		p.mkdir(parents=True, exist_ok=True)


def cmd_cluster(args):
	ensure_dirs()
	cluster_by_template(SAMPLES, TIPOS_DIR, max_hamming=args.max_hamming)


def cmd_providers(args):
	path = sync_providers(PROVEEDORES_EXCEL_DIR, PROVIDERS_JSON)
	print(f"Sincronizado: {path}")


def cmd_link(args):
	link_types_to_providers(TIPOS_DIR, PROVIDERS_JSON)


def cmd_extract(args):
	extract_fields_for_types(TIPOS_DIR, PATTERNS_YAML, PENDIENTES, OUT / "renombradas")


def cmd_route(args):
	rename_and_route_all(OUT / "renombradas", PROVIDERS_JSON, OUT / "estaciones", PENDIENTES)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Clasificador de facturas")
	sub = parser.add_subparsers(dest="cmd", required=True)

	p0 = sub.add_parser("providers", help="Sincroniza Excel->JSON de proveedores")
	p0.set_defaults(func=cmd_providers)

	p1 = sub.add_parser("cluster", help="Agrupa por tipo usando pHash")
	p1.add_argument("--max-hamming", type=int, default=5)
	p1.set_defaults(func=cmd_cluster)

	p2 = sub.add_parser("link", help="Vincula tipo con proveedor (usa providers.json)")
	p2.set_defaults(func=cmd_link)

	p3 = sub.add_parser("extract", help="Extrae campos y renombra preliminarmente")
	p3.set_defaults(func=cmd_extract)

	p4 = sub.add_parser("route", help="Envía a estación o pendientes")
	p4.set_defaults(func=cmd_route)

	args = parser.parse_args()
	args.func(args)
