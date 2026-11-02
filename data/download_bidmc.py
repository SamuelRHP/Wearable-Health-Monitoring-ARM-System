"""Download script for PhysioNet BIDMC PPG and Respiration Dataset records.

Downloads selected WFDB records from physionet.org/content/bidmc/1.0.0/
under the Open Data Commons Attribution License v1.0 (ODC-By 1.0).
"""

import sys
from pathlib import Path

try:
    import wfdb
except ImportError:
    print("Error: wfdb is not installed. Install with `pip install wfdb`.", file=sys.stderr)
    sys.exit(1)


def download_record(record_name: str = "bidmc01", output_dir: str | Path = "data") -> Path:
    """Download a BIDMC record from PhysioNet.

    Args:
        record_name: Name of the record (e.g. 'bidmc01')
        output_dir: Local destination directory

    Returns:
        Path to local record directory
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    print(f"Downloading record '{record_name}' from PhysioNet BIDMC repository...")

    try:
        wfdb.dl_database(
            db_dir="bidmc",
            dl_dir=str(out_path),
            records=[record_name],
            annotators=None,
            keep_subdirs=False,
        )
        print(f"Successfully downloaded '{record_name}' to {out_path.resolve()}")
    except Exception as exc:
        print(f"Notice: Failed to download from PhysioNet ({exc}).", file=sys.stderr)
        print("The simulation will use the high-fidelity offline synthetic fallback generator.", file=sys.stderr)

    return out_path


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "bidmc01"
    download_record(target)
