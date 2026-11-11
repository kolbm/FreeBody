import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import json

COLOR_OPTIONS = {
    "Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500",
    "Purple": "#800080", "Cyan": "#00FFFF", "Magenta": "#FF00FF", "Black": "#000000",
    "Gray": "#808080", "Yellow": "#FFFF00", "White": "#FFFFFF"
}
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]
FONT_OPTIONS = ["Sans-serif", "Serif", "Monospace", "Fantasy", "Cursive", "Courier New", "Verdana", "Arial"]

def draw_fbd(forces, directions, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, font_choice, arrow_thickness, arrowhead_size, show_net_force, net_color, show_net_val, show_components, angle_modes, custom_angles, show_grid, show_magnitudes, unit, mass_val, show_mass, arrow_offset, show_ground, motion_dir, motion_corner, font_color, show_box, box_color, font_size):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
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
        
    for i in range(len(forces)):
        f = forces[i]
        scale = 1.5 / max(forces) if max(forces) > 0 else 1
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
        bbox = dict(facecolor=box_color, alpha=0.7, edgecolor='none') if show_box else None
        ax.text(tx+dx*1.2, center_y+ty+dy*1.2, lbl, fontsize=font_size, fontweight='bold', fontfamily=font_choice.lower(), ha='center', va='center', color=font_color, bbox=bbox)

    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    plt.tight_layout()
    return fig

def main():
    st.sidebar.header("Label Settings")
    font_color = COLOR_OPTIONS[st.sidebar.selectbox("Font Color", list(COLOR_OPTIONS.keys()), index=9)]
    font_size = st.sidebar.slider("Font Size", 8, 24, 12)
    show_box = st.sidebar.checkbox("Show Label Background Box")
    box_color = COLOR_OPTIONS[st.sidebar.selectbox("Box Color", list(COLOR_OPTIONS.keys()), index=10)]
    
    # ... (other inputs remain the same)
    st.sidebar.header("Forces")
    num_forces = st.sidebar.number_input("Forces:", 1, 10, 2)
    forces, directions, labels, colors, angle_modes, custom_angles = [], [], [], [], [], []
    for i in range(num_forces):
        with st.sidebar.expander(f"Force {i+1}"):
            forces.append(st.number_input("Magnitude", value=5, key=f"m{i}"))
            labels.append(st.text_input("Label", f"F{i+1}", key=f"l{i}"))
            colors.append(COLOR_OPTIONS[st.selectbox("Color", list(COLOR_OPTIONS.keys()), key=f"c{i}")])
            directions.append(st.selectbox("Dir", ["Up", "Down", "Left", "Right"], key=f"d{i}"))
    
    if st.button("Generate"):
        fig = draw_fbd(forces, directions, labels, colors, False, 0, "Rectangle", None, "Sans-serif", 2, 0.3, False, "#FF0000", False, [False]*num_forces, ["Custom Angle"]*num_forces, [0]*num_forces, False, True, "Newtons", 1, False, 0, True, "None", "Top-Right", font_color, show_box, box_color, font_size)
        st.pyplot(fig)

if __name__ == "__main__": main()
