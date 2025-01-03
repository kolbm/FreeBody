import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

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
def draw_fbd(forces, directions, labels, colors, title, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction):
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Remove axes for a clean diagram

    # Scaling factor for forces
    scale_factor = 1.0 if simple_mode else 2.0 / max([f for f in forces if f is not None and f > 0], default=1)

    # Object size
    rect_size = 0.5
    ax.add_patch(plt.Rectangle((-rect_size/2, -rect_size/2), rect_size, rect_size,
                               fill=False, linewidth=4, color="black"))

    # Direction mapping
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}

    # Draw forces
    max_distance = 0  # Track the furthest distance for motion arrow placement
    farthest_direction = (0, 0)

    for i in range(len(forces)):
        force = forces[i] if not simple_mode else 1
        if force is None or force <= 0:
            continue

        if angled_mode:
            angle = np.radians(angles[i])
            dx = force * scale_factor * np.cos(angle)
            dy = force * scale_factor * np.sin(angle)
        else:
            dx, dy = [component * force * scale_factor for component in direction_map[directions[i]]]

        # Draw vector arrow
        ax.arrow(0, 0, dx, dy, head_width=0.1 * scale_factor, head_length=0.2 * scale_factor,
                 fc=colors[i], ec=colors[i], linewidth=2)

        # Track maximum distance for motion arrow placement
        distance = np.sqrt(dx**2 + dy**2)
        if distance > max_distance:
            max_distance = distance
            farthest_direction = (dx / distance, dy / distance)  # Unit vector of the farthest force

        # Adjust label position to prevent overlap
        label_offset_x = 0.3 if dx >= 0 else -0.3
        label_offset_y = 0.4 if dy >= 0 else -0.4
        label_x = dx + label_offset_x
        label_y = dy + label_offset_y
        label_with_magnitude = f"{labels[i]}" if simple_mode else f"{labels[i]} ({force}N)"
        plt.text(label_x, label_y, label_with_magnitude, fontsize=12, fontweight='bold', color=colors[i], ha='center')

    # Add motion arrow if enabled
    if motion_arrow:
        motion_dx, motion_dy = direction_map[motion_direction]

        # Place the motion arrow away from other forces, between the center and the edge in the farthest direction
        motion_arrow_x = 0.7 * farthest_direction[0]
        motion_arrow_y = 0.7 * farthest_direction[1]

        ax.arrow(motion_arrow_x, motion_arrow_y, 0.3 * farthest_direction[0], 0.3 * farthest_direction[1],
                 head_width=0.1, head_length=0.1, fc="black", ec="black", linewidth=2)

        plt.text(motion_arrow_x + 0.15, motion_arrow_y + 0.15, "Direction of Motion",
                 fontsize=10, fontweight='bold', ha='center', color="black")

    # Add title and caption
    plt.title(title, fontsize=14, fontweight='bold')
    plt.figtext(0.5, 0.01, caption, ha="center", fontsize=10, color='gray')

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
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
        fig = draw_fbd(forces, directions, labels, colors, title, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction)
        st.pyplot(fig)

        # Export as SVG
        buf = BytesIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="Download FBD as SVG",
            data=buf,
            file_name="kolbs_free_body.svg",
            mime="image/svg+xml"
        )

if __name__ == "__main__":
    main()
