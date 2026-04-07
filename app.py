import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

# ==========================
# Page Configuration
# ==========================
st.set_page_config(layout="wide", page_title="Defensive Actions Map")

st.title("Defensive Actions Interception Map - Multiple Matches")
st.caption("Click on the icons on the pitch to view event details.")

# ==========================
# Data Setup
# ==========================
matches_data = {
    "Vs Connecticut": [
        # Duelos Vencidos
        ("DEFENSIVE DUEL WON", 80.28, 5.26, None),
        ("DEFENSIVE DUEL WON", 74.13, 19.22, None),
        ("DEFENSIVE DUEL WON", 68.31, 25.21, None),
        ("DEFENSIVE DUEL WON", 29.75, 29.69, None),
        ("DEFENSIVE DUEL WON", 33.74, 65.43, None),
        # Duelos Perdidos
        ("DEFENSIVE DUEL LOST", 65.49, 22.71, None),
        ("DEFENSIVE DUEL LOST", 3.48, 72.42, None),
        # Intercepts + Recoveries
        ("INTERCEPTION", 85.27, 34.85, None),
        ("INTERCEPTION", 65.32, 27.37, None), 
        ("INTERCEPTION", 85.43, 57.79, None), 
   
    ],
    "Vs Nashville": [
        # Duelos Vencidos
        ("DEFENSIVE DUEL WON", 35.56, 12.07, None),
        ("DEFENSIVE DUEL WON", 27.09, 25.87, None),
        ("DEFENSIVE DUEL WON", 37.89, 44.82, None),
        ("DEFENSIVE DUEL WON", 19.11, 57.29, None),
        ("DEFENSIVE DUEL WON", 33.57, 64.77, None),
        ("DEFENSIVE DUEL WON", 37.56, 73.41, None),
        ("DEFENSIVE DUEL WON", 62.16, 57.12, None),
        ("DEFENSIVE DUEL WON", 84.10, 56.29, None),
        # Duelos Perdidos
        ("DEFENSIVE DUEL LOST", 20.10, 24.54, None),
        ("DEFENSIVE DUEL LOST", 35.40, 38.17, None),
        ("DEFENSIVE DUEL LOST", 38.89, 45.82, None),
        ("DEFENSIVE DUEL LOST", 28.58, 53.46, None),
        ("DEFENSIVE DUEL LOST", 55.51, 72.91, None),
        ("DEFENSIVE DUEL LOST", 65.15, 64.44, None),
        ("DEFENSIVE DUEL LOST", 87.93, 54.63, None),
        # Intercepts + Recoveries
        ("INTERCEPTION", 35.73, 10.24, None),
        ("INTERCEPTION", 54.85, 11.74, None), 
        ("INTERCEPTION", 84.10, 28.53, None),
        ("INTERCEPTION", 68.48, 58.12, None),
        ("INTERCEPTION", 79.45, 62.61, None), 
        ("INTERCEPTION", 76.62, 67.10, None), 
    ],
    "Vs Seongnam": [
        # Duelo Perdido
        ("DEFENSIVE DUEL LOST", 73.80, 21.71, None),
        # Intercept
        ("INTERCEPTION", 38.06, 30.36, None),
    ],
    "Vs Red Bull": [
        # Duelos Vencidos
        ("DEFENSIVE DUEL WON", 33.87, 59.39, None),
        ("DEFENSIVE DUEL WON", 37.58, 67.14, None),
        # Duelos Perdidos
        ("DEFENSIVE DUEL LOST", 66.32, 60.28, None),
        # Interceptações + Recoveries
        ("INTERCEPTION", 34.90, 34.02, None),
        ("INTERCEPTION", 68.15, 54.30, None),
    ],
}

# Create DataFrames for each match and combined
dfs_by_match = {}
for match_name, events in matches_data.items():
    dfs_by_match[match_name] = pd.DataFrame(events, columns=["type", "x", "y", "video"])

# All games combined
df_all = pd.concat(dfs_by_match.values(), ignore_index=True)
full_data = {"All games": df_all}
full_data.update(dfs_by_match)


def get_style(event_type, has_video):
    """Returns marker, color (rgba), size, and linewidth based on event type"""
    event_type = event_type.upper()

    # 1. DEFENSIVE DUELS
    if "DEFENSIVE DUEL" in event_type:
        if "WON" in event_type:
            return 's', (0.0, 0.75, 0.2, 0.95), 130, 0.5
        if "LOST" in event_type:
            alpha = 0.95 if has_video else 0.85
            return 'D', (0.85, 0.1, 0.1, alpha), 130, 2.5

    # 2. INTERCEPTION - Blue circle
    if "INTERCEPTION" in event_type:
        return 'o', (0.2, 0.6, 0.95, 0.95), 130, 0.5

    # 3. BLOCK - Purple pentagon
    if "BLOCK" in event_type:
        return 'P', (0.7, 0.3, 0.9, 0.95), 130, 0.5

    # 4. CLEARANCE - Orange triangle
    if "CLEARANCE" in event_type:
        return '^', (1.0, 0.65, 0.0, 0.95), 130, 0.5

    # Default
    return 'o', (0.5, 0.5, 0.5, 0.8), 90, 0.5


