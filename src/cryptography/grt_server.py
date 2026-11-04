from __future__ import annotations

import math
import random
import numpy as np
from PIL import Image


#=====================================================#
#==========# Mathematical Theory Reference #==========#
#=====================================================#

# (Encryption) Scalar forward GRT coordinate mapping (single coordinate pair)
# Direct 1-to-1 reference implementation for formulas in the project report
# We will use this one to illustrate our implementation on the report
def forward_grt_coordinate(
    x: int, y: int, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> tuple[int, int]:
    if not (0 <= x < M and 0 <= y < N):
        raise ValueError(f"Coordinate ({x}, {y}) out of bounds [0, {M}) x [0, {N})")
    x_next = (a * x + b * y + rm) % M
    y_next = (c * x + d * y + rn) % N
    return x_next, y_next

# Complete decyption Pipline
def scramble_image_grt(image: Image.Image, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int) -> Image.Image:
    # Scrambles an image by permuting M x N tiles using forward GRT
    valid, reason = validate_grt_parameters(M, N, a, b, c, d, rm, rn)
    if not valid:
        raise ValueError(f"Invalid GRT parameters: {reason}")

    width, height = image.size
    if width % M != 0 or height % N != 0:
        raise ValueError(f'Image dimensions ({width}, {height}) must be divisible by grid ({M}, {N})')

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

#=======================================#
#==========# Helper function #==========#
#=======================================#

def generate_valid_grt_keys(M: int, N: int, max_val: int = 50) -> tuple[int, int, int, int, int, int]:
    # Constructively generates valid GRT keys (a, b, c, d, rm, rn) satisfying all 4 conditions

    if M < 1 or N < 1:
        raise ValueError("Grid dimensions M and N must be positive integers (>= 1)")

    p = math.gcd(M, N)
    h = M // p
    v = N // p

    # 1. Vectorized coprime pools for Condition 3 (gcd(a, h) == 1) and Condition 4 (gcd(d, v) == 1)
    upper = max(max_val, h, v, p, 2) + 1
    candidates = np.arange(1, upper, dtype=np.int64)
    valid_a_pool = candidates[np.gcd(candidates, h) == 1]
    valid_d_pool = candidates[np.gcd(candidates, v) == 1]

    a_bounded = valid_a_pool[valid_a_pool <= max_val]
    d_bounded = valid_d_pool[valid_d_pool <= max_val]
    if len(a_bounded) == 0:
        a_bounded = valid_a_pool
    if len(d_bounded) == 0:
        d_bounded = valid_d_pool

    # 2. Constructive sampling: enforce Condition 1 directly by setting b = k * h or c = k * v
    for _ in range(64):
        a = int(np.random.choice(a_bounded))
        d = int(np.random.choice(d_bounded))

        if random.choice([True, False]):
            # Enforce b % h == 0 directly
            b = random.randint(0, max_val // h) * h
            c = random.randint(0, max_val)
        else:
            # Enforce c % v == 0 directly
            b = random.randint(0, max_val)
            c = random.randint(0, max_val // v) * v

        det = a * d - b * c
        if (p > 1 and math.gcd(det, p) == 1) or (p == 1 and det != 0):
            rm = random.randint(0, M - 1)
            rn = random.randint(0, N - 1)
            return a, b, c, d, rm, rn

    # 3. Deterministic O(1) analytical fallback via Lan & Wang (2025) Eq. (7)-(8) & Eq. (11):
    # Base ESRT matrix has det = 1 and satisfies all 4 conditions unconditionally:
    #   a0 = 1, b0 = r, c0 = k_s * v, d0 = r * c0 + 1
    # Extended via E1 = [[e*a0, e*b0], [f*c0, f*d0]] with gcd(e, M) == 1 and gcd(f, N) == 1.
    r = random.randint(1, max(1, max_val // 4))
    c0 = random.randint(0, max(0, max_val // max(1, v))) * v
    a0, b0, d0 = 1, r, r * c0 + 1

    valid_e = candidates[np.gcd(candidates, M) == 1]
    valid_f = candidates[np.gcd(candidates, N) == 1]
    e = int(np.random.choice(valid_e[: min(10, len(valid_e))]))
    f = int(np.random.choice(valid_f[: min(10, len(valid_f))]))

    rm = random.randint(0, M - 1)
    rn = random.randint(0, N - 1)
    return e * a0, e * b0, f * c0, f * d0, rm, rn


def validate_grt_parameters(
    M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> tuple[bool, str]:
    params = [('M', M), ('N', N), ('a', a), ('b', b), ('c', c), ('d', d), ('rm', rm), ('rn', rn)]
    for name, val in params:
        if not isinstance(val, int) or isinstance(val, bool):
            return (False, f'Parameter {name} must be an integer, got {type(val).__name__}')

    if M < 1 or N < 1:
        return (False, 'Grid dimensions M and N must be positive integers (>= 1)')

    if a < 0 or b < 0 or c < 0 or d < 0:
        return (False, f'Matrix parameters a, b, c, d must be non-negative integers (>= 0), got a={a}, b={b}, c={c}, d={d}')

    if not (0 <= rm < M and 0 <= rn < N):
        return (False, 'Offset coordinates (rm, rn) must satisfy 0 <= rm < M and 0 <= rn < N')

    p = math.gcd(M, N)
    h = M // p
    v = N // p
    det = a * d - b * c

    if not (b % h == 0 or c % v == 0):
        return (False, 'Violated Lan & Wang Eq (2) Condition 1: expected (b % h == 0 or c % v == 0)')

    if (p > 1 and math.gcd(abs(det), p) != 1) or (p == 1 and det == 0):
        return (False, 'Violated Lan & Wang Eq (2) Condition 2: expected gcd(|G|, p) == 1')

    if math.gcd(a, h) != 1:
        return (False, 'Violated Lan & Wang Eq (2) Condition 3: expected gcd(a, h) == 1')

    if math.gcd(d, v) != 1:
        return (False, 'Violated Lan & Wang Eq (2) Condition 4: expected gcd(d, v) == 1')

    return True, 'Valid GRT parameters'
