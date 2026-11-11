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
TITLE_IMAGE_URL = "https://github.com/kolbm/FreeBody/blob/main/title.jpg?raw=true"

def draw_fbd(forces, directions, labels, colors, advanced_mode, inclined_angle, shape, rect_rotation, uploaded_image, font_choice, arrow_thickness, arrowhead_size, show_net_force, net_color, show_net_comp, show_net_val, show_components, angle_modes, custom_angles):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    rad = np.radians(inclined_angle) if advanced_mode else 0
    if advanced_mode and inclined_angle > 0:
        ax.plot([-5, 5], [np.tan(rad)*-5, np.tan(rad)*5], color='brown', linewidth=3)
        ax.fill_between([-5, 5], -6, [np.tan(rad)*-5, np.tan(rad)*5], color='sandybrown', alpha=0.3)
        ax.text(3, np.tan(rad)*3 + 0.5, f"Ramp Angle: {inclined_angle}°", fontsize=10, color='brown')

    transform = plt.matplotlib.transforms.Affine2D().rotate_deg(inclined_angle if advanced_mode else 0)
    
    if uploaded_image:
        img = Image.open(uploaded_image)
        ax.imshow(img, extent=[-1, 1, -1, 1], transform=transform + ax.transData)
    else:
        if shape == "Rectangle": patch = patches.Rectangle((-1, -0.5), 2, 1, color='gray', fill=True, transform=transform + ax.transData)
        elif shape == "Square": patch = patches.Rectangle((-1, -1), 2, 2, color='gray', fill=True, transform=transform + ax.transData)
        elif shape == "Circle": patch = patches.Circle((0, 0), 1, color='gray', fill=True, transform=transform + ax.transData)
        else: patch = patches.Polygon([(-1, -1), (1, -1), (0, 1)], color='gray', fill=True, transform=transform + ax.transData)
        ax.add_patch(patch)

    max_val = max(forces) if forces else 1
    scale = 2.5 / max_val if max_val > 0 else 1
    net_dx, net_dy = 0, 0
    for i in range(len(forces)):
        f = forces[i] * scale
        if advanced_mode:
            if angle_modes[i] == "Up the ramp": a = rad
            elif angle_modes[i] == "Down the ramp": a = rad + np.pi
            elif angle_modes[i] == "Perpendicular to ramp": a = rad + np.pi/2
            else: a = np.radians(custom_angles[i])
            dx, dy = f * np.cos(a), f * np.sin(a)
        else:
            direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
            dx, dy = [c * f for c in direction_map[directions[i]]]
        
        net_dx += dx; net_dy += dy
        ax.arrow(0, 0, dx, dy, head_width=arrowhead_size, head_length=arrowhead_size*1.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        ax.text(dx, dy, labels[i], fontsize=12, fontfamily=font_choice)

    if show_net_force:
        ax.arrow(0, 0, net_dx, net_dy, head_width=arrowhead_size*1.5, head_length=arrowhead_size*2, fc=net_color, ec=net_color, linewidth=arrow_thickness+1, linestyle=':')

    plt.figtext(0.5, 0.05, "Generated using the Free Body Diagram Generator: freebody.streamlit.app", ha="center", fontsize=8, color='gray')
    if max_val * scale > 3: plt.figtext(0.5, 0.02, "Note: Arrows are scaled for visibility.", ha="center", fontsize=8, color='red')
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    plt.tight_layout()
    return fig

def main():
    st.sidebar.image(TITLE_IMAGE_URL, use_container_width=True)
    mode = st.radio("Mode", ["Regular", "Advanced"])
    inclined_angle = st.slider("Inclined Plane Angle", 0, 45, 0) if mode == "Advanced" else 0
    num_forces = st.number_input("Number of Forces:", 1, 10, 2)
    shape = st.selectbox("Object Shape", SHAPE_OPTIONS)
    uploaded_file = st.file_uploader("Insert Picture", type=["png", "jpg", "jpeg"])
    
    st.sidebar.header("Settings")
    arrow_thickness = st.sidebar.slider("Arrow Line Thickness", 1.0, 5.0, 2.0)
    arrowhead_size = st.sidebar.slider("Arrowhead Size", 0.1, 1.0, 0.3)
    font_choice = st.sidebar.selectbox("Font Style", FONT_OPTIONS)
    show_net_force = st.sidebar.checkbox("Show Net Force")
    net_color = COLOR_OPTIONS[st.sidebar.selectbox("Net Force Color", list(COLOR_OPTIONS.keys()))]
    
    forces, directions, labels, colors, show_components, angle_modes, custom_angles = [], [], [], [], [], [], []
    for i in range(num_forces):
        with st.expander(f"Force {i+1}"):
            c1, c2, c3, c4 = st.columns(4)
            forces.append(c1.number_input("Magnitude", value=5, key=f"m{i}"))
            if mode == "Advanced":
                angle_modes.append(c2.selectbox("Angle Mode", ["Custom Angle", "Up the ramp", "Down the ramp", "Perpendicular to ramp"], key=f"am{i}"))
                custom_angles.append(c3.number_input("Angle", value=0, key=f"a{i}") if angle_modes[-1] == "Custom Angle" else 0)
                show_components.append(c4.checkbox("Components", key=f"comp{i}"))
            else:
                directions.append(c2.selectbox("Direction", DIRECTION_OPTIONS, key=f"d{i}"))
                angle_modes.append("Custom Angle"); custom_angles.append(0); show_components.append(False)
            labels.append(c3.text_input("Label", f"F{i+1}", key=f"l{i}"))
            colors.append(COLOR_OPTIONS[st.selectbox("Color", list(COLOR_OPTIONS.keys()), key=f"c{i}")])

    if st.button("Generate"):
        fig = draw_fbd(forces, directions, labels, colors, mode=="Advanced", inclined_angle, shape, 0, uploaded_file, font_choice, arrow_thickness, arrowhead_size, show_net_force, net_color, False, False, show_components, angle_modes, custom_angles)
        buf = BytesIO()
        fig.savefig(buf, format="png", transparent=True)
        st.image(buf)
        st.download_button("Download", buf, "fbd.png", "image/png")

if __name__ == "__main__": main()
