from pint import UnitRegistry
from math import isclose
from scipy.optimize import minimize
ureg = UnitRegistry()
ureg.auto_reduce_dimensions = True
m, cm, kN, N_mm2 = ureg.m, ureg.cm, ureg.kN, ureg.N / ureg.mm**2


# Initialize units with Pint and handcalcs options
ureg = UnitRegistry()
m, cm, kN, N_mm2 = ureg.m, ureg.cm, ureg.kN, ureg.N / ureg.mm**2

def steel_stress_strain_relation(epsilon_s, f_yk=500*N_mm2, f_tk_cal=525*N_mm2, gamma_s=1.15, E_s=210000*N_mm2, epsilon_su=0.025):
    # Calculate design values based on Eurocode 2
    f_yd = f_yk / gamma_s  # Design yield strength
    f_td_cal = f_tk_cal / gamma_s  # Design tensile strength
    epsilon_yd = f_yd / E_s  # Yield strain

    # Calculate stress based on the strain
    if epsilon_s <= epsilon_yd:
        sigma_s = E_s * epsilon_s  # Linear in the elastic range
    elif epsilon_s <= epsilon_su:
        sigma_s = f_yd + (f_td_cal - f_yd) / (epsilon_su - epsilon_yd) * (epsilon_s - epsilon_yd)  # Linear in the plastic range
    else:
        sigma_s = f_td_cal  # Capped at f_td_cal for strains beyond ultimate strain

    return sigma_s
1
# Function to calculate alpha_R and k_a based on ec, ec3, and ec3u
def calculate_alpha_k_a(ec, ec3=-2, ec3u=-3.5):
    ec_abs = abs(ec)
    if ec_abs <= abs(ec3):
        alpha_R = (ec_abs / 2) - (ec**2 / 12)
        k_a = (8 - ec_abs) / (24 - 4 * ec_abs)
    elif abs(ec3) < ec_abs <= abs(ec3u):
        alpha_R = (3 * ec_abs - 2) / (3 * ec_abs)
        k_a = (ec_abs * (3 * ec_abs - 4) + 2) / (2 * ec_abs * (3 * ec_abs - 2))
    return alpha_R, k_a

# Objective function to minimize error based on constraints
def objective(vars, mueds):
    ec, es = vars
    alpha_r, k_a = calculate_alpha_k_a(ec)
    
    if isclose(ec, es):
        return float("inf")  # Penalize if ec is close to es to avoid division by zero
    
    xi = ec / (ec - es)
    zeta = 1 - k_a * xi
    error = (alpha_r * xi * zeta - mueds) ** 2
    return error

def dimensioning(mueds):
    # Optimization setup
    initial_guess = [-3.5, 25.0]
    bounds = [(-3.5, 0), (0, 25)]    

    result = minimize(objective, initial_guess, args=(mueds,), bounds=bounds, tol=1e-12)

    # Check if the optimization was successful
    if result.success:
        # Extract and print the optimized values of ec and es
        ec_opt, es_opt = result.x  # result.x contains the optimized values
        return ec_opt, es_opt
    else:
        return None

    

# Main code to set up parameters and optimize solution
if __name__ == "__main__":
    # Input parameters
    MEd = 7 * kN * m
    b, h, d1 = 100 * cm, 40 * cm, 5 * cm
    fcd = 0.85 * 20 / 1.5 * N_mm2
    d = h - d1
    mueds = MEd / (b * d**2 * fcd)
    
    # Perform the optimization
    result = dimensioning(mueds)
    print("Optimization Result:", result)

    sigma = steel_stress_strain_relation(15.62/1000, 525*N_mm2, f_tk_cal=525*N_mm2, gamma_s=1.15, E_s=210000*N_mm2, epsilon_su=0.025)
    print(sigma)