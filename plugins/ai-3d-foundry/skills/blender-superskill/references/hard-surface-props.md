# Hard-Surface Props

Use this reference for batteries, utility cabinets, transformers, generators, HVAC units, service boxes, industrial modules, and cable-connected props.

## Reference-Led Step Loop

For each visible feature:

1. Look at the reference.
2. Name the feature's parent/anchor and estimate the relevant proportions.
3. Build one feature only in Solid shading.
4. Inspect the Blender result from the correct view.
5. Inspect attachment points from close-up and, when relevant, six orthographic sides.
6. Look back at the reference.
7. Iterate before moving on.

Do not add vents, hatches, bolts, panels, sockets, and cables in one batch.

## Low-Poly Edge Discipline

For stylized reusable hard-surface props, crisp construction beats rounded polish.

- Do not add bevel modifiers to every cube, panel, plinth, bolt, rim, or base.
- Do not use weighted normals as a default finishing pass; they can make blocky assets look soft and over-rendered.
- Preserve hard seams, square corners, faceted cylinders, and planar face breaks unless the reference clearly shows a chamfer or rounded part.
- For colored bands on a continuous object, do not split the model into stacked objects just to change color. Build one mesh with ring/face loops and assign materials to the band faces.
- When a reference shows a chamfer, model it as a small flat cut face and inspect it. The chamfer should read as construction, not smoothing.
- Rectangular bolts, raised panels, trim strips, hatch rims, vents, and industrial bases should usually stay square-edged.
- If the viewport screenshot starts reading like rounded plastic instead of crisp low-poly industrial geometry, remove the bevels before adding more detail.

## Repeating Detail Modules

Build repeated details as modules first, then duplicate them as single-user objects.

- Validate one complete module in close-up before duplicating it.
- Do not leave linked duplicates/shared mesh data in the final asset. Blender cannot Apply Transform cleanly on multi-user mesh objects, and per-object edits become annoying.
- Keep consistency by reusing the same dimensions, anchor math, and construction helper, not by sharing the mesh datablock.
- Railings should be post-to-post panel modules with foot plates, posts, mid rail, and top rail built together. Do not make loose long rails and hope they visually meet separate posts.
- Rim facets, vents, louver slats, bolts, ladder rungs, stair treads, fence sections, warning panels, and repeated brackets should come from a proven source module or shared dimensions.
- Anchor module endpoints to real parent surfaces. For a rail panel, post bottoms must penetrate or sit on the deck; for a vent module, slats must sit inside the frame; for rim facets, each block must seat on the rim line.
- After duplicating modules around a circle or platform, inspect a side view and a close connection view to catch floating posts, mis-rotated rails, or uneven gaps.

## Anatomy And Proportion Pass

Before modeling a hard-surface prop, write a quick anatomy list:

- primary mass
- secondary masses
- through-parts, such as pipes, axles, rails, beams, or cables
- connection parts, such as flanges, collars, sockets, brackets, feet, hinges, or saddles
- repeated detail, such as bolts, vents, slats, caps, handles, or ribs
- support logic: what holds the object up, and where it touches the ground or parent object

Then estimate ratios from the reference before the first primitive:

- total length : height : depth
- main body size relative to through-parts
- flange/collar diameter relative to pipe diameter
- wheel/handle/antenna/sign size relative to the body
- support height and footprint relative to the object it holds

If these ratios are wrong, the model may be recognizable but still bad. Fix blockout proportions before adding detail.

## Pipe / Valve Assembly Pattern

1. Start with the side silhouette in Solid shading:
   - continuous pipe axis
   - dominant valve body
   - flange/collar stacks
   - support saddles and base plates
   - vertical neck and wheel/handle envelope
2. Compare proportions before details:
   - valve body should dominate over the pipe if the reference shows a bulky body
   - handwheel diameter should be checked against body width
   - flange width and diameter should be checked against pipe diameter
3. Build mechanical connections in order:
   - pipe passes into or overlaps flanges/body
   - collars/flanges overlap pipe/body faces
   - supports seat into pipe underside with a saddle or overlap
   - vertical neck seats into valve body top
   - wheel spokes overlap both hub and rim
4. Inspect from six sides before adding bolts:
   - side view for length/height
   - front/back for body roundness and flange spacing
   - top for wheel/body alignment
   - underside for supports and saddle contact
