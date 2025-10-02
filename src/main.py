from pathlib import Path
import argparse

from cluster import cluster_by_template
from link_providers import link_types_to_providers
from fields_extract import extract_fields_for_types
from rename_and_route import rename_and_route_all

DATA_DIR = Path("data")
SAMPLES = DATA_DIR / "samples"
OUT = DATA_DIR / "out"
TIPOS_DIR = OUT / "tipos"
PENDIENTES = OUT / "Pendientes_de_identificar"
PROVEEDORES_XLSX = DATA_DIR / "proveedores.xlsx"
PATTERNS_YAML = Path("patterns") / "patterns.yaml"


def ensure_dirs():
	for p in [OUT, TIPOS_DIR, PENDIENTES, OUT / "renombradas", OUT / "estaciones"]:
		p.mkdir(parents=True, exist_ok=True)


def cmd_cluster(args):
	ensure_dirs()
	cluster_by_template(SAMPLES, TIPOS_DIR, max_hamming=args.max_hamming)


def cmd_link(args):
	link_types_to_providers(TIPOS_DIR, PROVEEDORES_XLSX)


def cmd_extract(args):
	extract_fields_for_types(TIPOS_DIR, PATTERNS_YAML, PENDIENTES, OUT / "renombradas")


def cmd_route(args):
	rename_and_route_all(OUT / "renombradas", PROVEEDORES_XLSX, OUT / "estaciones", PENDIENTES)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Clasificador de facturas")
	sub = parser.add_subparsers(dest="cmd", required=True)

	p1 = sub.add_parser("cluster", help="Agrupa por tipo usando pHash")
	p1.add_argument("--max-hamming", type=int, default=5)
	p1.set_defaults(func=cmd_cluster)

	p2 = sub.add_parser("link", help="Vincula tipo con proveedor usando Excel + texto")
	p2.set_defaults(func=cmd_link)

	p3 = sub.add_parser("extract", help="Extrae campos y renombra preliminarmente")
	p3.set_defaults(func=cmd_extract)

	p4 = sub.add_parser("route", help="Envía a estación o pendientes")
	p4.set_defaults(func=cmd_route)

	args = parser.parse_args()
	args.func(args)
