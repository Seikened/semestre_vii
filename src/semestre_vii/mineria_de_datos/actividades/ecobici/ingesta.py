import argparse
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import duckdb
import httpx
import polars as pl

# ============================================================
# Configuration
# ============================================================

OPEN_DATA_URL = "https://ecobici.mx/datos-abiertos/"

DATA_DIR = Path("data/ecobici")
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "ecobici.duckdb"

TRIPS_TABLE = "trips_raw"
FILES_TABLE = "ingestion_files"

REQUEST_TIMEOUT = 120.0

CSV_LINK_PATTERN = re.compile(
    r'<a[^>]+href=["\']([^"\']+\.csv)["\'][^>]*>'
    r'\s*(\d{4}-\d{2})\s*</a>',
    re.IGNORECASE,
)


# ============================================================
# Discovery
# ============================================================

def discover_files(
    client: httpx.Client,
) -> dict[int, list[tuple[str, str]]]:
    """
    Reads ECOBICI's official Open Data page and discovers every
    published historical CSV.

    Returns:

    {
        2025: [
            ("2025-01", "https://.../2025-01.csv"),
            ("2025-02", "https://.../2025-02.csv"),
        ]
    }
    """
    response = client.get(OPEN_DATA_URL)
    response.raise_for_status()

    files: dict[int, list[tuple[str, str]]] = {}

    for href, period in CSV_LINK_PATTERN.findall(response.text):
        year = int(period[:4])
        url = urljoin(str(response.url), href)

        files.setdefault(year, []).append(
            (period, url)
        )

    for year in files:
        files[year].sort()

    if not files:
        raise RuntimeError(
            "No historical ECOBICI CSV files were discovered."
        )

    return files


# ============================================================
# Download
# ============================================================

def download_csv(
    client: httpx.Client,
    url: str,
    destination: Path,
) -> None:
    """
    Streams the CSV to disk without loading the whole file
    into memory.
    """
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = destination.with_suffix(".csv.part")

    with client.stream("GET", url) as response:
        response.raise_for_status()

        with temp_path.open("wb") as file:
            for chunk in response.iter_bytes(
                chunk_size=1024 * 1024
            ):
                file.write(chunk)

    temp_path.replace(destination)


# ============================================================
# Polars
# ============================================================

def normalize_column(name: str) -> str:
    """
    Example:

    Ciclo_Estación_Retiro
        ↓
    ciclo_estacion_retiro
    """
    value = unicodedata.normalize(
        "NFKD",
        name,
    )

    value = (
        value
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
        .lower()
    )

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    return value.strip("_")


def normalize_columns(
    columns: list[str],
) -> list[str]:
    """
    Normalizes column names while preventing empty identifiers
    and duplicates.

    Some historical ECOBICI CSV files contain unnamed or malformed
    headers. DuckDB cannot create a column named "", so those
    columns receive a deterministic positional name instead.
    """
    result: list[str] = []
    used: dict[str, int] = {}

    for index, column in enumerate(columns, start=1):
        base = normalize_column(str(column))

        # Historical CSVs can contain blank/malformed headers.
        # Preserve the column instead of silently dropping it.
        if not base:
            base = f"unnamed_column_{index}"

        # Keep generated SQL identifiers simple and predictable.
        if base[0].isdigit():
            base = f"column_{base}"

        count = used.get(base, 0) + 1
        used[base] = count

        if count == 1:
            result.append(base)
        else:
            result.append(f"{base}_{count}")

    return result


def detect_separator(path: Path) -> str:
    """
    Some historical datasets can change formatting.
    Detect comma / semicolon / tab from the header.
    """
    sample = (
        path
        .read_bytes()[:64_000]
        .decode("utf-8", errors="replace")
    )

    first_line = (
        sample.splitlines()[0]
        if sample
        else ""
    )

    candidates = {
        ",": first_line.count(","),
        ";": first_line.count(";"),
        "\t": first_line.count("\t"),
    }

    separator, score = max(
        candidates.items(),
        key=lambda item: item[1],
    )

    return separator if score else ","


