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
    "Gray": "#808080", "Yellow": "#FFFF00", "White": "#FFFFFF"
}
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]
FONT_OPTIONS = ["Sans-serif", "Serif", "Monospace", "Fantasy", "Cursive", "Courier New", "Verdana", "Arial"]
UNIT_OPTIONS = ["Newtons (N)", "Pounds (lbs)"]
PREFIX_OPTIONS = ["", "kilo (k)", "centi (c)", "milli (m)", "micro (u)"]
TITLE_IMAGE_URL = "https://github.com/kolbm/FreeBody/blob/main/title.jpg?raw=true"

def draw_fbd(forces, directions, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, font_choice, arrow_thickness, arrowhead_size, show_net_force, net_color, show_net_val, show_components, angle_modes, custom_angles, show_grid, show_magnitudes, unit, mass_val, show_mass, arrow_offset, show_ground, motion_dir, motion_corner, show_box, box_color, font_size):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.set_aspect('equal', adjustable='box')
    rad = np.radians(inclined_angle) if advanced_mode else 0
    t_rot = transforms.Affine2D().rotate_deg(inclined_angle if advanced_mode else 0)
    center_y = 0.5 + (0.5 if shape != "Circle" else 1.0)
    
    # Ground/Ramp
    ax.axis('off')
    if show_ground and inclined_angle >= 0:
        ax.plot([-5, 5], [np.tan(rad)*-5, np.tan(rad)*5], color='brown', linewidth=3)
        ax.fill_between([-5, 5], -6, [np.tan(rad)*-5, np.tan(rad)*5], color='sandybrown', alpha=0.3)
    
    # Object
    if uploaded_file:
        img = Image.open(uploaded_file)
        ax.imshow(img, extent=[-1, 1, 0, 2], transform=t_rot + ax.transData)
    else:
        if shape == "Rectangle": patch = patches.Rectangle((-1, 0), 2, 1, color='gray', fill=True, transform=t_rot + ax.transData)
        elif shape == "Square": patch = patches.Rectangle((-1, 0), 2, 2, color='gray', fill=True, transform=t_rot + ax.transData)
        elif shape == "Circle": patch = patches.Circle((0, 1), 1, color='gray', fill=True, transform=t_rot + ax.transData)
        else: patch = patches.Polygon([(-1, 0), (1, 0), (0, 2)], color='gray', fill=True, transform=t_rot + ax.transData)
        ax.add_patch(patch)
    
    # Forces
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
        bbox = dict(facecolor=box_color, alpha=0.7, edgecolor='none') if show_box else None
        ax.text(tx+dx*1.2, center_y+ty+dy*1.2, lbl, fontsize=font_size, fontweight='bold', fontfamily=font_choice.lower(), ha='center', va='center', color=colors[i], bbox=bbox)
    
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    return fig

def main():
    st.sidebar.image(TITLE_IMAGE_URL, use_container_width=True)
    mode = st.radio("Mode", ["Regular", "Advanced"])
    inclined_angle = st.slider("Inclined Plane Angle", 0, 45, 0) if mode == "Advanced" else 0
    shape = st.selectbox("Object Shape", SHAPE_OPTIONS)
    uploaded_file = st.file_uploader("Insert Picture", type=["png", "jpg", "jpeg"])
    
    st.sidebar.header("Label Settings")
    font_choice = st.sidebar.selectbox("Font Style", FONT_OPTIONS)
    font_size = st.sidebar.slider("Font Size", 8, 24, 12)
    show_box = st.sidebar.checkbox("Show Label Background Box")
    box_color = COLOR_OPTIONS[st.sidebar.selectbox("Box Color", list(COLOR_OPTIONS.keys()), index=10)]
    
    st.sidebar.header("Advanced Settings")
    arrow_thickness = st.sidebar.slider("Arrow Line Thickness", 1.0, 5.0, 2.0)
    arrowhead_size = st.sidebar.slider("Arrowhead Size", 0.1, 1.0, 0.3)
    arrow_offset = st.sidebar.slider("Arrow Tail Offset", 0.0, 2.0, 0.0)
    show_ground = st.sidebar.checkbox("Display Ground", True)
    show_magnitudes = st.sidebar.checkbox("Show Magnitudes in Labels")
    
    st.sidebar.header("Forces")
    num_forces = st.sidebar.number_input("Number of Forces:", 1, 10, 2)
    forces, directions, labels, colors, angle_modes, custom_angles, show_components = [], [], [], [], [], [], []
    for i in range(num_forces):
        with st.sidebar.expander(f"Force {i+1}"):
            forces.append(st.number_input("Magnitude", value=5, key=f"m{i}"))
            labels.append(st.text_input("Label", f"F{i+1}", key=f"l{i}"))
            colors.append(COLOR_OPTIONS[st.selectbox("Color", list(COLOR_OPTIONS.keys()), key=f"c{i}")])
            if mode == "Advanced":
                angle_modes.append(st.selectbox("Mode", ["Custom Angle", "Up the ramp", "Down the ramp", "Perpendicular to ramp"], key=f"am{i}"))
                custom_angles.append(st.number_input("Angle", value=0, key=f"a{i}"))
                show_components.append(st.checkbox("Components", key=f"comp{i}"))
            else:
                directions.append(st.selectbox("Direction", ["Up", "Down", "Left", "Right"], key=f"d{i}"))
                angle_modes.append("Custom"); custom_angles.append(0); show_components.append(False)
    
    if st.button("Generate"):
        fig = draw_fbd(forces, directions, labels, colors, mode=="Advanced", inclined_angle, shape, uploaded_file, font_choice, arrow_thickness, arrowhead_size, False, "#FF0000", False, show_components, angle_modes, custom_angles, False, show_magnitudes, "Newtons", 1.0, False, arrow_offset, show_ground, "None", "Top-Right", show_box, box_color, font_size)
        st.pyplot(fig)

if __name__ == "__main__": main()
