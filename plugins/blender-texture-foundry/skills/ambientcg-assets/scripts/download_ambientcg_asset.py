from __future__ import annotations

from pathlib import Path
from typing import Any

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success

from _ambientcg import download_rows, fetch


def asset_descriptor(asset_id: str, local_path: str, download: dict[str, str]) -> dict[str, Any]:
    descriptor = AssetDescriptor(
        asset_id=f"ambientcg:{asset_id}",
        variants=[
            AssetFileVariant(
                local_path=local_path,
                format=Path(local_path).suffix.lstrip(".").lower() or "unknown",
                preferred=True,
            )
        ],
        attribution=AssetAttribution(
            source_url=f"https://ambientcg.com/a/{asset_id}",
            license_spdx="CC0-1.0",
            attribution_text="ambientCG asset — CC0 1.0 Universal.",
        ),
        extra={"download_attribute": download.get("downloadAttribute"), "download_url": download.get("downloadLink")},
    )
    descriptor.validate()
    return descriptor.to_dict()


@skill_entry
def main(
    asset_id: str,
    output_dir: str,
    download_attribute: str = "2K-JPG",
    use_raw_link: bool = False,
    **_: Any,
) -> dict[str, Any]:
    try:
        rows = download_rows(asset_id)
        row = next((r for r in rows if r.get("downloadAttribute", "").lower() == download_attribute.lower()), None)
        if row is None:
            return skill_error("ambientCG download not found", download_attribute, downloads=rows)
        url = row.get("rawLink" if use_raw_link else "downloadLink")
        if not url:
            return skill_error("ambientCG download URL missing", download_attribute, row=row)
        path = fetch(url, output_dir)
        return skill_success(
            "ambientCG asset downloaded",
            file=path,
            asset_id=asset_id,
            download=row,
            asset_descriptor=asset_descriptor(asset_id, path, row),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download ambientCG asset")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
