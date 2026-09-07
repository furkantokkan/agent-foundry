from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _ambientcg import download_rows


@skill_entry
def main(asset_id: str, **_: Any) -> dict[str, Any]:
    try:
        rows = download_rows(asset_id)
        downloads = [
            {
                "attribute": row.get("downloadAttribute"),
                "filetype": row.get("filetype"),
                "size": int(row.get("size") or 0),
                "download_link": row.get("downloadLink"),
            }
            for row in rows
        ]
        return skill_success("ambientCG downloads listed", asset_id=asset_id, downloads=downloads)
    except Exception as exc:
        return skill_exception(exc, message="Failed to list ambientCG downloads")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
