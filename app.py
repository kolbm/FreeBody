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
    # Calculate the rectangle size based on the smallest arrow length
    max_force = max(forces) if forces else 1
    rect_size = max(max_force * 0.5, 1)  # Ensure minimum box size for readability
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Clean layout without axes

    # Draw rectangle representing the object
    ax.add_patch(plt.Rectangle((-rect_size / 2, -rect_size / 2), rect_size, rect_size, fill=False, linewidth=2, color="black"))

    # Direction mapping
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}

    # Draw forces and labels
    for i in range(len(forces)):
        force = forces[i] if not simple_mode else 1
        if force is None or force <= 0:
            continue

        if angled_mode:
            angle = np.radians(angles[i])
            dx = force * 0.5 * np.cos(angle)
            dy = force * 0.5 * np.sin(angle)
        else:
            dx, dy = [component * force * 0.5 for component in direction_map[directions[i]]]

        # Draw vector arrow with larger head for visibility
        ax.arrow(0, 0, dx, dy, head_width=0.4, head_length=0.5, fc=colors[i], ec=colors[i], linewidth=2)

        # Label with magnitude in parenthesis
        label_with_magnitude = f"{labels[i]} ({force}N)"

        # Label positioning outside the box
        offset = 1.2  # Offset factor to move labels outside the box
        if directions[i] == "Right":
            label_x = dx * offset
            label_y = dy
            rotation_angle = 270
        elif directions[i] == "Left":
            label_x = dx * offset
            label_y = dy
            rotation_angle = 90
        elif directions[i] == "Up":
            label_x = dx
            label_y = dy * offset
            rotation_angle = 0
        else:  # Down
            label_x = dx
            label_y = dy * offset
            rotation_angle = 0

        ax.text(label_x, label_y, label_with_magnitude, fontsize=12, fontweight='bold', color=colors[i], ha='center', va='center', rotation=rotation_angle)

    # Add motion arrow outside the box, same size as the largest force arrow
    if motion_arrow:
        motion_dx, motion_dy = direction_map[motion_direction]
        arrow_length = max_force * 0.5  # Same size as the largest force arrow
        motion_x = -rect_size * 1.8 if motion_dx == 0 else -rect_size * 1.5
        motion_y = -rect_size * 1.8 if motion_dy == 0 else -rect_size * 1.5

        ax.arrow(motion_x, motion_y, arrow_length * motion_dx, arrow_length * motion_dy, head_width=0.3, head_length=0.4, fc="black", ec="black", linewidth=2)

        # Label placement for direction of motion above the arrow
        label_x = motion_x + (arrow_length * motion_dx / 2)
        label_y = motion_y + (arrow_length * motion_dy / 2) + (0.5 if motion_dx != 0 else 0.7)

        rotation_angle = 0 if motion_direction in ["Left", "Right"] else 270

        ax.text(label_x, label_y, "Direction of Motion", fontsize=10, fontweight='bold', ha='center', va='bottom', color="black", rotation=rotation_angle)

    # Add title and caption
    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.figtext(0.5, 0.01, caption, ha="center", fontsize=10, color='gray')

    ax.set_xlim(-rect_size * 2.5, rect_size * 2.5)
    ax.set_ylim(-rect_size * 2.5, rect_size * 2.5)
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
            color = st.selectbox(f"Color for Force {i+1}", list(COLOR_OPTIONS.keys()), index=i % len(COLOR_OPTIONS), key=f"color_{i}")

        forces.append(magnitude)
        directions.append(direction)
        labels.append(label)
        colors.append(COLOR_OPTIONS[color])

    if st.button("Generate Diagram"):
        try:
            fig = draw_fbd(forces, directions, labels, colors, title, caption, motion_arrow, simple_mode, angled_mode, angles, motion_direction)

            # Display the diagram
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            st.image(buf, caption="Free Body Diagram", use_container_width=True)

            # Download options
            st.download_button("Download as PNG", data=buf, file_name="free_body_diagram.png", mime="image/png")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
