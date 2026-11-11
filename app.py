import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
import requests
import matplotlib.patches as patches

COLOR_OPTIONS = {
    "Red": "#FF0000", "Blue": "#0000FF", "Green": "#00FF00", "Orange": "#FFA500",
    "Purple": "#808080", "Cyan": "#00FFFF", "Magenta": "#FF00FF", "Black": "#000000",
    "Gray": "#808080", "Yellow": "#FFFF00"
}
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]
SHAPE_OPTIONS = ["Rectangle", "Square", "Circle", "Triangle"]
FONT_OPTIONS = ["sans-serif", "serif", "monospace", "fantasy", "cursive"]
LABEL_POSITIONS = ["Above", "Below", "At Arrowhead"]

def draw_fbd(forces, directions, labels, colors, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction, shape, rect_rotation, uploaded_image, font_choice, arrow_thickness, arrow_offset, arrowhead_size, label_position, inclined_plane_angle):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    
    # Inclined Plane
    if inclined_plane_angle > 0:
        rad = np.radians(inclined_plane_angle)
        x_vals = np.linspace(-2, 2, 100)
        y_vals = np.tan(rad) * x_vals
        ax.plot(x_vals, y_vals, color='brown', linewidth=3)
        ax.fill_between(x_vals, -3, y_vals, color='sandybrown', alpha=0.3)

    # Object
    if uploaded_image:
        img = Image.open(uploaded_image)
        ax.imshow(img, extent=[-1, 1, -1, 1])
    else:
        if shape == "Rectangle":
            patch = patches.Rectangle((-1, -0.5), 2, 1, angle=rect_rotation, color='gray', fill=True)
        elif shape == "Square":
            patch = patches.Rectangle((-1, -1), 2, 2, angle=rect_rotation, color='gray', fill=True)
        elif shape == "Circle":
            patch = patches.Circle((0, 0), 1, color='gray', fill=True)
        else: # Triangle
            patch = patches.Polygon([(-1, -1), (1, -1), (0, 1)], color='gray', fill=True)
        ax.add_patch(patch)

    # Forces
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
    for i in range(len(forces)):
        f = forces[i] if not simple_mode else 1
        if angled_mode:
            a = np.radians(angles[i])
            dx, dy = f * np.cos(a), f * np.sin(a)
        else:
            dx, dy = [c * f for c in direction_map[directions[i]]]
        
        ax.arrow(0, 0, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.2, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        
        # Labeling
        pos_shift = 0.2
        lx, ly = dx, dy
        if label_position == "Above": ly += pos_shift
        elif label_position == "Below": ly -= pos_shift
        
        ax.text(lx, ly, labels[i], fontsize=12, fontfamily=font_choice, ha='center')

    # Motion Arrow
    if motion_arrow:
        ax.annotate('', xy=(2, 2), xytext=(3, 2), arrowprops=dict(arrowstyle='->', lw=2))
        ax.text(2.5, 2.2, "Motion", ha='center')

    # Watermark
    plt.figtext(0.5, 0.02, "Generated using the Free Body Diagram Generator: freebody.streamlit.app", ha="center", fontsize=8, color='gray')
    plt.tight_layout()
    return fig

def main():
    st.title("Advanced Free Body Diagram Generator")
    # UI Inputs
    num_forces = st.number_input("Number of Forces:", 1, 10, 2)
    simple_mode = st.checkbox("Simple Mode", True)
    inclined_plane = st.slider("Inclined Plane Angle", 0, 45, 0)
    shape = st.selectbox("Object Shape", SHAPE_OPTIONS)
    
    # Sidebar
    st.sidebar.header("Advanced Settings")
    arrow_thickness = st.sidebar.slider("Line Thickness", 1.0, 5.0, 2.0)
    arrowhead_size = st.sidebar.slider("Arrowhead Size", 0.1, 1.0, 0.3)
    motion_arrow = st.sidebar.checkbox("Show Motion Arrow")
    font_choice = st.sidebar.selectbox("Font", FONT_OPTIONS)
    label_position = st.sidebar.selectbox("Label Position", LABEL_POSITIONS)
    
    forces, directions, labels, colors, angles = [], [], [], [], []
    for i in range(num_forces):
        c1, c2, c3 = st.columns(3)
        with c1: forces.append(st.number_input(f"Mag {i+1}", value=5))
        with c2: directions.append(st.selectbox(f"Dir {i+1}", DIRECTION_OPTIONS, key=f"d{i}"))
        with c3: labels.append(st.text_input(f"Label {i+1}", f"F{i+1}"))
        colors.append("#000000")

    if st.button("Generate"):
        fig = draw_fbd(forces, directions, labels, colors, "FBD", motion_arrow, simple_mode, False, angles, "Right", shape, 0, None, font_choice, arrow_thickness, 1.2, arrowhead_size, label_position, inclined_plane)
        buf = BytesIO()
        fig.savefig(buf, format="png", transparent=True)
        st.image(buf)
        st.download_button("Download", buf, "fbd.png", "image/png")

if __name__ == "__main__": main()
