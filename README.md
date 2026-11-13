# FreeBody

Bilingual free-body diagrams for high-school Physics and Honors Physics.

**App:** https://freebody.streamlit.app/  
**Repository:** https://github.com/kolbm/FreeBody

## Quick start

1. Select English or Español, then General or Advanced.
2. General uses Up, Down, Left and Right. Advanced adds force angles, ramp-relative directions and a 30° starting ramp.
3. Enter force labels, magnitudes and colors. The diagram updates after each committed input change.
4. Save an editable `.fbd` file or download a transparent PNG.

General starts with 100 N normal upward, 100 N weight downward, 100 N applied right and 50 N friction left. Advanced starts with 100 N weight, 86.602540… N normal, 100 N applied upramp and 25 N friction downramp. Each mode has its own wizard image. The physics tools below are optional; automatic force calculations start off.

## Physics tools

- **Mass:** positive kg value. Default 10 kg and g = 10 m/s²; g is editable in Advanced.
- **Calculate gravity:** choose the existing weight force. The app calculates mg straight down, including on a ramp.
- **Show acceleration:** a = ΣF/m. Its dashed orange arrow has its own visual scale and m/s² units; its length must not be compared with force arrows in N. Acceleration direction is not necessarily motion direction.
- **Solve for equilibrium:** choose one unknown force and enter its direction. The app checks ΣFx = ΣFy = 0. Equilibrium means rest or constant velocity. Impossible or non-unique solutions are explained rather than invented.
- **Calculate normal:** assumes contact without perpendicular acceleration and accounts for all perpendicular force components. A surface cannot pull: loss of contact gives N = 0.
- **Calculate friction:** select the normal and friction forces, coefficient and motion direction. Sliding uses μkN opposite motion. Not moving uses the required static friction up to μsN. If static friction is insufficient, the app shows the limiting value and warns that rest is impossible; select motion and a kinetic coefficient to model sliding.
- Coupled normal/friction/equilibrium values are solved together. A force cannot have two automatic controllers. Some static-friction/equilibrium combinations have no unique solution; enter another force manually or specify motion.

**🧮 / ◆ means calculated.** Hover over calculated inputs for formulas. Their magnitudes are locked; turning automation off restores the original manual inputs. Calculated gravity, normal and friction directions follow their physical constraints. The equilibrium force's direction remains editable.

## Equations and display

Force symbols use saved-label initials: Normal Force → F_N, Gravitational Force → F_G, Applied Force → F_A and Frictional Force → F_F. The words force/forces and fuerza/fuerzas are ignored when forming initials. Duplicate initials receive numbers. Components append x/y or parallel/perpendicular subscripts. Equations show signed values and use all forces, even when the diagram displays only the resultant. The numerical summary explicitly labels horizontal ΣFx and vertical ΣFy totals rather than using column-vector shorthand. Under Force equations, save the current formulas as a readable white-background PNG or a complete LaTeX `.tex` document, or expand Copy LaTeX for equation snippets. These exports follow the current component axes, acceleration settings and display precision.

Net-force and component switches combine: together they show components of the net force. Advanced also supports ramp-aligned components, positive upramp and away from the surface. All angles remain degrees measured counterclockwise from global +x.

Grid, Cartesian axes, degree-based polar references, shape/image controls, 18 font presets, arrow styling and transparent PNG export remain available. Slider settings also have synchronized exact entry and −/+ controls. Display precision does not round saved or calculated values. Expand **Show calculation steps** for explanations.

Undo/redo remembers up to 30 source-diagram edits in the current session; history itself is not included in `.fbd` files. Restore starting forces resets the selected mode to its preset.

## File compatibility

The app reads released version-1 `.fbd` files, preserving their force values, directions, settings and embedded images. Missing physics settings default to manual operation. Version-2 files save the new physics settings and full image bytes. New files are intended for the updated app; loading them in the older app does not reproduce its new automatic calculations. Malformed inputs and unsupported future versions are rejected with a message.

## Run and test

```bash
pip install -r requirements.txt
streamlit run app.py
python -m unittest discover -p 'test*.py'
```

The cumulative tests include the released regression suite, version-1 fixtures with images, physics and error cases, bilingual UI interactions, fonts/shapes/overlays, component reconstruction, undo/redo, precision and automatic-toggle combinations.

## Last released backup

The unmodified pre-improvement app is preserved at [release/last-released-2026-11-13](https://github.com/kolbm/FreeBody/tree/release/last-released-2026-11-13), commit `aad444d13033156a3897a93d4612ea3c50836873`.

See [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) for the report after each implementation stage.
