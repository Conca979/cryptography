from __future__ import annotations

import math
import numpy as np
from PIL import Image


# def validate_grt_parameters(M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int) -> tuple[bool, str]:
#     params = [("M", M), ("N", N), ("a", a), ("b", b), ("c", c), ("d", d), ("rm", rm), ("rn", rn)]
#     for name, val in params:
#         if not isinstance(val, int) or isinstance(val, bool):
#             return (False, f"Parameter {name} must be an integer, got {type(val).__name__}")

#     if M < 1 or N < 1:
#         return (False, f"Grid dimensions M and N must be positive integers (>= 1)")

#     if a < 0 or b < 0 or c < 0 or d < 0:
#         return (False, f"Matrix parameters a, b, c, d must be non-negative integers (>= 0), got a={a}, b={b}, c={c}, d={d}")

#     if not (0 <= rm < M and 0 <= rn < N):
#         return (False, f"Offset coordinates (rm, rn) must satisfy 0 <= rm < M and 0 <= rn < N")

#     # Compute greatest common divisor and quotient factors (Lan & Wang 2025, Eq 2)
#     p = math.gcd(M, N)
#     h = M // p
#     v = N // p
#     det = a * d - b * c

#     # Condition 1: b % h == 0 or c % v == 0
#     if not (b % h == 0 or c % v == 0):
#         return (False, f"Violated Lan & Wang Eq (2) Condition 1: expected (b % h == 0 or c % v == 0)")

#     # Condition 2: gcd(det, p) == 1
#     if math.gcd(det, p) != 1:
#         return (False, f"Violated Lan & Wang Eq (2) Condition 2: expected gcd(|G|, p) == 1")

#     # Condition 3: gcd(a, h) == 1
#     if math.gcd(a, h) != 1:
#         return (False, f"Violated Lan & Wang Eq (2) Condition 3: expected gcd(a, h) == 1")

#     # Condition 4: gcd(d, v) == 1
#     if math.gcd(d, v) != 1:
#         return (False, f"Violated Lan & Wang Eq (2) Condition 4: expected gcd(d, v) == 1")

#     return True, "Valid GRT parameters"

# Encryption
def forward_grt_coordinate(x: int, y: int, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int) -> tuple[int, int]:
    x_next = (a * x + b * y + rm) % M
    y_next = (c * x + d * y + rn) % N
    return x_next, y_next

# Decyption
def inverse_grt_coordinate(x_prime: int, y_prime: int, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int) -> tuple[int, int]:

    p = math.gcd(M, N)
    h = M // p
    v = N // p
    det = a * d - b * c

    # Stage 1: Equilateral inverse mapping modulo p (Lan & Wang 2025, Eq 12)
    if p > 1:
        det_inv_p = pow(det % p, -1, p)
        dx = (x_prime - rm) % p
        dy = (y_prime - rn) % p
        xp = (det_inv_p * (d * dx - b * dy)) % p
        yp = (det_inv_p * (-c * dx + a * dy)) % p
    else:
        xp = 0
        yp = 0

    # Stage 2: Inverse projection mapping (Lan & Wang 2025, Eq 13 & Table 6)
    delta_x = (x_prime - rm) - (a * xp + b * yp)
    delta_y = (y_prime - rn) - (c * xp + d * yp)
    H = (delta_x // p) % h if h > 1 else 0
    V = (delta_y // p) % v if v > 1 else 0

    # Stage 3: Inverse triangular mapping (Lan & Wang 2025, Eq 14, 15, 16)
    b_mod_h = b % h if h > 1 else 0
    c_mod_v = c % v if v > 1 else 0

    if b_mod_h == 0 and c_mod_v == 0:
        # Case 1 (Diagonal system, Eq 14)
        xh = (pow(a, -1, h) * H) % h if h > 1 else 0
        yv = (pow(d, -1, v) * V) % v if v > 1 else 0
    elif b_mod_h == 0 and c_mod_v != 0:
        # Case 2 (Lower triangular system, Eq 15)
        xh = (pow(a, -1, h) * H) % h if h > 1 else 0
        yv = (pow(d, -1, v) * (V - c * xh)) % v if v > 1 else 0
    elif b_mod_h != 0 and c_mod_v == 0:
        # Case 3 (Upper triangular system, Eq 16)
        yv = (pow(d, -1, v) * V) % v if v > 1 else 0
        xh = (pow(a, -1, h) * (H - b * yv)) % h if h > 1 else 0

    # Stage 4: CRT assembly / Coordinate reconstruction (Lan & Wang 2025, Eq 17)
    x = xp + p * xh
    y = yp + p * yv

    return x, y

def scramble_image_grt(image: Image.Image, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int) -> Image.Image:
    # Scrambles an image by permuting M x N tiles using forward GRT

    width, height = image.size

    tile_width = width // M
    tile_height = height // N

    # Use NumPy array representation for fast, lossless block slicing
    source_array = np.array(image)
    scrambled_array = np.empty_like(source_array)

    # Permute each tile from original (x, y) to forward destination (x_next, y_next)
    for y in range(N):
        for x in range(M):
            x_next, y_next = forward_grt_coordinate(x, y, M, N, a, b, c, d, rm, rn)

            src_y_start = y * tile_height
            src_y_end = (y + 1) * tile_height
            src_x_start = x * tile_width
            src_x_end = (x + 1) * tile_width

            dst_y_start = y_next * tile_height
            dst_y_end = (y_next + 1) * tile_height
            dst_x_start = x_next * tile_width
            dst_x_end = (x_next + 1) * tile_width

            scrambled_array[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = (
                source_array[src_y_start:src_y_end, src_x_start:src_x_end]
            )

    scrambled_image = Image.fromarray(scrambled_array, mode=image.mode)
    if image.mode == "P" and image.getpalette() is not None:
        scrambled_image.putpalette(image.getpalette())

    return scrambled_image

def descramble_image_grt(scrambled_image: Image.Image, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int) -> Image.Image:
    width, height = scrambled_image.size

    tile_width = width // M
    tile_height = height // N

    # Use NumPy array representation for fast, lossless block slicing
    scrambled_array = np.array(scrambled_image)
    reconstructed_array = np.empty_like(scrambled_array)

    # Map each tile from scrambled position (x_prime, y_prime) back to original (x, y)
    for y_prime in range(N):
        for x_prime in range(M):
            x, y = inverse_grt_coordinate(
                x_prime, y_prime, M, N, a, b, c, d, rm, rn
            )

            src_y_start = y_prime * tile_height
            src_y_end = (y_prime + 1) * tile_height
            src_x_start = x_prime * tile_width
            src_x_end = (x_prime + 1) * tile_width

            dst_y_start = y * tile_height
            dst_y_end = (y + 1) * tile_height
            dst_x_start = x * tile_width
            dst_x_end = (x + 1) * tile_width

            reconstructed_array[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = (
                scrambled_array[src_y_start:src_y_end, src_x_start:src_x_end]
            )

    reconstructed_image = Image.fromarray(
        reconstructed_array, mode=scrambled_image.mode
    )
    if scrambled_image.mode == "P" and scrambled_image.getpalette() is not None:
        reconstructed_image.putpalette(scrambled_image.getpalette())

    return reconstructed_image
