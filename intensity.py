from functools import reduce
from typing import Callable, Any


def intensity(i0: float, distance: float, d: float) -> float:
    if d <= 0.0001:
        return 0.0
    return max(i0 * (1.0 - distance / d), 0.0)


def intensity_to_color(max_intensity: float) -> tuple[int, int, int, int]:
    if max_intensity < 0.001:
        return 255, 255, 255, 0
    if max_intensity < 1.0:
        return 255, 0, 0, int(max_intensity * 255)
    elif max_intensity < 2:
        return 255, int((max_intensity - 1.0) * 255.0), 0, 255
    else:
        clamped_intensity = min(3.0, max_intensity) - 2.0
        return 255, 255, int(clamped_intensity * 192.0), 255


def avg_color(colors: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    color_length = len(colors)
    if color_length == 0:
        return 255, 255, 255, 0
    if color_length == 1:
        return colors[0]
    sum_colors = []
    for i in range(0, 4):
        sum_colors.append(reduce(lambda c1, c2: c1 + c2[i], colors, 0))
    avg: Callable[[int], int] = lambda pos: int(float(sum_colors[pos]) / color_length)
    return avg(0), avg(1), avg(2), avg(3)
