from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _ambientcg import json_api, normalize_asset_type


@skill_entry
def main(
    query: str | None = None,
    asset_type: str = "all",
    sort: str = "popular",
    limit: int = 10,
    **_: Any,
) -> dict[str, Any]:
    try:
        data = json_api(
            {
                "q": query,
                "type": normalize_asset_type(asset_type),
                "sort": sort.lower(),
                "limit": limit,
            }
        )
        found = data.get("assets", [])
        assets = [
            {
                "id": a.get("id"),
                "display_name": a.get("title"),
                "type": a.get("type"),
                "category": None,
                "preview_image": (a.get("thumbnails") or {}).get("256-PNG"),
                "short_link": a.get("url"),
            }
            for a in found
        ]
        return skill_success(
            "ambientCG assets found",
            assets=assets,
            count=len(assets),
            total_results=data.get("totalResults", len(assets)),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to search ambientCG")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
