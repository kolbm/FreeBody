import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import json

# Constants and Options
COLOR_OPTIONS = {
    "Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500",
    "Purple": "#800080", "Cyan": "#00FFFF", "Magenta": "#FF00FF", "Black": "#000000",
    "Gray": "#808080", "Yellow": "#FFFF00", "White": "#FFFFFF", "Transparent": "none"
}
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]
FONT_OPTIONS = ["Sans-serif", "Serif", "Monospace", "Fantasy", "Cursive", "Courier New", "Verdana", "Arial"]

def draw_fbd(forces, directions, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, font_choice, arrow_thickness, arrowhead_size, show_net_force, net_color, show_net_val, show_components, angle_modes, custom_angles, show_grid, show_magnitudes, unit, arrow_offset, show_ground, font_size, show_box, box_color):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_aspect('equal', adjustable='box')
    rad = np.radians(inclined_angle) if advanced_mode else 0
    t_rot = transforms.Affine2D().rotate_deg(inclined_angle if advanced_mode else 0)
    center_y = 0.5 + (0.5 if shape != "Circle" else 1.0)
    
    ax.axis('off')
    if show_ground and inclined_angle >= 0:
        ax.plot([-5, 5], [np.tan(rad)*-5, np.tan(rad)*5], color='brown', linewidth=3)
        ax.fill_between([-5, 5], -6, [np.tan(rad)*-5, np.tan(rad)*5], color='sandybrown', alpha=0.3)
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        ax.imshow(img, extent=[-1, 1, 0, 2], transform=t_rot + ax.transData)
    else:
        if shape == "Rectangle": patch = patches.Rectangle((-1, 0), 2, 1, color='gray', fill=True, transform=t_rot + ax.transData)
        elif shape == "Square": patch = patches.Rectangle((-1, 0), 2, 2, color='gray', fill=True, transform=t_rot + ax.transData)
        elif shape == "Circle": patch = patches.Circle((0, 1), 1, color='gray', fill=True, transform=t_rot + ax.transData)
        else: patch = patches.Polygon([(-1, 0), (1, 0), (0, 2)], color='gray', fill=True, transform=t_rot + ax.transData)
        ax.add_patch(patch)
    
    if show_grid:
        for i in np.arange(-5, 6, 1):
            ax.plot([i, i], [-5, 5], 'k--', alpha=0.1)
            ax.plot([-5, 5], [i, i], 'k--', alpha=0.1)
    
    max_val = max(forces) if forces else 1
    scale = 1.5 / max_val if max_val > 0 else 1
    
    for i in range(len(forces)):
        f = forces[i]
        f_scaled = f * scale
        if advanced_mode:
            if angle_modes[i] == "Up the ramp": a = rad
            elif angle_modes[i] == "Down the ramp": a = rad + np.pi
            elif angle_modes[i] == "Perpendicular to ramp": a = rad + np.pi/2
            else: a = np.radians(custom_angles[i])
            dx, dy = f_scaled * np.cos(a), f_scaled * np.sin(a)
        else:
            direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
            dx, dy = [c * f_scaled for c in direction_map[directions[i]]]
        
        tx, ty = (dx/f_scaled * arrow_offset) if f_scaled > 0 else 0, (dy/f_scaled * arrow_offset) if f_scaled > 0 else 0
        ax.arrow(tx, center_y+ty, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        
        lbl = labels[i]
        if show_magnitudes: lbl += f" ({f}{unit[0]})"
        bbox = dict(facecolor=box_color, alpha=0.7, edgecolor='none') if show_box and box_color != "none" else None
        # Offset text away from arrowhead
        ax.text(tx+dx*1.3, center_y+ty+dy*1.3, lbl, fontsize=font_size, fontweight='bold', fontfamily=font_choice.lower(), ha='center', va='center', color=colors[i], bbox=bbox)
    
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    return fig

def main():
    st.set_page_config(layout="wide")
    
    # State management
    if "project" not in st.session_state: st.session_state.project = {}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Technical Settings")
        import_file = st.file_uploader("Import FBD", type=["fbd"])
        if import_file: st.session_state.project = json.load(import_file)
        
        mode = st.radio("Mode", ["Regular", "Advanced"])
        inclined_angle = st.number_input("Inclined Plane Angle", 0, 45, 0) if mode == "Advanced" else 0
        num_forces = st.number_input("Number of Forces:", 1, 10, 2)
        shape = st.selectbox("Object Shape", SHAPE_OPTIONS)
        
        forces, directions, labels, colors, angle_modes, custom_angles = [], [], [], [], [], []
        for i in range(num_forces):
            with st.expander(f"Force {i+1}"):
                forces.append(st.number_input("Magnitude", value=5, key=f"m{i}"))
                labels.append(st.text_input("Label", f"F{i+1}", key=f"l{i}"))
                colors.append(COLOR_OPTIONS[st.selectbox("Color", list(COLOR_OPTIONS.keys()), key=f"c{i}")])
                if mode == "Advanced":
                    angle_modes.append(st.selectbox("Angle Mode", ["Custom Angle", "Up the ramp", "Down the ramp", "Perpendicular to ramp"], key=f"am{i}"))
                    custom_angles.append(st.number_input("Angle", value=0, key=f"a{i}"))
                else:
                    directions.append(st.selectbox("Direction", DIRECTION_OPTIONS, key=f"d{i}"))
                    angle_modes.append("Custom"); custom_angles.append(0)
        
        if st.button("Generate"): st.session_state.generate = True
        if st.button("Export FBD"): st.download_button("Download", json.dumps({"forces": forces}), "diagram.fbd")

    with col2:
        st.header("Diagram")
        fig = draw_fbd(forces, directions, labels, colors, mode=="Advanced", inclined_angle, shape, None, "Sans-serif", 2, 0.3, False, "#FF0000", False, [], angle_modes, custom_angles, False, False, "Newtons", 0, True, 12, False, "#FFFFFF")
        st.pyplot(fig)
        
        st.header("Aesthetic Settings")
        a1, a2 = st.columns(2)
        with a1:
            arrow_thickness = st.number_input("Arrow Thickness", 1.0, 5.0, 2.0)
            font_size = st.number_input("Font Size", 8, 24, 12)
        with a2:
            show_box = st.checkbox("Show Background Box")
            box_color = COLOR_OPTIONS[st.selectbox("Box Color", list(COLOR_OPTIONS.keys()), index=10)]

if __name__ == "__main__": main()
