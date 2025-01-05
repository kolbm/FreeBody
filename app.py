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
DIRECTION_OPTIONS = ["Up", "Down", "Left", "Right"]

# Function to draw Free Body Diagram
def draw_fbd(forces, directions, labels, colors, title, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)  # Consistent size and high DPI
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Clean layout without axes

    # Draw default rectangle representing the object
    rect_size = 1.5
    ax.add_patch(plt.Rectangle((-rect_size / 2, -rect_size / 2), rect_size, rect_size, fill=False, linewidth=2, color="black"))

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

        # Label positioning
        label_x = dx * 1.1
        label_y = dy * 1.1
        label_with_magnitude = f"{labels[i]}" if simple_mode else f"{labels[i]} ({force}N)"
        ax.text(label_x, label_y, label_with_magnitude, fontsize=12, fontweight='bold', color=colors[i], ha='center')

    # Add motion arrow if enabled
    if motion_arrow:
        motion_dx, motion_dy = direction_map[motion_direction]
        arrow_length = 0.5
        ax.arrow(0, 0, arrow_length * motion_dx, arrow_length * motion_dy, head_width=0.15, head_length=0.2, fc="black", ec="black", linewidth=2)
        ax.text(arrow_length * 1.2 * motion_dx, arrow_length * 1.2 * motion_dy, "Direction of Motion", fontsize=10, fontweight='bold', ha='center', color="black")

    # Add title and caption
    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.figtext(0.5, 0.01, caption, ha="center", fontsize=10, color='gray')

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    plt.tight_layout()
    plt.close(fig)
    return fig

# Streamlit UI
def main():
    st.title("Free Body Diagram Generator with Customization")

    # Title and caption input
    title = st.text_input("Enter diagram title:", "Free Body Diagram")
    caption = st.text_input("Enter diagram caption:", "Generated using Free Body Diagram Generator.")

    # Number of forces
    num_forces = st.number_input("Number of Forces:", min_value=1, max_value=10, value=4)

    # Modes
    simple_mode = st.checkbox("Simple Mode (Equal-sized arrows)", value=True)
    angled_mode = st.checkbox("Angled Mode (Input angles for forces)", value=False)
    motion_arrow = st.checkbox("Show direction of motion arrow", value=True)
    motion_direction = st.selectbox("Direction of motion:", DIRECTION_OPTIONS, index=0)

    # User inputs for forces
    forces = []
    directions = []
    labels = []
    colors = []
    angles = []

    default_directions = ["Up", "Right", "Left", "Down"]
    default_colors = ["Red", "Blue", "Green", "Orange"]

    for i in range(num_forces):
        st.write(f"### Force {i+1}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if not simple_mode:
                magnitude = st.number_input(f"Magnitude of Force {i+1} (N):", min_value=0, value=5)
            else:
                magnitude = 1  # Default for simple mode

        with col2:
            if not angled_mode:
                direction = st.selectbox(f"Direction of Force {i+1}", DIRECTION_OPTIONS, index=i % len(DIRECTION_OPTIONS), key=f"dir_{i}")
                angles.append(0)
            else:
                direction = ""  # Use angles for direction in angled mode
                angle = st.number_input(f"Angle for Force {i+1} (degrees):", value=0)
                angles.append(angle)

        with col3:
            label = st.text_input(f"Label for Force {i+1}", f"Force {i+1}")

        with col4:
            color = st.selectbox(f"Color for Force {i+1}", list(COLOR_OPTIONS.keys()), index=i % len(default_colors), key=f"color_{i}")

        forces.append(magnitude)
        directions.append(direction)
        labels.append(label)
        colors.append(COLOR_OPTIONS[color])

    if st.button("Generate Diagram"):
        fig = draw_fbd(forces, directions, labels, colors, title, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction)

        # Display the diagram
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        st.image(buf, caption="Free Body Diagram", use_container_width=True)

        # Download options
        st.download_button("Download as PNG", data=buf, file_name="free_body_diagram.png", mime="image/png")

if __name__ == "__main__":
    main()
