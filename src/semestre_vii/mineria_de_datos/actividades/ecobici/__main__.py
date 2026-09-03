import argparse

from .ingesta import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingesta histórica de datos abiertos de ECOBICI.",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Carga un año específico, por ejemplo 2025.",
    )
    parser.add_argument("--from-year", type=int)
    parser.add_argument("--to-year", type=int)
    parser.add_argument(
        "--all",
        dest="all_years",
        action="store_true",
        help="Carga todos los años históricos disponibles.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recarga meses que ya fueron ingeridos.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run(
        year=args.year,
        from_year=args.from_year,
        to_year=args.to_year,
        all_years=args.all_years,
        force=args.force,
    )


if __name__ == "__main__":
    main()