def read_month(
    path: Path,
    period: str,
    source_url: str,
) -> pl.DataFrame:
    """
    Raw CSV -> normalized Polars DataFrame.

    Source fields are initially read as strings intentionally.
    Historical schemas can change between years.
    """
    separator = detect_separator(path)

    dataframe = pl.read_csv(
        path,
        separator=separator,

        # Avoid type conflicts between years.
        infer_schema=False,

        ignore_errors=True,
        truncate_ragged_lines=True,

        encoding="utf8-lossy",

        null_values=[
            "",
            "NA",
            "N/A",
            "NULL",
            "null",
        ],
    )

    dataframe.columns = normalize_columns(
        dataframe.columns
    )

    year, month = map(
        int,
        period.split("-"),
    )

    return dataframe.with_columns(
        pl.lit(year)
        .cast(pl.Int16)
        .alias("_source_year"),

        pl.lit(month)
        .cast(pl.Int8)
        .alias("_source_month"),

        pl.lit(period)
        .alias("_source_period"),

        pl.lit(source_url)
        .alias("_source_url"),

        pl.lit(
            datetime.now(
                timezone.utc
            ).isoformat()
        )
        .alias("_ingested_at"),
    )


# ============================================================
# DuckDB
# ============================================================

def initialize_database(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    """
    ingestion_files acts as our ingestion manifest.

    It prevents loading the same month twice.
    """
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS ingestion_files (
            period VARCHAR PRIMARY KEY,
            source_url VARCHAR,
            local_path VARCHAR,

            rows BIGINT,
            columns INTEGER,

            ingested_at TIMESTAMPTZ
                DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def table_exists(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
) -> bool:
    return bool(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'main'
              AND table_name = ?
            """,
            [table_name],
        ).fetchone()[0]
    )


def already_ingested(
    connection: duckdb.DuckDBPyConnection,
    period: str,
) -> bool:
    return bool(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM ingestion_files
            WHERE period = ?
            """,
            [period],
        ).fetchone()[0]
    )


def existing_columns(
    connection: duckdb.DuckDBPyConnection,
) -> set[str]:
    rows = connection.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'main'
          AND table_name = ?
        """,
        [TRIPS_TABLE],
    ).fetchall()

    return {
        row[0]
        for row in rows
    }


def ensure_schema(
    connection: duckdb.DuckDBPyConnection,
    batch: pl.DataFrame,
) -> None:
    """
    ECOBICI's schema may evolve between years.

    If a new column appears, DuckDB adds it instead of
    crashing the entire historical ingestion.
    """

    if not table_exists(
        connection,
        TRIPS_TABLE,
    ):
        connection.register(
            "_schema_batch",
            batch,
        )

        try:
            connection.execute(
                """
                CREATE TABLE trips_raw AS
                SELECT *
                FROM _schema_batch
                WHERE FALSE;
                """
            )
        finally:
            connection.unregister(
                "_schema_batch"
            )

        return

    current = existing_columns(
        connection
    )

    for column in batch.columns:
        # Defensive guard: normalize_columns() should already prevent
        # this, but fail here with a useful message instead of letting
        # DuckDB raise a cryptic parser error.
        if not column.strip():
            raise ValueError(
                "The batch contains an empty column name after normalization."
            )

        if column in current:
            continue

        # Every unexpected historical source field starts as VARCHAR.
        # Source CSV columns are intentionally read as strings so schema
        # changes across years do not break the raw ingestion layer.
        connection.execute(
            f"""
            ALTER TABLE trips_raw
            ADD COLUMN "{column}" VARCHAR;
            """
        )
        current.add(column)


def persist_month(
    connection: duckdb.DuckDBPyConnection,
    batch: pl.DataFrame,
    period: str,
    source_url: str,
    local_path: Path,
    force: bool,
) -> None:

    ensure_schema(
        connection,
        batch,
    )

    connection.register(
        "_month_batch",
        batch,
    )

    connection.execute(
        "BEGIN TRANSACTION"
    )

    try:

        if force:
            connection.execute(
                """
                DELETE FROM trips_raw
                WHERE _source_period = ?
                """,
                [period],
            )

            connection.execute(
                """
                DELETE FROM ingestion_files
                WHERE period = ?
                """,
                [period],
            )

        # BY NAME is important.
        #
        # If 2015 and 2025 have columns in different
        # orders, DuckDB aligns them by column name.
        connection.execute(
            """
            INSERT INTO trips_raw BY NAME
            SELECT *
            FROM _month_batch;
            """
        )

        connection.execute(
            """
            INSERT INTO ingestion_files (
                period,
                source_url,
                local_path,
                rows,
                columns
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                period,
                source_url,
                str(local_path),
                batch.height,
                batch.width,
            ],
        )

        connection.execute(
            "COMMIT"
        )

    except Exception:
        connection.execute(
            "ROLLBACK"
        )
        raise

    finally:
        connection.unregister(
            "_month_batch"
        )


