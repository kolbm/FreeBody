# FreeBody implementation and compatibility report

## Backup — last released version

- Snapshot: `release/last-released-2026-11-13` at `aad444d13033156a3897a93d4612ea3c50836873`.
- Contains the exact released code, both object images, splash artwork, requirements and tests.
- Baseline: all 10 original tests passed before changes.
- New work is committed in separate stages. The backup branch is not modified.

## Stage 1 — mass, gravity, acceleration and calculated-value indicators

- Optional positive mass and gravity inputs; classroom default g = 10 m/s².
- Automatic weight acts vertically downward in both modes.
- Acceleration magnitude/direction follow net force divided by mass, with a separate dashed orange arrow and m/s² units.
- Calculator icons and formula hover tips distinguish calculated values; calculated force magnitude/direction are locked. Switching automation off restores manual values.
- Older version-1 .fbd settings, force values and embedded images are retained; missing new settings default to manual operation. New files use version 2.
- Regression coverage: original tests plus legacy fixtures, calculation/validation/UI checks, all font presets and shapes, net/components combinations, signed ramp angles, overlays, style controls, transparency and PNG rendering.
- Result: **16 tests passed**, including the original 10. All 18 fonts render calculated markers with a fallback font; no missing-symbol warnings.

## Stage 2 — live force equations

- Rendered vector sums and separate x/y symbolic and signed numerical equations.
- Force symbols use safe label initials, with numbered duplicates and a symbol key; equation text cannot execute label content.
- Acceleration equations follow the mass toggle. English/Spanish UI and calculated markers remain compatible.
- Force-role selections are preserved separately across mode switches so automatic gravity always targets the selected weight force.
- Result: **19 tests passed** across the cumulative suite, including all original functionality and version-1 fixtures.

## Stage 3 — equilibrium solver

- Solves one selected force magnitude at its entered direction and verifies both axes.
- Zero solutions are represented as zero; impossible directions, perpendicular residuals and conflicting automatic controls produce explanatory errors rather than a false solution.
- Calculated fields are populated after all force edits, so dependent values reflect the same rerun as the live diagram.
- Raw/manual force values remain available when the solver is disabled. Equations, acceleration, net/components and file serialization use the same evaluated forces.
- Result: **23 tests passed**, including 50 N horizontal and 75 N upramp solutions, impossible cases, zero-force cases, source preservation and UI integration.

## Stage 4 — friction and normal force

- Kinetic friction is μkN opposite motion along the surface. Static friction adjusts to the tangential force needed, with a μsN limit; exceeding the limit warns that rest is impossible and does not silently substitute a kinetic coefficient.
- Automatic normal force accounts for every perpendicular force component. Loss of contact gives zero normal/friction forces.
- Coupled normal/friction/equilibrium values are solved as one linear system, including oblique applied forces. Inconsistent and underdetermined systems are explained; one force cannot have two automatic controllers.
- Mapped roles, calculated icons/hover tips, live equations and acceleration use the same solution. Existing partial live-session settings are upgraded safely.
- Result: **31 tests passed**. Added kinetic/static, positive/negative ramp, contact-loss, coupled-solver, invalid-input and bilingual UI tests. Extended the original display/font matrix to include normal/friction/equilibrium together. Released version-1 fixtures still load without changing their forces/images.

## Stage 5 — quality of life and final integration

- Advanced can display ramp-parallel/perpendicular components for each force or the resultant. Parallel is positive uphill (right on a flat surface); perpendicular is positive away from the surface. Components reconstruct the original vectors on either ramp slope.
- Added calculation steps, a balance/acceleration explanation, display precision from 0–6 decimals, and bounded undo/redo of up to 30 source-diagram edits. Precision never rounds the stored physics; calculated values never replace manual source values.
- Calculated inputs have calculator icons and formula hover tips. PNG legends use a font-safe calculated marker/key. The separate dashed acceleration arrow is offset from force arrows and uses its own visual scale.
- Custom force labels require an explicit force selection when a gravity/normal/friction/unknown role cannot be identified. Malformed/unsupported format versions are rejected.
- Result: **39 tests passed**. These include all original 10 tests; released-format fixtures with embedded images; the feature/font/shape/display regression matrix; equilibrium/static/kinetic/contact cases; bilingual UI; undo/redo; exact slider synchronization; and 128 automatic-toggle configurations in four net/components views (512 numerical/view combinations).
- Visual checks: transparent Advanced diagrams with wizard artwork, ramp contact, polar/grid/axes overlays, net/ramp components, calculated labels and acceleration were rendered and inspected. Diagram rendering checks are distinct from the 512 numerical/view combinations above.

## Completion and compatibility

Every stage was tested and committed separately to main after its checks passed. The backup branch remains unchanged. Version-1 files retain their original force values, image bytes, directions and existing settings; automatic physics stays off unless enabled. New version-2 files preserve all new settings and image bytes. The app's older-reader compatibility is not a promise that the old app can evaluate new physics settings.

Physics assumptions are shown in the app: automatic normal force imposes zero perpendicular acceleration; static friction is bounded and is not generally equal to μsN; zero vectors have no direction; equilibrium requires both axes to balance. Contradictory or underdetermined inputs are reported and are not accepted as calculated equilibrium solutions. Tests cover representative inputs and the listed combinations, rather than claiming every possible student input has been exhaustively tested.

Run all checks with `python -m unittest discover -p 'test*.py'` from the repository directory.

## Formula notation and export refinement

- Symbol initials ignore whole words force/forces and fuerza/fuerzas, case-insensitively. Defaults now use F_N, F_G, F_A and F_F. Duplicate remaining initials receive numbers; labels with no remaining initials use a numerical force index.
- Replaced the numerical column-vector shorthand with explicitly labeled ΣFx and ΣFy totals, plus a bilingual explanation distinguishing components from net magnitude. Acceleration summaries likewise name ax and ay.
- Added formula PNG download (readable white background), a standalone LaTeX .tex document, and copyable LaTeX snippets. The same formula rows feed the app, image and LaTeX exports, including component axes, acceleration, calculated values, units and precision.
- Exports use app-generated symbols rather than raw label text, preventing user labels from injecting LaTeX commands. PNG rendering uses Matplotlib without requiring an external LaTeX installation.
- Result: **43 tests passed** across the cumulative suite. New checks cover ignored words, all eight mode/components/acceleration export views, long labels, TeX safety, PNG borders/content, and bilingual download controls. The PNG layout was rendered and visually inspected. Legacy .fbd fixtures and all physics regression tests still pass; this change does not alter saved force labels or file formats.

## Classroom arithmetic and hot-reload correction

- The default numerical display now spells out Horizontal and Vertical calculations with units on every term (for example 100 N − 50 N = 50 N), followed by a labeled Net force result. Component-view symbolic equations remain available when selected.
- The app loads its own formula helper afresh from its exact source path on every rerun, bypassing a stale imported module retained during an app-only Streamlit hot reload. This prevents a mixed view with a new explanation but old NF/GF/AF/FF symbols or column-vector formulas.
- Formula images and LaTeX downloads use the same fresh formulas; saved force labels and .fbd data are unchanged.
- Result: **45 tests passed**, including a simulated stale imported helper, default arithmetic/unit checks, simplified symbols, rendering/export tests, all physics regressions and legacy files. The updated formula PNG was visually inspected.
