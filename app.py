# File: fbd_creator_app_v16.py

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
def draw_fbd(forces, directions, labels, colors, title, caption):
    """
    Draw the Free Body Diagram with dynamically sized and visible arrowheads.

    Args:
        forces: List of force magnitudes.
        directions: List of (dx, dy) directions.
        labels: List of labels for each force.
        colors: List of colors for each force.
        title: Title of the diagram.
        caption: Caption of the diagram.
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Remove axes for a clean diagram

    # Determine scaling factor
    known_forces = [f for f in forces if f is not None]
    min_force = min(known_forces) if known_forces else 1
    scale_factor = 2.0 / (max(known_forces) if known_forces else 1)

    # Object size scaled to half the smallest known vector
    object_size = min_force / 2.0 if known_forces else 0.5
    rect_size = object_size * 1.5

    # Draw rectangle at the center
    ax.add_patch(plt.Rectangle((-rect_size/2, -rect_size/2), rect_size, rect_size,
                               fill=False, linewidth=4, color="black"))

    # Force directions map
    direction_map = {"Up": (0, 1), "Down": (0, -1), "Left": (-1, 0), "Right": (1, 0)}

    # Arrowhead size adjustments (dynamic scaling)
    head_width = 0.1 * scale_factor
    head_length = 0.2 * scale_factor

    # Draw forces
    for i in range(len(forces)):
        force = forces[i]
        if force is None:
            continue

        # Scale the force
        scaled_force = force * scale_factor
        dx = scaled_force * direction_map[directions[i]][0]
        dy = scaled_force * direction_map[directions[i]][1]

        # Offset the force vector to start outside the rectangle
        rect_offset = rect_size / 2
        start_x = rect_offset * direction_map[directions[i]][0]
        start_y = rect_offset * direction_map[directions[i]][1]

        # Draw vector arrow with dynamically sized arrowheads
        ax.arrow(start_x, start_y, dx, dy, head_width=head_width, head_length=head_length,
                 fc=colors[i], ec=colors[i], linewidth=2)

        # Adjust label position dynamically
        label_x = start_x + dx
        label_y = start_y + dy

        if directions[i] == "Up":
            label_x += 0.1  # Shift slightly right
            label_y += 0.2
        elif directions[i] == "Down":
            label_x += 0.1  # Shift slightly right
            label_y -= 0.3
        elif directions[i] == "Right":
            label_y += 0.2  # Shift upward
        elif directions[i] == "Left":
            label_y -= 0.2  # Shift downward

        label_with_magnitude = f"{labels[i]} ({force}N)"
        plt.text(label_x, label_y, label_with_magnitude, fontsize=12, fontweight='bold', color=colors[i], ha='center')

    # Add title and caption
    plt.title(title, fontsize=14, fontweight='bold')
    plt.figtext(0.5, 0.01, caption, ha="center", fontsize=10, color='gray')

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    plt.close(fig)
    return fig

# Streamlit UI
def main():
    st.title("Free Body Diagram Creator")
    st.write("Create a Free Body Diagram with visible, dynamically sized arrowheads and clear labels.")

    # Title and caption input
    title = st.text_input("Enter diagram title:", "Free Body Diagram")
    caption = st.text_input("Enter diagram caption:", "Generated using the Free Body Diagram Creator.")

    # Number of forces
    num_forces = st.number_input("Number of forces:", min_value=1, max_value=10, value=4, step=1)

    # User inputs for forces
    st.subheader("Input Forces")
    forces = []
    directions = []
    labels = []
    colors = []

    direction_options = ["Up", "Down", "Left", "Right"]

    for i in range(num_forces):
        st.write(f"### Force {i+1}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            magnitude = st.text_input("Magnitude (N):", key=f"force_{i}")
            magnitude = float(magnitude) if magnitude.strip().replace('.', '', 1).isdigit() else None
        with col2:
            direction = st.selectbox("Direction:", direction_options, key=f"dir_{i}")
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
        fig = draw_fbd(forces, directions, labels, colors, title, caption)
        st.pyplot(fig)

        # Export as SVG
        buf = BytesIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="Download FBD as SVG",
            data=buf,
            file_name="free_body_diagram.svg",
            mime="image/svg+xml"
        )

if __name__ == "__main__":
    main()
