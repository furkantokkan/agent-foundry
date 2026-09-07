# Buildings

Use this reference for commercial buildings, warehouses, factories, sheds, signs, doors, site assets, and low-poly building massing.

## Basic Commercial Building Pattern

1. Start from a clean cube-derived main mass.
2. Keep the origin and base placement predictable.
3. Add broad architectural bands before details:
   - floor split
   - cornice/parapet band
   - roof recess or flat roof detail
4. Use modest extrusions. Overlarge cornices become chunky fast.
5. Anchor entrance kits to the actual facade face, not the full bounding box if cornices protrude.
6. Use shallow boolean cuts for recessed doors and garage doors.
7. Place visible door panels at the back of the pocket.
8. Chain steps/canopies/pillars from contact faces so they touch the building.
9. Place roof signs from mesh-derived anchors: posts touch roof, sign panel touches posts.
10. Join approved detail pieces into logical modules to reduce object spam.

## Warehouse / Slanted Roof Pattern

- Build the warehouse body and opening first.
- Make garage openings on the correct face and scale them to the reference.
- Use real recessed door pockets or reusable garage door modules.
- Build roof objects separately while exploring proportions.
- For slanted/shed roofs, keep thickness and overhang deliberate.
- Check normals/shading after roof edits; flat faces can still shade badly if topology is ambiguous.

## Building Detail Discipline

- Do not add windows, doors, signs, AC units, and props in one pass while learning a building.
- Build one feature, inspect, compare to the reference, then continue.
- Prefer face-derived placement for all attached modules.
- Keep main building masses simple and modular until the design is approved.