5. Add bolts only after flange/body proportions are approved.

## Battery / Utility Cabinet Pattern

1. Build the mass first:
   - match front width, height, depth, and chunkiness
   - use a dark base/plinth if the reference has one
   - add base feet/notches only if they affect the silhouette
2. Add the body edge treatment:
   - keep hard square edges unless the reference visibly shows planar chamfers
   - model only the specific chamfered edges shown in the reference
   - force flat shading afterward
   - avoid weighted normals when they make edges look soft or rounded
3. Build front panels as real recesses:
   - cut one clean shallow rectangular pocket
   - add a dark backplate inside the pocket
   - add cube-clean frame bars and door plates inside the pocket
   - keep visible inserts flush inside the recess, not proud of the surface
4. Build top details as separate steps:
   - top vent: shallow top recess, dark bed, simple rim, parallel slats
   - top hatch: low gray plate with darker inner plate
   - corner caps: blocky raised caps near top corners
5. Build side cable assemblies port-first:
   - make a side bay or dark socket area
   - seat rectangular socket blocks in the bay
   - start cables exactly at socket centers
   - add a short straight exit before the cable bends
   - route cables with controlled curves, not loose loops
   - terminate each cable at a simple ground pad or collar

## Recessed Panels

Surface rectangles are not panels. A panel should have depth:

- Cut the body first with a shallow boolean pocket.
- Place the visible panel/backplate at the back of the pocket.
- Put frame bars and door plates inside the pocket.
- The panel face should usually be flush with, or slightly behind, the parent wall face. Do not paste proud rectangular plaques on the outside unless the reference clearly shows a raised cover.
- Use an inward seam/frame: a thin dark reveal around the panel that is recessed into the wall, not a border sitting on top of it.
- Treat screens as recessed panels. Cut the console or cabinet face first, put the dark screen bed at the back of that cut, and seat the smaller glowing glass/UI elements inside it so no display surface clips through or floats proud of the parent face.
- Add handles/bolts only after the panel reads cleanly.

Prefer one main bay cut over many tiny cuts. Many small cuts can make the main face messy.

The same rule applies to roof insets, hatch beds, vent beds, and decorative rectangular reveals. If the reference reads as an inward extrusion on the parent piece, rebuild or cut the parent mesh so the inset floor and side walls are part of that piece. Do not simulate the inset with thin bars or rectangles placed on top of an uncut surface.

## Vents And Louvers

Vents are openings with inserts, not stacks of bars pasted onto the wall.

- Cut or build a shallow pocket in the parent wall first.
- Keep the surrounding wall face continuous around the opening.
- Put a dark backplate at the rear of the pocket.
- Seat the frame and all louver slats inside the pocket. Their front-most face must stay flush with or behind the parent wall plane, never proud of it.
- Use a thin inward reveal around the opening so the cut reads as real depth.
- Build one slat to the correct depth and spacing, then duplicate it with the same dimensions.
- Inspect from a side view specifically to prove the slats do not protrude beyond the wall face.

## Cables And Hoses

- Use bevel-depth curves for cables.
- Anchor curve start points from measured socket positions.
- Keep the first segment straight out of the socket.
- Use a small number of curve points for disciplined industrial bends.
- Use separate cable objects until routing is approved.
- Make ground pads/collars separate simple objects.

## Common Failures

- Generic cube block instead of reference-matched cabinet proportions.
- Bevels sprayed over every edge, making a low-poly prop look rounded, soft, or plastic.
- Soft bevels or weighted normals where the reference needs hard planar faces.
- Repeated rails, posts, bolts, slats, or rim blocks hand-placed as unrelated one-offs, causing drift, bad rotations, floating contact, or inconsistent spacing.
- Linked duplicate mesh data left in final assets, causing Cannot apply transform / multi-user mesh errors.
- Panel rectangles pasted on the surface.
- Louver vents built as frames and bars stuck on top of an uncut wall.
- Roof insets or panel seams made from raised strips on top of a flat roof cap instead of a real inward cut.
- Custom pocket meshes with inward-wound side/back faces that disappear from the relevant outside view.
- Too many details added before the body shape is approved.
- Cable curves that are too long, too organic, or all bunched into one pad.
