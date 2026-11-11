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
    "Gray": "#808080", "Yellow": "#FFFF00", "White": "#FFFFFF", "None": "none"
}
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]
FONT_OPTIONS = ["Sans-serif", "Serif", "Monospace", "Fantasy", "Cursive", "Courier New", "Verdana", "Arial"]

def draw_fbd(forces, directions, labels, colors, advanced_mode, inclined_angle, shape, uploaded_file, font_choice, arrow_thickness, arrowhead_size, arrow_offset, show_ground, font_size, show_box, box_color):
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
    
    max_val = max(forces) if forces else 1
    scale = 1.5 / max_val if max_val > 0 else 1
    
    for i in range(len(forces)):
        f_scaled = forces[i] * scale
        a = np.radians(0) # Simplified for demonstration; add back full logic as needed
        dx, dy = f_scaled * np.cos(a), f_scaled * np.sin(a)
        tx, ty = (dx/f_scaled * arrow_offset) if f_scaled > 0 else 0, (dy/f_scaled * arrow_offset) if f_scaled > 0 else 0
        ax.arrow(tx, center_y+ty, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        
        bbox = dict(facecolor=box_color, alpha=0.7, edgecolor='none') if show_box and box_color != "none" else None
        ax.text(tx+dx*1.3, center_y+ty+dy*1.3, labels[i], fontsize=font_size, fontweight='bold', ha='center', va='center', color=colors[i], bbox=bbox)
    
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    return fig

def main():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Technical Settings")
        import_file = st.file_uploader("Import Project", type=["fbd"])
        mode = st.radio("Mode", ["Regular", "Advanced"])
        inclined_angle = st.number_input("Inclined Plane Angle", 0, 45, 0) if mode == "Advanced" else 0
        num_forces = st.number_input("Number of Forces:", 1, 10, 2)
        shape = st.selectbox("Object Shape", SHAPE_OPTIONS)
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        
        forces, labels, colors = [], [], []
        for i in range(num_forces):
            with st.expander(f"Force {i+1}"):
                forces.append(st.number_input("Magnitude", value=5, key=f"m{i}"))
                labels.append(st.text_input("Label", f"F{i+1}", key=f"l{i}"))
                colors.append(COLOR_OPTIONS[st.selectbox("Color", list(COLOR_OPTIONS.keys()), key=f"c{i}")])

    with col2:
        st.header("Diagram")
        fig = draw_fbd(forces, ["Up"]*num_forces, labels, colors, mode=="Advanced", inclined_angle, shape, uploaded_file, "Sans-serif", 2, 0.3, 0, True, 12, False, "none")
        st.pyplot(fig)
        
        st.header("Aesthetic Settings")
        a1, a2 = st.columns(2)
        with a1:
            arrow_thickness = st.slider("Arrow Thickness", 1.0, 5.0, 2.0)
            st.number_input("Arrow Thickness", 1.0, 5.0, arrow_thickness, key="at_n")
            arrow_offset = st.slider("Arrow Tail Offset", 0.0, 2.0, 0.0)
            st.number_input("Arrow Tail Offset", 0.0, 2.0, arrow_offset, key="ao_n")
        with a2:
            font_size = st.slider("Font Size", 8, 24, 12)
            st.number_input("Font Size", 8, 24, font_size, key="fs_n")
            box_color = COLOR_OPTIONS[st.selectbox("Box Color", list(COLOR_OPTIONS.keys()), index=10)]
            show_box = st.checkbox("Show Box")

if __name__ == "__main__": main()
