# Expression, movement, and optional web adaptation

For contrasting examples of symbolic states, flat silhouette transformation, and coupled face/body performance, consult [supplied-videos.md](supplied-videos.md).

## Give movement a cause

Choose a material behavior that supports the selected identity: rigid balance, elastic stretch, weighted softness, or another coherent response. Use anticipation, action, reaction, and settling when they make the emotion clearer. Small asymmetry can convey effort or weight; uniform noise usually obscures the action.

Different states need different intentions. Curiosity may lead with gaze and then posture. Success may release held tension. Uncertainty may pause or retract. These are possible mappings, not required emotions. Avoid turning every reaction into a larger smile or every idle into perpetual bobbing.

Test expression from the intended camera and at the smallest real product size. Check body silhouette, face contrast, gaze readability, and quiet neutral behavior. A design without conventional eyes can direct attention through orientation or shape. Do not add speech visemes unless speech is part of the brief.

For a loop, inspect pose and velocity around the wrap, not only matching endpoint images. For reactions, include recovery into rest. For interruptible use, test entering and leaving the action mid-motion; a seamless loop alone does not prove clean transitions. Preserve characteristic timing while allowing practical duration changes.

## Choose a web representation only when integration is requested

| Representation | Prefer when | Cost or limit |
| --- | --- | --- |
| Rendered sprites or video | The camera and reactions are predetermined | Predictable appearance and rendering cost; limited interactive pose or gaze |
| Live glTF geometry and animation | Gaze, pose, camera, or interaction must change continuously | More flexibility; needs export compatibility, loading, rendering, and device testing |

Neither replaces the editable `.blend`. Choose against actual product needs and measured constraints. Do not attach a universal triangle, texture, or file-size budget to every mascot. Establish budgets from screen size, target devices, competing page work, and expected loading behavior.

For glTF, use exporter behavior for the installed Blender version. Bake constraints or drivers into supported object/bone transforms or shape-key channels where required. Blender materials and arbitrary material, physics, or light animation do not automatically survive export. Check action slots, clip names, mappings, and grouping in the actual exported consumer.

Drive product reactions from real events. Define priority, cancellation, transition duration, and neutral fallback. Success responds to confirmed success; text keywords alone should not invent an emotional or operational state. Keep idle variation bounded and let the user complete their task without constant motion.

Provide a reduced-motion static state and pause unnecessary work while hidden or offscreen. Keep the same character identity in those states. When integration is in scope, test the actual application with representative target devices, loading, resizing, interruption, repeated events, failure, reduced motion, and offscreen behavior.

Report native rig verification, exported-asset verification, and application runtime verification separately. Portfolio visuals and Blender preview playback provide no evidence of browser performance.
