import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
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

def draw_fbd(forces, directions, labels, colors, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction, shape, rect_rotation, uploaded_image, font_choice, arrow_thickness, arrow_offset, arrowhead_size, label_position, inclined_plane_angle, show_net_force, show_components):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    
    # Inclined Plane
    if inclined_plane_angle > 0:
        rad = np.radians(inclined_plane_angle)
        ax.plot([-2, 2], [np.tan(rad)*-2, np.tan(rad)*2], color='brown', linewidth=3)
        ax.fill_between([-2, 2], -3, [np.tan(rad)*-2, np.tan(rad)*2], color='sandybrown', alpha=0.3)

    # Object
    if uploaded_image:
        img = Image.open(uploaded_image)
        ax.imshow(img, extent=[-1, 1, -1, 1])
    else:
        if shape == "Rectangle": patch = patches.Rectangle((-1, -0.5), 2, 1, angle=rect_rotation, color='gray', fill=True)
        elif shape == "Square": patch = patches.Rectangle((-1, -1), 2, 2, angle=rect_rotation, color='gray', fill=True)
        elif shape == "Circle": patch = patches.Circle((0, 0), 1, color='gray', fill=True)
        else: patch = patches.Polygon([(-1, -1), (1, -1), (0, 1)], color='gray', fill=True)
        ax.add_patch(patch)

    # Forces
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
    net_dx, net_dy = 0, 0
    for i in range(len(forces)):
        f = forces[i] if not simple_mode else 1
        dx, dy = [c * f for c in direction_map[directions[i]]]
        net_dx += dx; net_dy += dy
        
        ax.arrow(0, 0, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        if show_components[i]:
            ax.plot([0, dx], [0, 0], 'k--', alpha=0.5)
            ax.plot([dx, dx], [0, dy], 'k--', alpha=0.5)
        
        ax.text(dx * arrow_offset, dy * arrow_offset, labels[i], fontsize=12, fontfamily=font_choice, ha='center')

    if show_net_force:
        ax.arrow(0, 0, net_dx, net_dy, head_width=arrowhead_size*1.5, head_length=arrowhead_size*2, fc='black', ec='black', linewidth=arrow_thickness+1, linestyle=':')
        ax.text(net_dx * arrow_offset, net_dy * arrow_offset, f"Net: {np.hypot(net_dx, net_dy):.1f}N", color='black', fontweight='bold')

    plt.figtext(0.5, 0.02, "Generated using the Free Body Diagram Generator: freebody.streamlit.app", ha="center", fontsize=8, color='gray')
    plt.tight_layout()
    return fig

def main():
    st.title("Advanced Free Body Diagram Generator")
    num_forces = st.number_input("Number of Forces:", 1, 10, 2)
    simple_mode = st.checkbox("Simple Mode", True)
    inclined_plane = st.slider("Inclined Plane Angle", 0, 45, 0)
    shape = st.selectbox("Object Shape", SHAPE_OPTIONS)
    uploaded_file = st.file_uploader("Insert Picture", type=["png", "jpg", "jpeg"])
    
    st.sidebar.header("Advanced Settings")
    arrow_thickness = st.sidebar.slider("Line Thickness", 1.0, 5.0, 2.0)
    arrowhead_size = st.sidebar.slider("Arrowhead Size", 0.1, 1.0, 0.3)
    font_choice = st.sidebar.selectbox("Font", FONT_OPTIONS)
    show_net_force = st.sidebar.checkbox("Show Net Force")
    
    forces, directions, labels, colors, show_components = [], [], [], [], []
    for i in range(num_forces):
        with st.expander(f"Force {i+1}"):
            c1, c2, c3, c4 = st.columns(4)
            forces.append(c1.number_input(f"Mag", value=5, key=f"m{i}"))
            directions.append(c2.selectbox(f"Dir", DIRECTION_OPTIONS, key=f"d{i}"))
            labels.append(c3.text_input(f"Label", f"F{i+1}", key=f"l{i}"))
            colors.append(c4.selectbox(f"Color", list(COLOR_OPTIONS.keys()), key=f"c{i}"))
            show_components.append(st.checkbox("Show Components", key=f"comp{i}"))

    if st.button("Generate"):
        fig = draw_fbd(forces, directions, labels, [COLOR_OPTIONS[c] for c in colors], "FBD", False, simple_mode, False, [], "Right", shape, 0, uploaded_file, font_choice, arrow_thickness, 1.1, arrowhead_size, "Above", inclined_plane, show_net_force, show_components)
        buf = BytesIO()
        fig.savefig(buf, format="png", transparent=True)
        st.image(buf)
        st.download_button("Download", buf, "fbd.png", "image/png")

if __name__ == "__main__": main()
