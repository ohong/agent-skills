# Build and verify the editable character

## Discover the actual environment

Locate Blender using the environment's executable lookup and normal application locations; read its version. Use its Python command line or an available Blender connector. Inspect supported APIs for the installed version. Do not assume a connector exists or declare a speculative dependency. Tool setup may proceed within the user's existing authorization.

If Blender cannot be made available within existing authorization, finish the concept work that remains useful. Preserve the user's selection and report the concrete production blocker. An image in a scene, renamed archive, placeholder, or promised later conversion is not the deliverable.

## Choose construction from the performance

| Approach | Suits | Tradeoff |
| --- | --- | --- |
| Separate native parts with a meaningful control hierarchy | Mechanical, stacked, hinged, or rigid characters | Easy to edit and art direct; can expose gaps when forced to bend |
| Deforming armature with selected shape keys | Continuous bodies, bending limbs, facial or silhouette changes | Supports smooth deformation; needs topology and weight checks |
| A deliberate hybrid | Rigid eyes or props on a soft body, mixed materials | Supports distinct mechanics; control ownership must remain clear |

Choose the simplest construction that reproduces the selected poses. Do not impose a universal armature, limb count, or blob generator. Keep geometry native and editable. Flat graphic characters can use native curves, shallow geometry, and articulated parts; a `.blend` does not require a soft 3D aesthetic. Textured facial planes can be rig components, but a whole character on one image billboard is not editable mascot geometry.

Build the silhouette and identity features first. Establish useful scale, forward/up axes, origins, and neutral transforms. Add topology where the selected motion needs deformation. Check extreme poses for collapsed volume, intersecting face parts, broken contact, or detached features before polishing materials.

Use understandable names and semantic controls: controls describe intent, such as attention direction, eye closure, posture, or a characteristic bend. Keep facial expression, gaze, and body pose independently adjustable where the anatomy supports them. Verify that the controls actually cause the intended visible changes. Document control ranges and coupled behavior. Do not add unused rig complexity merely to check boxes.

Keep expressive asymmetry available when it serves the character. Set limits so normal control use remains stable. A feature that looks correct in the neutral frame still needs checks at its intended extremes and in useful combinations.

## Preserve actions and editability

Create named examples that teach the asset's performance. Ordinarily retain a quiet loop and two distinct reactions with clear returns to rest. Adapt the set to the brief and explain any change. Include neutral/rest independently of animation playback.

Verify that actions survive saving and reopening, with correct object or armature assignments. Use the installed Blender version's retention and action APIs. Modern Blender supports layered actions and slots; legacy assumptions about `Action.fcurves` or exporter grouping are not universal. Inspect current official documentation when scripting those operations.

Store a short handoff note in a Blender Text datablock: Blender version, scale, axes, main controls, their ranges, action names and frame ranges, frame rate, neutral-state instructions, and material constraints. Include selected design references internally when helpful. This keeps the single `.blend` understandable without a sidecar manual.

Prefer locally editable dependencies. Pack eligible images and resources, then save. Embedded linked libraries can remain linked rather than locally editable; inspect that distinction. Some external media cannot be packed. Remove unnecessary dependencies or replace them with suitable self-contained assets instead of claiming everything is automatically portable.

## Verify the actual final file

Mechanical verification and visual review answer different questions. Perform both, using a temporary validation location for renders and copies.

1. Save the asset with a useful neutral opening state, camera, and lighting.
2. Open the saved final file in a fresh Blender process. Confirm it loads without missing dependencies.
3. Inspect external paths and linked data explicitly. Reopening a moved copy alone can still resolve assets from their original location.
4. Inspect native geometry, expected controls, action assignments, frame ranges, and action retention. Exercise intended control extremes and combinations.
5. Render representative neutral, expression, and action poses from the reopened asset. Visually compare silhouette and identity against the selected concept.
6. Review movement across each retained action, including the loop seam, reaction recovery, and contact/deformation quality. Keyframe counts alone do not prove good animation.
7. Save any verified corrections and repeat the affected checks on that final file. Remove validation renders from the deliverable set.

Report what ran and what remains unverified. If render or playback inspection is unavailable, state that limit rather than treating file structure as visual proof. Native Blender validation does not establish glTF export correctness, browser speed, or product integration.

Deliver `<mascot-name>.blend` and `<mascot-name>.md`. The Markdown description explains physical identity, expression, movement, and available controls/clips. Count its words and keep it at most 300. Keep the detailed technical map inside Blender. Intermediate images, backups, and diagnostic outputs need not be user deliverables.
