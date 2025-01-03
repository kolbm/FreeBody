import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image

# Basic color options
COLOR_OPTIONS = {
    "Red": "#FF0000",
    "Blue": "#0000FF",
    "Green": "#00FF00",
    "Orange": "#FFA500",
    "Purple": "#800080",
    "Cyan": "#00FFFF",
    "Magenta": "#FF00FF",
    "Black": "#000000",
    "Gray": "#808080",
    "Yellow": "#FFFF00"
}

# Function to draw Free Body Diagram
def draw_fbd(forces, directions, labels, colors, title, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction, uploaded_image):
    fig, ax = plt.subplots(figsize=(10, 10))  # Increased figure size to prevent Streamlit crashes
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Remove axes for a clean diagram

    # Upload image or use default rectangle
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        ax.imshow(img, extent=[-1, 1, -1, 1], aspect='auto')
    else:
        rect_size = 1.0
        ax.add_patch(plt.Rectangle((-rect_size / 2, -rect_size / 2), rect_size, rect_size,
                                   fill=False, linewidth=4, color="black"))

    # Direction mapping
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}

    # Draw forces and collect points
    points = []
    for i in range(len(forces)):
        force = forces[i] if not simple_mode else 1
        if force is None or force <= 0:
            continue

        if angled_mode:
            angle = np.radians(angles[i])
            dx = force * np.cos(angle)
            dy = force * np.sin(angle)
        else:
            dx, dy = [component * force for component in direction_map[directions[i]]]

        # Draw vector arrow
        ax.arrow(0, 0, dx, dy, head_width=0.15, head_length=0.2, fc=colors[i], ec=colors[i], linewidth=2)

        # Store points for least dense region calculation
        points.append((dx, dy))

        # Label positioning to prevent overlap
        label_offset_x = 0.4 if dx >= 0 else -0.4
        label_offset_y = 0.4 if dy >= 0 else -0.4
        label_x = dx + label_offset_x
        label_y = dy + label_offset_y
        label_with_magnitude = f"{labels[i]}" if simple_mode else f"{labels[i]} ({force}N)"
        ax.text(label_x, label_y, label_with_magnitude, fontsize=14, fontweight='bold', color=colors[i], ha='center')

    # Determine least dense region for motion arrow
    grid_x = np.linspace(-1.5, 1.5, 10)
    grid_y = np.linspace(-1.5, 1.5, 10)
    min_density = float('inf')
    best_position = (0, 0)

    for gx in grid_x:
        for gy in grid_y:
            density = sum(np.exp(-((gx - px)**2 + (gy - py)**2)) for px, py in points)
            if density < min_density:
                min_density = density
                best_position = (gx, gy)

    # Add motion arrow if enabled
    if motion_arrow:
        motion_dx, motion_dy = direction_map[motion_direction]
        arrow_length = 0.5
        ax.arrow(best_position[0], best_position[1], arrow_length * motion_dx, arrow_length * motion_dy,
                 head_width=0.2, head_length=0.2, fc="black", ec="black", linewidth=2)
        ax.text(best_position[0] + 0.2 * motion_dx, best_position[1] + 0.2 * motion_dy, "Direction of Motion",
                fontsize=12, fontweight='bold', ha='center', color="black")

    # Add title and caption
    plt.title(title, fontsize=16, fontweight='bold')
    plt.figtext(0.5, 0.01, caption, ha="center", fontsize=10, color='gray')

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    plt.close(fig)
    return fig

# Streamlit UI
def main():
    # App Title with Image
    st.image("https://raw.githubusercontent.com/kolbm/FreeBody/63540a484dda1329695026d8a40369414f8df440/title.svg", use_container_width=True)
    st.title("Kolb's Free Body")
    st.write("Create a Free Body Diagram with visible, dynamically sized arrowheads and clear labels.")

    # Title and caption input
    title = st.text_input("Enter diagram title:", "Free Body Diagram")
    caption = st.text_input("Enter diagram caption:", "Generated using Kolb's Free Body.")

    # Upload image option
    uploaded_image = st.file_uploader("Upload an image to replace the square (optional):", type=["png", "jpg", "jpeg"])

    # Number of forces
    num_forces = st.number_input("Number of forces:", min_value=1, max_value=10, value=4, step=1)

    # Modes
    simple_mode = st.checkbox("Simple Mode (Equal-sized arrows)", value=True)
    angled_mode = st.checkbox("Angled Mode (Input angles for forces)", value=False)
    motion_arrow = st.checkbox("Show direction of motion arrow", value=True)
    motion_direction = st.selectbox("Direction of motion:", ["Up", "Down", "Left", "Right"], index=0)

    # User inputs for forces
    st.subheader("Input Forces")
    forces = []
    directions = []
    labels = []
    colors = []
    angles = []

    direction_options = ["Up", "Down", "Left", "Right"]

    for i in range(num_forces):
        st.write(f"### Force {i+1}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if not simple_mode:
                magnitude = st.text_input("Magnitude (N):", key=f"force_{i}")
                magnitude = float(magnitude) if magnitude.strip().replace('.', '', 1).isdigit() else None
            else:
                magnitude = 1  # Default for simple mode

        with col2:
            if not angled_mode:
                direction = st.selectbox("Direction:", direction_options, key=f"dir_{i}")
                angles.append(0)  # Placeholder when using direction dropdown
            else:
                direction = ""  # Empty if using angle
                angle = st.number_input("Angle (degrees):", value=0, key=f"angle_{i}")
                angles.append(angle)

        with col3:
            label = st.text_input("Custom Label:", value=f"Force {i+1}", key=f"label_{i}")
        with col4:
            color = st.selectbox("Pick arrow color:", list(COLOR_OPTIONS.keys()), key=f"color_{i}")

        forces.append(magnitude)
        directions.append(direction)
        labels.append(label)
        colors.append(COLOR_OPTIONS[color])

    # Generate the Free Body Diagram
    if st.button("Generate Diagram"):
        fig = draw_fbd(forces, directions, labels, colors, title, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction, uploaded_image)
        st.pyplot(fig)

        # Export as SVG
        buf_svg = BytesIO()
        fig.savefig(buf_svg, format="svg", bbox_inches="tight")
        buf_svg.seek(0)
        st.download_button(
            label="Download FBD as SVG",
            data=buf_svg,
            file_name="kolbs_free_body.svg",
            mime="image/svg+xml"
        )

        # Export as PNG
        buf_png = BytesIO()
        fig.savefig(buf_png, format="png", bbox_inches="tight")
        buf_png.seek(0)
        st.download_button(
            label="Download FBD as PNG",
            data=buf_png,
            file_name="kolbs_free_body.png",
            mime="image/png"
        )

        # Export as JPG
        buf_jpg = BytesIO()
        fig.savefig(buf_jpg, format="jpeg", bbox_inches="tight")
        buf_jpg.seek(0)
        st.download_button(
            label="Download FBD as JPG",
            data=buf_jpg,
            file_name="kolbs_free_body.jpg",
            mime="image/jpeg"
        )

if __name__ == "__main__":
    main()
