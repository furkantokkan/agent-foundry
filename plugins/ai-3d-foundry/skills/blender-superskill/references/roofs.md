# Roofs

Use this reference for gable, gambrel, shed/slanted, hip, dormer, gazebo, warehouse, and commercial roof modeling.

## Core Roof Workflow

1. Start roof forms from simple primitives or clean top faces.
2. Define the profile before adding detail:
   - center loop for gable
   - raised edge for shed roof
   - scaled top face for hip roof
   - low-sided cylinder for polygon/gazebo roofs
3. Add thickness. Do not leave paper-thin roof planes.
4. Add overhangs deliberately:
   - side eaves from normal-based expansion
   - front/back overhangs from face extrusions
   - fascia/lip pieces where needed
5. Keep roof objects separate while exploring proportions.
6. Check normals and flat shading after edits.

## Shed / Slanted Roofs

- A shed roof is not just a single tilted plane.
- It needs thickness, side faces, and believable overhang.
- If broad faces shade badly, rebuild as explicit planar quads and force flat shading.

## Dormers

- Build dormers as separate intersecting roof objects first.
- Push their backs into the parent roof so there are no gaps.
- Clean/boolean only after the dormer is approved.

## Common Failures

- Paper-thin roofs.
- Lopsided eaves from global-direction extrusion.
- Bad normals that make correct geometry look broken.
- Over-complex roof cleanup before the roof silhouette reads.
