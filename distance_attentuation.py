def get_attentuated_max_distance(intensity: float, max_distance: float, projected_distance_ratio: float) -> float:
    escaped_ratio = projected_distance_ratio
    very_large_distance = 1000.0
    if escaped_ratio < 0:
        escaped_ratio = very_large_distance  # Assign big number, so we consider distance very large
    return max_distance * (intensity - escaped_ratio)