# ============================================================
# Year ingestion
# ============================================================

def ingest_year(
    year: int,
    files: list[tuple[str, str]],
    client: httpx.Client,
    connection: duckdb.DuckDBPyConnection,
    force: bool,
) -> None:

    print()
    print(
        f"===== {year} "
        f"({len(files)} meses) ====="
    )

    total_rows = 0

    for period, url in files:

        if (
            already_ingested(
                connection,
                period,
            )
            and not force
        ):
            print(
                f"{period}  ✓ already ingested"
            )
            continue

        path = (
            RAW_DIR
            / str(year)
            / f"{period}.csv"
        )

        if path.exists():
            print(
                f"{period}  → local CSV"
            )

        else:
            print(
                f"{period}  ↓ downloading"
            )

            download_csv(
                client,
                url,
                path,
            )

        print(
            f"{period}  → Polars"
        )

        batch = read_month(
            path,
            period,
            url,
        )

        print(
            f"{period}  → DuckDB "
            f"({batch.height:,} rows)"
        )

        persist_month(
            connection,
            batch,
            period,
            url,
            path,
            force,
        )

        total_rows += batch.height

    print(
        f"===== {year} ready · "
        f"{total_rows:,} new rows ====="
    )


# ============================================================
# Application
# ============================================================

def run(
    year: int | None,
    from_year: int | None,
    to_year: int | None,
    all_years: bool,
    force: bool,
) -> None:

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = duckdb.connect(
        str(DB_PATH)
    )

    initialize_database(
        connection
    )

    with httpx.Client(
        follow_redirects=True,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent":
                "ecobici-historical-research/0.1"
        },
    ) as client:

        print(
            "Discovering ECOBICI "
            "historical datasets..."
        )

        available = discover_files(
            client
        )

        years = sorted(
            available
        )

        print(
            f"Available: "
            f"{min(years)} → {max(years)}"
        )

        if all_years:
            selected = years

        elif year is not None:
            selected = [year]

        elif (
            from_year is not None
            or to_year is not None
        ):
            start = (
                from_year
                if from_year is not None
                else min(years)
            )

            end = (
                to_year
                if to_year is not None
                else max(years)
            )

            selected = [
                value
                for value in years
                if start <= value <= end
            ]

        else:
            # Safe default:
            # only latest available year.
            selected = [
                max(years)
            ]

        for selected_year in selected:

            if selected_year not in available:
                print(
                    f"{selected_year}: "
                    "no published files"
                )
                continue

            ingest_year(
                selected_year,
                available[selected_year],
                client,
                connection,
                force,
            )

    if table_exists(
        connection,
        TRIPS_TABLE,
    ):
        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM trips_raw
            """
        ).fetchone()[0]

        print()
        print(
            f"Total trips in DuckDB: "
            f"{total:,}"
        )

    connection.close()

    print(
        f"DuckDB: {DB_PATH}"
    )


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--year",
        type=int,
        help="Load one year, e.g. 2025",
    )

    parser.add_argument(
        "--from-year",
        type=int,
    )

    parser.add_argument(
        "--to-year",
        type=int,
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Load every historical year",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Reload months already ingested",
    )

    args = parser.parse_args()

    run(
        year=args.year,
        from_year=args.from_year,
        to_year=args.to_year,
        all_years=args.all,
        force=args.force,
    )