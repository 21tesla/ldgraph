import numpy as np
from scipy.optimize import curve_fit

# Mathematical Models

def one_to_one_binding(x, Kd, max_signal, min_signal):
    return min_signal + max_signal * (x / (Kd + x))

def hill_equation(x, Kd, max_signal, min_signal, n):
    x_safe = np.abs(x)
    return min_signal + max_signal * ((x_safe**n) / (Kd**n + x_safe**n + 1e-12))

def cooperative_binding(x, K1, K2, max_signal, min_signal):
    # Two-site Adair equation
    num = (x / K1) + 2 * (x**2 / (K1 * K2))
    den = 2 * (1 + (x / K1) + (x**2 / (K1 * K2)))
    return min_signal + max_signal * (num / den)


# Generic Fitting

def generic_fit(model_func, x, y, p0, free_mask):
    try:
        p0_free = [p for p, is_free in zip(p0, free_mask) if is_free]
        
        # If all parameters are fixed, return immediately
        if not p0_free:
            return p0, [0.0] * len(p0)
            
        def wrapper(x_val, *free_args):
            full_args = []
            free_idx = 0
            for is_free, fixed_val in zip(free_mask, p0):
                if is_free:
                    full_args.append(free_args[free_idx])
                    free_idx += 1
                else:
                    full_args.append(fixed_val)
            return model_func(x_val, *full_args)
            
        popt_free, pcov_free = curve_fit(wrapper, x, y, p0=p0_free, maxfev=10000)
        perr_free = np.sqrt(np.diag(pcov_free))
        
        # Reconstruct the full parameter array with fixed values slotted back in
        popt_full = []
        perr_full = []
        free_idx = 0
        for is_free, fixed_val in zip(free_mask, p0):
            if is_free:
                popt_full.append(popt_free[free_idx])
                perr_full.append(perr_free[free_idx])
                free_idx += 1
            else:
                popt_full.append(fixed_val)
                perr_full.append(0.0)
                
        return popt_full, perr_full
    except Exception as e:
        print(f"Fitting failed: {e}")
        return None, None


# Registry

AVAILABLE_MODELS = {
    "1:1 Binding Isotherm": {
        "model_func": one_to_one_binding,
        "default_params": {"Kd": 1.0, "Max Signal": 100.0, "Min Signal": 0.0}
    },
    "Hill Equation": {
        "model_func": hill_equation,
        "default_params": {"Kd": 1.0, "Max Signal": 100.0, "Min Signal": 0.0, "n (Hill coeff)": 1.0}
    },
    "Cooperative Binding (2-Site)": {
        "model_func": cooperative_binding,
        "default_params": {"K1": 1.0, "K2": 1.0, "Max Signal": 100.0, "Min Signal": 0.0}
    }
}
