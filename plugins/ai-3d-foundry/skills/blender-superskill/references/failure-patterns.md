# Failure Patterns

Use this reference when a Blender asset looks wrong, noisy, generic, soft, broken, or hard to critique.

## Generic Primitive Drift

Symptom:
- The asset technically uses a cube, cylinder, or plane but does not match the reference shape.

Fix:
- Re-check reference proportions.
- Match silhouette before adding details.
- Stop calling the primitive itself the desired object.

## Recognizable But Wrong Proportions

Symptom:
- The object can be identified, but it does not feel like the reference.
- Main masses are the wrong hierarchy: a body that should dominate is too small, a wheel is too tiny, a pipe is too thick, or supports are generic.
- Details were added before proving the blockout ratios.

Fix:
- Stop adding detail.
- Return to Solid shading and inspect the silhouette.
- Write the important ratios from the reference: length/height/depth, primary mass to secondary mass, connector size to through-part size.
- Rebuild or resize the blockout before preserving any detail.

Rule:
- Recognition is not enough. Proportions are part of construction.

## Surface Sticker Detail

Symptom:
- Panels, doors, windows, or vents are rectangles pasted on the surface.

Fix:
- Cut a shallow recess first.
- Place visible inserts inside the pocket.
- Keep inserts flush with the recess, not proud of the body.

## Bevel Addiction

Symptom:
- The asset looks soft, melted, or toy-like in the wrong way.

Fix:
- Use smaller one-segment flat chamfers.
- Apply geometry and force flat shading when the reference has planar angled edges.
- Avoid weighted normals when they hide the chamfer plane.

## Boolean Noise

Symptom:
- Faces become messy, panels look damaged, or details create diagonal artifacts.

Fix:
- Use one broad clean cut instead of many tiny cuts.
- Put detail inserts inside that cut as separate cube-clean objects.
- Use direct face topology only when the wall/body was planned for it.

## Wrong View Critique

Symptom:
- A top detail is judged from the front, a side cable is judged from too far away, or selection outlines hide the surface.

Fix:
- Change the camera/view to match the detail.
- Deselect before judging surfaces.
- Compare to reference again from the right view.
- Use six-side orthographic checks for attached assemblies: front, back, left, right, top, and underside/bottom.

## Cable Noodles

Symptom:
- Cables are too organic, too long, floating, or all terminate at one messy point.

Fix:
- Build sockets first.
- Start curves exactly at socket centers.
- Add short straight exits before bends.
- Use controlled curves and separate ground pads/collars.

## Floating Stack / Fake Contact

Symptom:
- Parts look aligned from far away but have visible gaps in close-up.
- A hanging or stacked detail appears under the parent object but is not actually seated into it.
- Repeated discs, sockets, caps, posts, or cables are placed by eye and drift apart.

Fix:
- Stop and inspect only that attachment area in close-up.
- Name the parent surface before placing the child part, such as `underside of crossarm end block` or `center of socket face`.
- Derive child location from the parent bounding box, dimensions, or face center.
- Use exact contact or a tiny intentional overlap so the pieces read as connected.
- Validate one instance before duplicating it across the asset.

Rule:
- Visual alignment is not connection. Connection is proven by close-up inspection from a gap-revealing angle.
