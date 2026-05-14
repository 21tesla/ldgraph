import numpy as np
from scipy.optimize import curve_fit

# Mathematical Models

def one_to_one_binding(x, Kd, max_signal, min_signal):
    Kd_safe = np.abs(Kd) + 1e-15
    return min_signal + max_signal * (x / (Kd_safe + x))

def hill_equation(x, Kd, max_signal, min_signal, n):
    x_safe = np.abs(x)
    Kd_safe = np.abs(Kd) + 1e-15
    return min_signal + max_signal * ((x_safe**n) / (Kd_safe**n + x_safe**n + 1e-12))

def cooperative_binding(x, K1, K2, max_signal, min_signal):
    # Two-site Adair equation
    K1_s = np.abs(K1) + 1e-15
    K2_s = np.abs(K2) + 1e-15
    num = (x / K1_s) + 2 * (x**2 / (K1_s * K2_s))
    den = 2 * (1 + (x / K1_s) + (x**2 / (K1_s * K2_s)))
    return min_signal + max_signal * (num / den)


def mono_association(x, k, span, y0):
    k_s = np.abs(k) + 1e-15
    return y0 + span * (1 - np.exp(-k_s * x))


def mono_decay(x, k, span, plateau):
    k_s = np.abs(k) + 1e-15
    return plateau + span * np.exp(-k_s * x)


def general_monoexponential(x, a, b, c):
    # Pure mathematical form: y = a * e^(b * x) + c
    return a * np.exp(b * x) + c


# Generic Fitting

def generic_fit(model_func, x, y, p0, free_mask, bounds=None):
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
            
        # Squeeze bounds to match free parameters
        fit_bounds = (-np.inf, np.inf)
        if bounds:
            lower_full, upper_full = bounds
            lower_free = [l for l, is_free in zip(lower_full, free_mask) if is_free]
            upper_free = [u for u, is_free in zip(upper_full, free_mask) if is_free]
            fit_bounds = (lower_free, upper_free)

        popt_free, pcov_free = curve_fit(wrapper, x, y, p0=p0_free, bounds=fit_bounds, maxfev=10000)
        
        # Check if covariance was estimated
        if pcov_free is None or np.any(np.isinf(pcov_free)) or np.any(np.isnan(pcov_free)):
            perr_free = np.zeros_like(popt_free)
        else:
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
        "default_params": {"Kd": 1.0, "Max Signal": 100.0, "Min Signal": 0.0},
        "bounds": ([0, -np.inf, -np.inf], [np.inf, np.inf, np.inf])
    },
    "Hill Equation": {
        "model_func": hill_equation,
        "default_params": {"Kd": 1.0, "Max Signal": 100.0, "Min Signal": 0.0, "n (Hill coeff)": 1.0},
        "bounds": ([0, -np.inf, -np.inf, 0], [np.inf, np.inf, np.inf, 10])
    },
    "Cooperative Binding (2-Site)": {
        "model_func": cooperative_binding,
        "default_params": {"K1": 1.0, "K2": 1.0, "Max Signal": 100.0, "Min Signal": 0.0},
        "bounds": ([0, 0, -np.inf, -np.inf], [np.inf, np.inf, np.inf, np.inf])
    },
    "One-phase Association": {
        "model_func": mono_association,
        "default_params": {"k (rate)": 0.1, "Span": 100.0, "Y0": 0.0},
        "bounds": ([0, -np.inf, -np.inf], [np.inf, np.inf, np.inf]),
        "is_kinetic": True
    },
    "One-phase Decay": {
        "model_func": mono_decay,
        "default_params": {"k (rate)": 0.1, "Span": 100.0, "Plateau": 0.0},
        "bounds": ([0, -np.inf, -np.inf], [np.inf, np.inf, np.inf]),
        "is_kinetic": True
    },
    "General Monoexponential": {
        "model_func": general_monoexponential,
        "default_params": {"a (amplitude)": 1.0, "b (rate)": 0.01, "c (offset)": 0.0},
        "bounds": ([-np.inf, -np.inf, -np.inf], [np.inf, np.inf, np.inf]),
        "is_kinetic": True
    }
}