def compute_stats(df: pd.DataFrame) -> dict:
    """Compute defensive duel, interception, block and clearance statistics"""
    # Defensive duels
    is_def_duel = df['type'].str.contains('DEFENSIVE DUEL', case=False)
    def_duels = df[is_def_duel]
    def_total = len(def_duels)
    def_wins = len(def_duels[def_duels['type'].str.contains('WON', case=False)])
    def_losses = len(def_duels[def_duels['type'].str.contains('LOST', case=False)])
    def_rate = (def_wins / def_total * 100) if def_total > 0 else 0

    # Interceptions
    intercepts = len(df[df['type'].str.contains('INTERCEPTION', case=False)])

    # Blocks
    blocks = len(df[df['type'].str.contains('BLOCK', case=False)])

    # Clearances
    clearances = len(df[df['type'].str.contains('CLEARANCE', case=False)])

    return {
        "def_total": def_total,
        "def_wins": def_wins,
        "def_losses": def_losses,
        "def_rate": def_rate,
        "intercepts": intercepts,
        "blocks": blocks,
        "clearances": clearances,
    }


# ==========================
# Sidebar Configuration
# ==========================
st.sidebar.header("📋 Filter Configuration")
selected_match = st.sidebar.radio("Select a match", list(full_data.keys()), index=0)

st.sidebar.divider()

filter_event_type = st.sidebar.multiselect(
    "Event Type",
    ["Defensive Duels", "Interceptions", "Blocks", "Clearances"],
    default=["Defensive Duels", "Interceptions", "Blocks", "Clearances"]
)

st.sidebar.divider()
st.sidebar.caption("Match filtered by selected options above")

# Get selected data
df = full_data[selected_match].copy()

# Apply event type filter
all_types = ["Defensive Duels", "Interceptions", "Blocks", "Clearances"]
if not all(x in filter_event_type for x in all_types):
    mask = pd.Series([False] * len(df))
    if "Defensive Duels" in filter_event_type:
        mask |= df['type'].str.contains('DEFENSIVE DUEL', case=False)
    if "Interceptions" in filter_event_type:
        mask |= df['type'].str.contains('INTERCEPTION', case=False)
    if "Blocks" in filter_event_type:
        mask |= df['type'].str.contains('BLOCK', case=False)
    if "Clearances" in filter_event_type:
        mask |= df['type'].str.contains('CLEARANCE', case=False)
    df = df[mask]

# Compute stats always from full match data
stats = compute_stats(full_data[selected_match])

# ==========================
# Main Layout
# ==========================
col_map, col_vid = st.columns([1, 1])

with col_map:
    st.subheader("Interactive Pitch Map")
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f8f8f8', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(10, 7))

    for _, row in df.iterrows():
        has_vid = row["video"] is not None
        marker, color, size, lw = get_style(row["type"], has_vid)
        ec = 'black' if has_vid else 'none'
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color,
                      edgecolors=ec, linewidths=lw, ax=ax, zorder=3)

    # Attack Arrow
    ax.annotate('', xy=(70, 83), xytext=(50, 83),
        arrowprops=dict(arrowstyle='->', color='#4a4a4a', lw=1.5))
    ax.text(60, 86, "Attack Direction", ha='center', va='center',
        fontsize=9, color='#4a4a4a', fontweight='bold')

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', label='Defensive Duel Won',
               markerfacecolor=(0.0, 0.75, 0.2, 0.95), markersize=10, linestyle='None'),

        Line2D([0], [0], marker='D', color='w', label='Defensive Duel Lost',
               markerfacecolor=(0.85, 0.1, 0.1, 0.95), markersize=10, linestyle='None'),

        Line2D([0], [0], marker='o', color='w', label='Interception',
               markerfacecolor=(0.2, 0.6, 0.95, 0.95), markersize=10, linestyle='None'),

        Line2D([0], [0], marker='P', color='w', label='Block',
               markerfacecolor=(0.7, 0.3, 0.9, 0.95), markersize=10, linestyle='None'),

        Line2D([0], [0], marker='^', color='w', label='Clearance',
               markerfacecolor=(1.0, 0.65, 0.0, 0.95), markersize=10, linestyle='None'),
    ]

    legend = ax.legend(
        handles=legend_elements,
        loc='upper left',
        bbox_to_anchor=(0.01, 0.99),
        frameon=True,
        facecolor='white',
        edgecolor='#333333',
        fontsize='small',
        title="Match Events",
        title_fontsize='medium',
        labelspacing=1.2,
        borderpad=1.0,
        framealpha=0.95
    )

    legend.get_title().set_fontweight('bold')

    # Convert plot to image for coordinate tracking
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_obj = Image.open(buf)

    click = streamlit_image_coordinates(img_obj, width=700)

# ==========================
# Interaction Logic
# ==========================
selected_event = None

if click is not None:
    real_w, real_h = img_obj.size
    disp_w, disp_h = click["width"], click["height"]

    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)

    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)

    RADIUS = 5
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Event Details & Stats
# ==========================
with col_vid:
    st.subheader("Event Details")
    if selected_event is not None:
        event_type = selected_event['type']
        if "WON" in event_type.upper():
            st.success(f"**Selected Event:** {selected_event['type']}")
        elif "LOST" in event_type.upper():
            st.error(f"**Selected Event:** {selected_event['type']}")
        else:
            st.info(f"**Selected Event:** {selected_event['type']}")

        st.info(f"**Position:** X: {selected_event['x']:.2f}, Y: {selected_event['y']:.2f}")

        if selected_event["video"]:
            try:
                st.video(selected_event["video"])
            except:
                st.error(f"Video file not found: {selected_event['video']}")
        else:
            st.warning("No video footage available for this specific event.")
    else:
        st.info("Select a marker on the pitch to view event details.")

    st.divider()
    st.subheader("Performance Statistics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Defensive Duels",
        f"{stats['def_wins']}/{stats['def_total']}",
        f"{stats['def_rate']:.1f}% Won"
    )
    col2.metric("Interceptions", stats['intercepts'])
    col3.metric("Blocks", stats['blocks'])
    col4.metric("Clearances", stats['clearances'])
