import streamlit as st
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


st.set_page_config(page_title="RC Beam Design (ACI 318)", layout="wide")

# ======================================================
# ACI CALCULATIONS
# ======================================================

def max_moment(beam, w, L):
    return {
        "Simply Supported": w * L**2 / 8,
        "Fixed End": w * L**2 / 12,
        "Cantilever": w * L**2 / 2,
        "Overhang": w * L**2 / 10
    }.get(beam, 0)

def flexural_design(beam, w, L, b, d, fc, fy):
    Mu = max_moment(beam, w, L)
    phi = 0.9
    As = (Mu * 1e6) / (phi * fy * d * 0.9)
    return round(Mu, 2), round(As, 2)

def shear_design(w, L, b, d, fc):
    Vu = w * L / 2
    phi = 0.75
    Vc = 0.17 * math.sqrt(fc) * b * d / 1000
    status = "SAFE" if phi * Vc >= Vu else "STIRRUPS REQUIRED"
    return round(Vu, 2), round(phi * Vc, 2), status

# ======================================================
# DRAW BEAM (SUPPORTS ATTACHED)
# ======================================================
def draw_beam(beam):
    fig, ax = plt.subplots(figsize=(7, 2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)

    beam_y = 2
    support_y = 1.75

    # 🔴 CONTROL VALUES
    support_length = 0.22   # horizontal kam
    support_height = 1.2    # ⬆️ vertical aur zyada

    # Beam
    ax.plot([1, 9], [beam_y, beam_y], linewidth=8, zorder=2)

    if beam == "Simply Supported":
        ax.plot(1, support_y, marker="^", markersize=12, zorder=3)
        ax.plot(9, support_y, marker="o", markersize=10, zorder=3)

    elif beam == "Fixed End":
        # LEFT vertical fixed support
        ax.add_patch(plt.Rectangle(
            (1 - support_length, beam_y - support_height / 2),
            support_length,
            support_height,
            color="black",
            zorder=5
        ))

        # RIGHT vertical fixed support
        ax.add_patch(plt.Rectangle(
            (9, beam_y - support_height / 2),
            support_length,
            support_height,
            color="black",
            zorder=5
        ))

    elif beam == "Cantilever":
        # LEFT vertical fixed support
        ax.add_patch(plt.Rectangle(
            (1 - support_length, beam_y - support_height / 2),
            support_length,
            support_height,
            color="black",
            zorder=5
        ))

    elif beam == "Overhang":
        ax.plot(2.5, support_y, marker="^", markersize=12, zorder=3)
        ax.plot(9, support_y, marker="o", markersize=10, zorder=3)

    ax.text(5, 2.6, f"{beam} Beam", ha="center", fontsize=11)
    ax.axis("off")
    return fig

# ======================================================
# DRAW SFD & BMD
# ======================================================

def draw_diagrams(beam, w, L):
    x = np.linspace(0, L, 100)

    if beam == "Simply Supported":
        V = w * (L/2 - x)
        M = w * x * (L - x) / 2
    elif beam == "Cantilever":
        V = w * (L - x)
        M = w * (L - x)**2 / 2
    elif beam == "Fixed End":
        V = w * (L/2 - x)
        M = w * x * (L - x) / 12
    else:
        V = w * (L/2 - x)
        M = w * x * (L - x) / 10

    fig = plt.figure(figsize=(7, 5))
    fig.subplots_adjust(left=0.22)

    ax1 = fig.add_axes([0.1, 0.58, 0.85, 0.32])
    ax1.plot(x, V)
    ax1.set_title("Shear Force Diagram")
    ax1.set_ylabel("Shear (kN)")
    ax1.grid(True)

    ax2 = fig.add_axes([0.1, 0.10, 0.85, 0.32])
    ax2.plot(x, M)
    ax2.set_title("Bending Moment Diagram")
    ax2.set_xlabel("Length (m)")
    ax2.set_ylabel("Moment (kN·m)")
    ax2.grid(True)

    return fig

# ======================================================
# STREAMLIT UI
# ======================================================

st.title("RC Beam Design – ACI 318")

col1, col2 = st.columns([1, 2])

with col1:
    beam = st.selectbox(
        "Beam Type",
        ["Simply Supported", "Fixed End", "Cantilever", "Overhang"]
    )

    w = st.number_input("Load w (kN/m)", value=30.0)
    L = st.number_input("Span L (m)", value=20.0)
    b = st.number_input("Width b (mm)", value=300.0)
    d = st.number_input("Depth d (mm)", value=500.0)
    fc = st.number_input("Concrete Strength f'c (MPa)", value=30.0)
    fy = st.number_input("Steel Yield Strength fy (MPa)", value=420.0)

    calc = st.button("Calculate Design")

    if calc:
        Mu, As = flexural_design(beam, w, L, b, d, fc, fy)
        Vu, Vc, status = shear_design(w, L, b, d, fc)

        st.subheader("Design Results")
        st.text(
            f"Flexural Design\n"
            f"Mu = {Mu} kN-m\n"
            f"As = {As} mm²\n\n"
            f"Shear Design\n"
            f"Vu = {Vu} kN\n"
            f"φVc = {Vc} kN\n"
            f"Status: {status}"
        )

with col2:
    if calc:
        st.subheader("Beam Diagram")
        st.pyplot(draw_beam(beam))

        st.subheader("Shear Force & Bending Moment Diagrams")
        st.pyplot(draw_diagrams(beam, w, L))
