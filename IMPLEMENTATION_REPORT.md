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
