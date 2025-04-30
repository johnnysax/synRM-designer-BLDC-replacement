import streamlit as st
import numpy as np
import pandas as pd
from io import StringIO

# Set page configuration
st.set_page_config(
    page_title="SynRM Design Calculator",
    page_icon=":electric_plug:",
    layout="wide"
)

# Title and description
st.title("🛠️ SynRM Design Calculator")
st.markdown("""
Browse and calculate parameters for designing a synchronous reluctance motor (SynRM) to replace a BLDC motor. Adjust inputs in the sidebar to match your BLDC's characteristics (e.g., KV, impedance). Results update in real-time, and you can download them as a CSV for Excel.
""")

# Add spacing
st.markdown("")

# Sidebar for parameter inputs
st.sidebar.header("Input Parameters")
st.sidebar.markdown("Adjust these to match your BLDC motor specs.")

# Input widgets with realistic ranges and defaults
p = st.sidebar.number_input("Pole Pairs (p)", min_value=1, max_value=10, value=2, step=1)
L_d = st.sidebar.number_input("d-axis Inductance (L_d, H)", min_value=0.0, max_value=0.1, value=0.01, step=0.001, format="%.4f")
L_q = st.sidebar.number_input("q-axis Inductance (L_q, H)", min_value=0.0, max_value=0.1, value=0.002, step=0.001, format="%.4f")
I_d = st.sidebar.number_input("d-axis Current (I_d, A)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
I_q = st.sidebar.number_input("q-axis Current (I_q, A)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
N_t = st.sidebar.number_input("Turns per Coil (N_t)", min_value=1, max_value=100, value=36, step=1)
k_w = st.sidebar.number_input("Winding Factor (k_w)", min_value=0.0, max_value=1.0, value=0.933, step=0.001)
phi = st.sidebar.number_input("Flux per Pole (φ, Wb)", min_value=0.0, max_value=0.01, value=0.001, step=0.0001, format="%.4f")
rho = st.sidebar.number_input("Copper Resistivity (ρ, Ω·m)", min_value=0.0, max_value=1e-7, value=1.68e-8, step=1e-9, format="%.10f")
l_w = st.sidebar.number_input("Wire Length (l_w, m)", min_value=0.0, max_value=100.0, value=43.2, step=0.1)
A_w = st.sidebar.number_input("Wire Area (A_w, m²)", min_value=0.0, max_value=1e-5, value=0.52e-6, step=1e-8, format="%.10f")
N_s = st.sidebar.number_input("Number of Slots (N_s)", min_value=3, max_value=72, value=36, step=3)
m = st.sidebar.number_input("Number of Phases (m)", min_value=1, max_value=6, value=3, step=1)
k_d = st.sidebar.number_input("Distribution Factor (k_d)", min_value=0.0, max_value=1.0, value=0.966, step=0.001)
k_p = st.sidebar.number_input("Pitch Factor (k_p)", min_value=0.0, max_value=1.0, value=0.966, step=0.001)
I_ph = st.sidebar.number_input("Phase Current (I_ph, A)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
J = st.sidebar.number_input("Current Density (J, A/m²)", min_value=0.0, max_value=1e7, value=6e6, step=1e5)
N_c = st.sidebar.number_input("Coils per Phase (N_c)", min_value=1, max_value=50, value=12, step=1)
A_slot = st.sidebar.number_input("Slot Area (A_slot, m²)", min_value=0.0, max_value=1e-4, value=1e-5, step=1e-6, format="%.10f")
RPM = st.sidebar.number_input("Rotor Speed (RPM)", min_value=0, max_value=10000, value=3000, step=100)
mu = st.sidebar.number_input("Core Permeability (μ, H/m)", min_value=0.0, max_value=0.01, value=0.001256, step=0.0001, format="%.6f")
A = st.sidebar.number_input("Magnetic Path Area (A, m²)", min_value=0.0, max_value=0.001, value=0.0001, step=0.00001, format="%.6f")
l = st.sidebar.number_input("Magnetic Path Length (l, m)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)

# Equations section
st.header("Equations", divider="gray")
st.markdown("These equations govern the SynRM design. Adjust parameters to see updated results below.")

equations = [
    ("Torque", r"T = \frac{3}{2} p (L_d - L_q) I_d I_q", "Torque (Nm)"),
    ("Back-EMF Constant", r"K_e = \sqrt{2} N_t k_w \phi p", "Back-EMF constant (V/rad/s)"),
    ("KV", r"K_V = \frac{60}{2 \pi K_e}", "Velocity constant (RPM/V)"),
    ("Phase Resistance", r"R_ph = \frac{\rho l_w N_t}{A_w}", "Phase resistance (Ω)"),
    ("Phase Inductance", r"L_d, L_q \propto N_t^2 \frac{\mu A}{l}", "Inductance (H, approximate)"),
    ("Slots per Pole per Phase", r"q = \frac{N_s}{2 p m}", "Slots per pole per phase"),
    ("Winding Factor", r"k_w = k_d k_p", "Winding factor"),
    ("Wire Area", r"A_w = \frac{I_ph}{J}", "Wire area (m²)"),
    ("Slot Fill Factor", r"S_fill = \frac{N_t A_w N_c}{A_slot}", "Slot fill factor"),
    ("Electrical Frequency", r"f = \frac{p RPM}{60}", "Electrical frequency (Hz)")
]

for name, latex, desc in equations:
    st.subheader(name)
    st.markdown(f"$${latex}$$")
    st.write(f"**Description**: {desc}")

# Calculations section
st.header("Calculated Results", divider="gray")
st.markdown("Results update based on your parameter inputs.")

try:
    T = (3/2) * p * (L_d - L_q) * I_d * I_q
    K_e = np.sqrt(2) * N_t * k_w * phi * p
    K_V = 60 / (2 * np.pi * K_e) if K_e != 0 else float('inf')
    R_ph = (rho * l_w * N_t) / A_w if A_w != 0 else float('inf')
    L_approx = (N_t**2 * mu * A) / l if l != 0 else float('inf')  # Placeholder
    q = N_s / (2 * p * m) if (p * m) != 0 else float('inf')
    k_w_calc = k_d * k_p
    A_w_calc = I_ph / J if J != 0 else float('inf')
    S_fill = (N_t * A_w * N_c) / A_slot if A_slot != 0 else float('inf')
    f = (p * RPM) / 60

    # Display results
    results = {
        "Parameter": ["Torque", "Back-EMF Constant", "KV", "Phase Resistance", "Phase Inductance (approx)", 
                      "Slots per Pole per Phase", "Winding Factor", "Wire Area", "Slot Fill Factor", "Electrical Frequency"],
        "Value": [f"{T:.4f}", f"{K_e:.6f}", f"{K_V:.2f}", f"{R_ph:.4f}", f"{L_approx:.6f}", 
                  f"{q:.2f}", f"{k_w_calc:.4f}", f"{A_w_calc:.8f}", f"{S_fill:.4f}", f"{f:.2f}"],
        "Unit": ["Nm", "V/rad/s", "RPM/V", "Ω", "H", "-", "-", "m²", "-", "Hz"]
    }
    results_df = pd.DataFrame(results)
    st.table(results_df)

    # Download results as CSV
    csv = results_df.to_csv(index=False)
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="SynRM_Results.csv",
        mime="text/csv"
    )
except Exception as e:
    st.error(f"Calculation error: {e}. Check for zero or invalid inputs.")

# Variable table
st.header("Variable Table", divider="gray")
variables = [
    ("T", "Torque", "Nm"),
    ("p", "Number of pole pairs", "-"),
    ("L_d", "d-axis inductance", "H"),
    ("L_q", "q-axis inductance", "H"),
    ("I_d", "d-axis current", "A"),
    ("I_q", "q-axis current", "A"),
    ("K_e", "Back-EMF constant", "V/rad/s"),
    ("K_V", "Velocity constant", "RPM/V"),
    ("N_t", "Number of turns per coil", "-"),
    ("k_w", "Winding factor", "-"),
    ("φ", "Flux per pole", "Wb"),
    ("R_ph", "Phase resistance", "Ω"),
    ("ρ", "Copper resistivity", "Ω·m"),
    ("l_w", "Wire length", "m"),
    ("A_w", "Wire cross-sectional area", "m²"),
    ("μ", "Core permeability", "H/m"),
    ("A", "Magnetic path area", "m²"),
    ("l", "Magnetic path length", "m"),
    ("q", "Slots per pole per phase", "-"),
    ("N_s", "Number of slots", "-"),
    ("m", "Number of phases", "-"),
    ("k_d", "Distribution factor", "-"),
    ("k_p", "Pitch factor", "-"),
    ("I_ph", "Phase current", "A"),
    ("J", "Current density", "A/m²"),
    ("S_fill", "Slot fill factor", "-"),
    ("N_c", "Number of coils per phase", "-"),
    ("A_slot", "Slot area", "m²"),
    ("f", "Electrical frequency", "Hz"),
    ("RPM", "Rotor speed", "RPM")
]
var_df = pd.DataFrame(variables, columns=["Symbol", "Description", "Unit"])
st.table(var_df)

# Notes
st.header("Notes", divider="gray")
st.markdown("""
- **Inductance**: The inductance equation is approximate; use FEA (e.g., ANSYS Maxwell) for accurate \( L_d \), \( L_q \).
- **Validation**: Verify results with FEA and prototype testing.
- **Controller**: Ensure the BLDC controller supports field-oriented control (FOC).
- **Example**: Defaults are set for a BLDC with KV ≈ 1000 RPM/V, 36 slots, 4 poles, R_ph ≈ 0.1 Ω.
- **Export**: Download the CSV for Excel or screenshot equations for Word.
""")