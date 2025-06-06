
concrete_cover_table = {
    "XC1": {
        "C16/20": {
            (0, 10): {"c_min": 10, "Δc_dev": 10, "c_nom": 20},
            (12, 14): {"c_min": 12, "Δc_dev": 10, "c_nom": 25},
            (16, 20): {"c_min": 15, "Δc_dev": 10, "c_nom": 30},
            (21, 25): {"c_min": 20, "Δc_dev": 10, "c_nom": 35},
            (26, 28): {"c_min": 25, "Δc_dev": 10, "c_nom": 40},
            (29, 32): {"c_min": 28, "Δc_dev": 10, "c_nom": 45},
        }
    },
    "XC2": {
        "C16/20": {
            (0, 20): {"c_min": 20, "Δc_dev": 15, "c_nom": 35},
            (21, 25): {"c_min": 25, "Δc_dev": 10, "c_nom": 35},
            (26, 28): {"c_min": 28, "Δc_dev": 10, "c_nom": 40},
            (29, 32): {"c_min": 32, "Δc_dev": 10, "c_nom": 45},
        }
    },
    "XC3": {
        "C20/25": {
            (0, 20): {"c_min": 20, "Δc_dev": 15, "c_nom": 35},
            (21, 25): {"c_min": 25, "Δc_dev": 10, "c_nom": 35},
            (26, 28): {"c_min": 28, "Δc_dev": 10, "c_nom": 40},
            (29, 32): {"c_min": 32, "Δc_dev": 10, "c_nom": 45},
        }
    },
    "XC4": {
        "C25/30": {
            (0, 25): {"c_min": 25, "Δc_dev": 15, "c_nom": 40},
            (26, 28): {"c_min": 28, "Δc_dev": 10, "c_nom": 40},
            (29, 32): {"c_min": 32, "Δc_dev": 10, "c_nom": 45},
        }
    },
    "XD1": {
        "C30/37": {
            (0, 32): {"c_min": "c_min,dur + Δc_dur = 40", "Δc_dev": 15, "c_nom": 55},
        }
    },
    "XS1": {
        "C30/37": {
            (0, 32): {"c_min": "c_min,dur + Δc_dur = 40", "Δc_dev": 15, "c_nom": 55},
        }
    },
    "XD2 XS2": {
        "C35/45": {
            (0, 32): {"c_min": "c_min,dur + Δc_dur = 40", "Δc_dev": 15, "c_nom": 55},
        }
    },
    "XD2 XS2": {
        "C35/45": {
            (0, 32): {"c_min": "c_min,dur + Δc_dur = 40", "Δc_dev": 15, "c_nom": 55},
        }
    },
    "XD3": {
        ">= C35/45": {
            (0, 32): {"c_min": "c_min,dur + Δc_dur = 40", "Δc_dev": 15, "c_nom": 55},
        }
    },
    "XS3": {
        ">= C35/45": {
            (0, 32): {"c_min": "c_min,dur + Δc_dur = 40", "Δc_dev": 15, "c_nom": 55},
        }
    }
}

def get_max_concrete_cover(exposure_classes, bar_diameter):
    max_c_min = 0
    max_delta_c_dev = 0
    max_c_nom = 0
    min_strength_classes = set()
    
    for exposure_class in exposure_classes:
        if exposure_class in concrete_cover_table:
            strength_classes = concrete_cover_table[exposure_class]
            
            for strength_class, diameter_ranges in strength_classes.items():
                # Check each diameter range
                for diameter_range, cover_info in diameter_ranges.items():
                    if diameter_range[0] <= bar_diameter <= diameter_range[1]:
                        # Update maximum values
                        c_min_value = cover_info["c_min"]
                        if isinstance(c_min_value, str) and "c_min,dur" in c_min_value:
                            c_min_value = 40  # Assign numerical equivalent
                        
                        max_c_min = max(max_c_min, c_min_value)
                        max_delta_c_dev = max(max_delta_c_dev, cover_info["Δc_dev"])
                        max_c_nom = max(max_c_nom, cover_info["c_nom"])
                        
                        # Track the minimum required strength class
                        min_strength_classes.add(strength_class)
    
    return {
        "max_c_min": max_c_min,
        "max_Δc_dev": max_delta_c_dev,
        "max_c_nom": max_c_nom,
        "min_strength_classes": sorted(min_strength_classes)  # Sorted for clarity
    }


def get_all_exposure_classes():
    exposure_classes = list(concrete_cover_table.keys())  # Get all keys (exposure classes)
    return exposure_classes
