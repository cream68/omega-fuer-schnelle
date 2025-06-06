import streamlit as st
import math
import pandas as pd
from biegefunctions import dimensioning, calculate_alpha_k_a, steel_stress_strain_relation
from pint import UnitRegistry
from handcalcs.decorator import handcalc
import eurocodepy as ec
import handcalcs
from concrete import get_all_exposure_classes, get_max_concrete_cover
handcalcs.set_option("preferred_string_formatter", "~L")


ureg = UnitRegistry()
ureg.auto_reduce_dimensions = True
m, cm, kN, N_mm2 = ureg.m, ureg.cm, ureg.kN, ureg.N / ureg.mm**2

f_yk2 = 500*N_mm2

with st.expander("# Eingangsgrößen"):
    col1, col2, col3 =st.columns(3)
    with col1:
        M_Ed = st.number_input("Bemessungsmoment [kNm]", value=240.0)*ureg.kN*ureg.m
        N_Ed = st.number_input("Bemessungsnormalkraft (Zug positiv) [kN]", value=40.0)*ureg.kN
    with col2:
        b=st.number_input("Breite [cm]",value=100.0)*ureg.cm
        h=st.number_input("Höhe [cm]",value=40.0)*ureg.cm

        d_L=st.number_input("Durchmesser Längsbewehrung [mm]",value=8)
        d_Q=st.number_input("Durchmesser Querbewehrung [mm]",value=10)*ureg.mm
        overwrite_dL = st.selectbox("Bewehrungabstand selber wählen?", [True, False], index=1)
        if overwrite_dL == False:
            cover_class = st.multiselect("Betongüte", options=get_all_exposure_classes())
            cover_max = get_max_concrete_cover(cover_class, d_L)
            d_L = d_L*ureg.mm
            d_1=cover_max["max_c_nom"]*ureg.mm
        else:
            d_prime = st.number_input("Bewehrungsabstand [mm]",value=20)*ureg.mm
    with col3:
        concrete_types = ec.ConcreteClasses.keys()
        selected_concrete_type = st.selectbox("Beton", concrete_types, index=1)
        concrete = ec.ConcreteClasses[selected_concrete_type] # Alternative 4
        f_ck = concrete["fck"]*N_mm2  # Characteristic compressive strength
        f_ctm = concrete["fctm"]*N_mm2
        reinforcement_types = ec.ReinforcementClasses.keys()
        selected_reinforcement_type = st.selectbox("Bewehrungsstahl", reinforcement_types, index=15)
        reinforcment = ec.ReinforcementClasses[selected_reinforcement_type]
        f_yk = reinforcment["fyk"]*N_mm2
        f_tk = 525*N_mm2
        gamma_s = 1.15




@handcalc(precision=2)
def fcd_formula(f_ck, f_yk, f_tk, gamma_s):
    f_cd = 0.85 * f_ck / 1.5
    f_yk = f_yk
    f_tk = f_tk
    gamma_s=gamma_s
    return locals()


@handcalc(precision=2)
def d_formula(h,d_1, d_L, d_Q):
    d_prime = d_1+d_Q+d_L/2
    d = h - d_prime
    z_s = h/2-d_prime
    return locals()

@handcalc(precision=2)
def d_formula_overwite(h,d_prime):
    d_prime = d_prime
    z_s = h/2-d_prime
    d = h - d_prime
    return locals()

@handcalc(precision=3, override="long")
def mu_Eds_formula(M_Ed,N_Ed,b,d,f_cd, z_s):
    M_Eds = M_Ed-N_Ed*z_s
    mu_Eds = M_Eds / (b* d**2 * f_cd)
    return locals()

@handcalc(precision=2, override="params")
def es_ec_sigma_formula(e_s,e_c, f_yk):
    e_c = e_c #Promille
    e_s = e_s #Promille
    sigma_sd = steel_stress_strain_relation(e_s/1000, f_yk, f_tk_cal=525*N_mm2, gamma_s=1.15, E_s=210000*N_mm2, epsilon_su=25/1000)
    return locals()


@handcalc(precision=4, override="params")
def biege_parameters(e_c,e_s, alpha_r, k_a):
    xi = e_c/(e_c-e_s)
    k_a = k_a
    alpha_r = alpha_r
    zeta = 1-k_a*xi
    omega = alpha_r*xi
    return locals()

@handcalc(precision=2)
def As_omega(omega,b,d, f_cd, f_yd,N_Ed):
    As = (1/f_yd*(omega*b*d*f_cd+N_Ed)).to(ureg.cm**2)
    return locals()

@handcalc(precision=2)
def As_min(b,d,h, f_ctm,f_yk):
    W_y = b*h**2/6
    M_cr = (f_ctm*W_y).to(kN*m)
    A_smin = (M_cr/(f_yk*0.9*d)).to(ureg.cm**2)
    return locals()

@handcalc(precision=2)
def Mcr_N(b,d,h, f_ctm,f_yk,N_Ed):
    W_y = b*h**2/6
    Delta_M = (W_y*N_Ed/(b*h)).to(ureg.kN*ureg.m)
    M_riss = (W_y*f_ctm-Delta_M).to(ureg.kN*ureg.m)
    return locals()

st.markdown("Nutzhöhe, Hebelarm")
if overwrite_dL == False:
    latex_code, output = d_formula(h,d_1, d_L, d_Q)
else:
    latex_code, output = d_formula_overwite(h,d_prime)
d = output["d"]
z_s = output["z_s"]
st.latex(latex_code)

st.markdown("Materialdaten")
latex_code, output = fcd_formula(f_ck, f_yk, f_tk, gamma_s)
f_cd = output["f_cd"]
st.latex(latex_code)


st.markdown("dimensionsloser Eingangswert")
latex_code, output = mu_Eds_formula(M_Ed,N_Ed,b,d,f_cd, z_s)
mu_Eds = output["mu_Eds"]
st.latex(latex_code)

with st.expander("Dehungsebene", expanded=False):
    result = dimensioning(mu_Eds)
    if result is not None:
        e_c, e_s = result
    alpha_r, k_a  = calculate_alpha_k_a(e_c)

    latex_code, output = es_ec_sigma_formula(e_s, e_c, f_yk)
    sigma_sd = output["sigma_sd"]
    st.latex(latex_code)


    latex_code, output = biege_parameters(e_c, e_s, alpha_r, k_a)
    omega = output["omega"]
    st.latex(latex_code)

st.markdown("erforderliche Bewehrung")
latex_code, _ = As_omega(omega,b,d, f_cd, sigma_sd,N_Ed)
st.latex(latex_code)

st.markdown("Rissbewehrung")

latex_code, _ = As_min(b,d,h,f_ctm,f_yk)
st.latex(latex_code)

latex_code, _ = Mcr_N(b,d,h,f_ctm,f_yk,N_Ed)
st.latex(latex_code)