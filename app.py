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
FONT_OPTIONS = ["sans-serif", "serif", "monospace", "fantasy", "cursive"]

TITLE_IMAGE_URL = "https://github.com/kolbm/FreeBody/blob/main/title.jpg?raw=true"

def display_title_image():
    try:
        response = requests.get(TITLE_IMAGE_URL)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        st.image(image, use_container_width=True)
    except Exception as e:
        st.warning("Could not load title image. Using text title instead.")
        st.title("Free Body Diagram Generator")

def draw_fbd(forces, directions, labels, colors, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction, rect_rotation, uploaded_image, font_choice, arrow_thickness, arrow_offset):
    max_force = max(forces) if forces else 1
    rect_size = max(max_force * 0.5, 1)
    
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    if uploaded_image:
        img = Image.open(uploaded_image)
        ax.imshow(img, extent=[-rect_size/2, rect_size/2, -rect_size/2, rect_size/2])
    
    rect = patches.Rectangle((-rect_size / 2, -rect_size / 2), rect_size, rect_size, 
                             fill=False, linewidth=2, color="black", 
                             angle=rect_rotation, rotation_point='center')
    ax.add_patch(rect)

    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}

    for i in range(len(forces)):
        force = forces[i] if not simple_mode else 1
        if force is None or force <= 0: continue
        if angled_mode:
            angle = np.radians(angles[i])
            dx = force * 0.5 * np.cos(angle)
            dy = force * 0.5 * np.sin(angle)
        else:
            dx, dy = [component * force * 0.5 for component in direction_map[directions[i]]]
        ax.arrow(0, 0, dx, dy, head_width=0.4, head_length=0.5, fc=colors[i], ec=colors[i], linewidth=arrow_thickness)
        label_with_magnitude = f"{labels[i]}" if simple_mode else f"{labels[i]} ({force}N)"
        ax.text(dx * arrow_offset, dy * arrow_offset, label_with_magnitude, fontsize=12, fontweight='bold', ha='center', va='center', fontfamily=font_choice)

    plt.figtext(0.5, 0.01, caption, ha="center", fontsize=10, color='gray')
    ax.set_xlim(-rect_size * 3, rect_size * 3)
    ax.set_ylim(-rect_size * 3, rect_size * 3)
    plt.tight_layout()
    plt.close(fig)
    return fig

def main():
    display_title_image()
    caption = st.text_input("Enter diagram caption:", "Generated using Free Body Diagram Generator.")
    num_forces = st.number_input("Number of Forces:", min_value=1, max_value=10, value=4)
    st.sidebar.header("Customization")
    rect_rotation = st.sidebar.slider("Rectangle Rotation (degrees)", 0, 360, 0)
    font_choice = st.sidebar.selectbox("Font Choice", FONT_OPTIONS)
    arrow_thickness = st.sidebar.slider("Arrow Thickness", 1.0, 5.0, 2.0)
    arrow_offset = st.sidebar.slider("Arrow Label Offset", 1.0, 2.0, 1.2)
    uploaded_file = st.sidebar.file_uploader("Insert your own picture", type=["png", "jpg", "jpeg"])
    simple_mode = st.checkbox("Simple Mode (Equal-sized arrows)", value=True)
    angled_mode = st.checkbox("Angled Mode (Input angles for forces)", value=False)
    
    forces, directions, labels, colors, angles = [], [], [], [], []
    for i in range(num_forces):
        st.write(f"### Force {i+1}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            magnitude = st.number_input(f"Magnitude {i+1}:", min_value=0, value=5) if not simple_mode else 1
        with col2:
            if not angled_mode:
                direction = st.selectbox(f"Direction {i+1}", DIRECTION_OPTIONS, key=f"dir_{i}")
                angles.append(0)
            else:
                direction = ""
                angles.append(st.number_input(f"Angle {i+1} (deg):", value=0))
        with col3:
            label = st.text_input(f"Label {i+1}", f"Force {i+1}")
        with col4:
            color = st.selectbox(f"Color {i+1}", list(COLOR_OPTIONS.keys()), key=f"color_{i}")
        forces.append(magnitude); directions.append(direction); labels.append(label); colors.append(COLOR_OPTIONS[color])

    if st.button("Generate Diagram"):
        fig = draw_fbd(forces, directions, labels, colors, caption, False, simple_mode, angled_mode, angles, "", rect_rotation, uploaded_file, font_choice, arrow_thickness, arrow_offset)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        st.image(buf, use_container_width=True)
        st.download_button("Download as PNG", data=buf, file_name="free_body_diagram.png", mime="image/png")

if __name__ == "__main__":
    main()
