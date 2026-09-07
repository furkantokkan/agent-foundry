# Collections And Cleanup

Use this reference for Blender scene organization, asset collections, object joining, tile lots, and final cleanup.

## Collection Rules

- Put generated objects in the user-specified collection.
- If the asset is experimental, create a clearly named subcollection.
- Do not leave objects both inside and outside the intended collection.
- Use parent empties for critique-friendly prototypes.
- Remove old prototype collections when starting over unless the user asks to preserve versions.

## Object Count Discipline

Separate objects are acceptable while learning, but each object needs a role:

- body mesh
- roof mesh
- panel insert module
- door module
- cable curve
- ground pad
- sign module
- rig/control object

For repeated elements, prefer module objects over many unrelated primitives:

- one rail/fence panel module duplicated around a platform
- one stair unit or tread module duplicated along a run when the design repeats
- one rim facet module duplicated around circular equipment
- one louver/slat/bolt/bracket module duplicated with shared dimensions

Do not leave linked duplicates/shared mesh data in final asset collections. Repeated pieces should be consistent because they were built from the same measured module and placement logic, but each object should have its own mesh datablock so Apply Transform and per-object edits work normally. If a repeated module needs variation, duplicate the module intentionally and rename the variant.
Do not leave linked clones hiding in the Outliner. Before finishing, scan the repeated objects for shared mesh datablocks and make them single-user or replace them with clean real duplicates. If a linked clone was useful during blockout, clean it up before calling the asset done.

After approval, join small static detail pieces into logical modules:

- one body mesh
- one door/panel module if useful
- one cable group if routing may vary
- one sign/roof/accessory module
- one rail/fence/platform-access module instead of loose individual posts and bars

## Tile Lots

- Use the project's base tile object for lot grids when available.
- Rebuild lot tiles from documented footprint sizes.
- Position placement/front/min/max empties from actual tile bounds.
- Remove old mesh planes when replacing them with tile lots.
- Keep tile source and lot dimensions as custom properties where useful.

## Cleanup Checks

- Hide or delete unused cutters after booleans.
- Delete temporary swatches and preview-only helpers from final asset collections.
- Keep preview cameras/lights only if they are intentionally useful.
- Verify object names communicate role and step.
- Check repeated objects: identical rail panels, rim facets, slats, bolts, and fence pieces should be clearly derived from one validated module, but must not share mesh datablocks in the final asset.
- Check the Outliner for linked clones, shared mesh data, accidental multi-collection objects, and leftover prototype duplicates. Clean them before final response.
- For contact-critical assemblies, keep a short interface audit list and verify the claimed touching parts still touch after any transforms, joins, or cleanup.
- Before final response, confirm objects are in the intended collection.
