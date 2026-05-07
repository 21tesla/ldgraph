import os
import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".ldgraph_prefs"

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_model_params(model_name, default_params):
    config = load_config()
    model_config = config.get(model_name, {})
    
    # Merge defaults with saved config
    result = []
    for param_name, default_val in default_params.items():
        val = model_config.get(param_name, {"value": default_val, "fixed": False})
        # Backwards compatibility: if it was saved as a raw float previously
        if isinstance(val, (int, float)):
            val = {"value": val, "fixed": False}
        result.append(val)
    return result

def save_model_params(model_name, param_names, param_values, fixed_flags):
    config = load_config()
    if model_name not in config:
        config[model_name] = {}
        
    for name, val, fixed in zip(param_names, param_values, fixed_flags):
        config[model_name][name] = {"value": val, "fixed": fixed}
        
    save_config(config)
