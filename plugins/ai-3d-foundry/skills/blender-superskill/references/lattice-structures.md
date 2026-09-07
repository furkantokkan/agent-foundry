# Lattice Structures

Use this reference for pylons, towers, gantries, trusses, scaffold bridges, cranes, and structural frames.

## Pylon / Tower Pattern

1. Start from the total envelope, not individual bars.
2. Create major height bands.
3. Taper the envelope as it rises.
4. Add crossarms from selected upper faces/edges.
5. Subdivide panels only enough to support the bracing rhythm.
6. Use `Poke Faces` to generate diagonal bracing patterns.
7. Delete filled faces that should become open lattice holes.
8. Add a `Wireframe` modifier for bar thickness.
9. Keep the modifier live until silhouette and density are approved.
10. Add insulators, wires, feet, and warning details separately.

## Low-Poly Pylon Notes

- A clean pylon reads best as one tapered lattice body plus logical modules for crossarms, insulators, and feet.
- Crossarms need depth and triangular support back into the tower. Flat beams floating through the tower read unfinished.
- Insulators must attach to crossarm end blocks or hanger rods. If their first visible disc starts below empty space, the asset reads broken.
- Insulator stacks should be built as a measured chain: hanger touches beam underside, first disc touches or slightly overlaps the hanger, each following disc touches or slightly overlaps the previous one, and the bottom pin touches the final disc.
- For city-scale readability, keep bracing rhythm sparse enough that negative space remains visible.
- Join small static details into modules after critique, but keep the main lattice modifier live while still learning or resizing.

## Crane / Mechanical Structures

- Separate into functional modules: base, tower, cabin, boom, counterweight, trolley, rope, grabber.
- Use simple bars and triangles for scaffold reads.
- Rig only the obvious mechanical functions when needed.
- Place pivots before rigging.
- Keep cables/ropes as curves with hooked endpoints when animated.

## Common Failures

- Starting by placing individual bars instead of defining the envelope.
- Leaving poked panels filled, which reads as decoration instead of open lattice.
- Over-thick wireframe bars that close the negative space.
- Crossarms that float or lack depth.
