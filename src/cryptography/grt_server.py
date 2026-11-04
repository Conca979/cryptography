from __future__ import annotations

import math
import random
import numpy as np
from PIL import Image


#=====================================================#
#==========# Mathematical Theory Reference #==========#
#=====================================================#

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

# Scalar forward GRT coordinate mapping (single coordinate pair)
# Direct 1-to-1 reference implementation for formulas in the project report
# We will use this one to illustrate our implementation on the report
def forward_grt_coordinate(
    x: int, y: int, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> tuple[int, int]:
    x_next = (a * x + b * y + rm) % M
    y_next = (c * x + d * y + rn) % N
    return x_next, y_next

# Scalar inverse GRT coordinate mapping (Decryption) (single coordinate pair, Lan & Wang 2025 Eq. 12-17)
# Direct 1-to-1 reference implementation for formulas in the project report
# Which we will use to illustrate our implementation on the report
def inverse_grt_coordinate(
    x_prime: int, y_prime: int, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> tuple[int, int]:
    p = math.gcd(M, N)
    h = M // p
    v = N // p
    det = a * d - b * c

    # Stage 1: Equilateral inverse mapping modulo p (Lan & Wang 2025, Eq. 12)
    if p > 1:
        det_inv_p = pow(det % p, -1, p)
        dx = (x_prime - rm) % p
        dy = (y_prime - rn) % p
        xp = (det_inv_p * (d * dx - b * dy)) % p
        yp = (det_inv_p * (-c * dx + a * dy)) % p
    else:
        xp = 0
        yp = 0

    # Stage 2: Inverse projection mapping (Lan & Wang 2025, Eq. 13 & Table 6)
    delta_x = (x_prime - rm) - (a * xp + b * yp)
    delta_y = (y_prime - rn) - (c * xp + d * yp)
    H = (delta_x // p) % h if h > 1 else 0
    V = (delta_y // p) % v if v > 1 else 0

    # Stage 3: Inverse triangular mapping (Lan & Wang 2025, Eq. 14, 15, 16)
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


#=======================================================================#
#==========# Highly Production-grade Vectorized Optimization #==========#
#=======================================================================#

# Batch forward coordinate mapping, highly optimized for performance
def forward_grt_coordinates_vectorized(
    M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> tuple[np.ndarray, np.ndarray]:

    x = np.arange(M, dtype=np.int32)[None, :]  # Shape: (1, M)
    y = np.arange(N, dtype=np.int32)[:, None]  # Shape: (N, 1)

    x_next = (a * x + b * y + rm) % M
    y_next = (c * x + d * y + rn) % N
    return x_next, y_next
 
# Batch inverse coordinate mapping
def inverse_grt_coordinates_vectorized(
    M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> tuple[np.ndarray, np.ndarray]:

    p = math.gcd(M, N)
    h = M // p
    v = N // p
    det = a * d - b * c

    x_prime = np.arange(M, dtype=np.int32)[None, :]  # Shape: (1, M)
    y_prime = np.arange(N, dtype=np.int32)[:, None]  # Shape: (N, 1)

    dx0 = x_prime - rm  # Shape: (1, M)
    dy0 = y_prime - rn  # Shape: (N, 1)

    # Stage 1: Equilateral inverse mapping modulo p (Eq. 12)
    # Pre-multiply 1D vectors before 2D broadcasting to minimize full-grid arithmetic
    if p > 1:
        det_inv_p = pow(det % p, -1, p)
        dx_d = ((det_inv_p * d) % p * (dx0 % p)) % p
        dy_b = ((-det_inv_p * b) % p * (dy0 % p)) % p
        dx_c = ((-det_inv_p * c) % p * (dx0 % p)) % p
        dy_a = ((det_inv_p * a) % p * (dy0 % p)) % p
        xp = (dx_d + dy_b) % p
        yp = (dx_c + dy_a) % p
    else:
        xp = 0
        yp = 0

    # Stage 2: Inverse projection mapping (Eq. 13)
    delta_x = dx0 - (a * xp + b * yp)
    delta_y = dy0 - (c * xp + d * yp)
    H = (delta_x // p) % h if h > 1 else 0
    V = (delta_y // p) % v if v > 1 else 0

    # Stage 3: Inverse triangular mapping (Eq. 14, 15, 16)
    b_mod_h = b % h if h > 1 else 0
    c_mod_v = c % v if v > 1 else 0
    a_inv_h = pow(a, -1, h) if h > 1 else 0
    d_inv_v = pow(d, -1, v) if v > 1 else 0

    if b_mod_h == 0 and c_mod_v == 0:
        xh = (a_inv_h * H) % h if h > 1 else 0
        yv = (d_inv_v * V) % v if v > 1 else 0
    elif b_mod_h == 0 and c_mod_v != 0:
        xh = (a_inv_h * H) % h if h > 1 else 0
        yv = (d_inv_v * (V - c * xh)) % v if v > 1 else 0
    else:
        yv = (d_inv_v * V) % v if v > 1 else 0
        xh = (a_inv_h * (H - b * yv)) % h if h > 1 else 0

    # Stage 4: CRT coordinate reconstruction (Eq. 17)
    orig_x = xp + p * xh
    orig_y = yp + p * yv
    return orig_x, orig_y

# Complete encryptio Pipeline
def scramble_image_grt_v(
    image: Image.Image, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> Image.Image:
    
    source_array = np.asarray(image)
    height, width = source_array.shape[:2]
    tile_height = height // N
    tile_width = width // M

    x_next, y_next = forward_grt_coordinates_vectorized(M, N, a, b, c, d, rm, rn)
    flat_dst = (y_next * M + x_next).ravel()

    if tile_height == 1 and tile_width == 1:
        scrambled_flat = np.empty_like(source_array).reshape(N * M, -1)
        scrambled_flat[flat_dst] = source_array.reshape(N * M, -1)
        scrambled_array = scrambled_flat.reshape(source_array.shape)
    else:
        rest = source_array.shape[2:]
        tiles = source_array.reshape(N, tile_height, M, tile_width, *rest).swapaxes(1, 2)
        tiles_flat = tiles.reshape(N * M, tile_height, tile_width, *rest)
        scrambled_tiles = np.empty_like(tiles_flat)
        scrambled_tiles[flat_dst] = tiles_flat
        scrambled_array = (
            scrambled_tiles.reshape(N, M, tile_height, tile_width, *rest)
            .swapaxes(1, 2)
            .reshape(source_array.shape)
        )

    scrambled_image = Image.fromarray(scrambled_array, mode=image.mode)
    if image.mode == "P" and image.getpalette() is not None:
        scrambled_image.putpalette(image.getpalette())

    return scrambled_image

# Complete decrypt Pipeline
def descramble_image_grt_v(
    scrambled_image: Image.Image, M: int, N: int, a: int, b: int, c: int, d: int, rm: int, rn: int
) -> Image.Image:
    
    scrambled_array = np.asarray(scrambled_image)
    height, width = scrambled_array.shape[:2]
    tile_height = height // N
    tile_width = width // M

    orig_x, orig_y = inverse_grt_coordinates_vectorized(M, N, a, b, c, d, rm, rn)
    flat_dst = (orig_y * M + orig_x).ravel()

    if tile_height == 1 and tile_width == 1:
        reconstructed_flat = np.empty_like(scrambled_array).reshape(N * M, -1)
        reconstructed_flat[flat_dst] = scrambled_array.reshape(N * M, -1)
        reconstructed_array = reconstructed_flat.reshape(scrambled_array.shape)
    else:
        rest = scrambled_array.shape[2:]
        tiles = scrambled_array.reshape(N, tile_height, M, tile_width, *rest).swapaxes(1, 2)
        tiles_flat = tiles.reshape(N * M, tile_height, tile_width, *rest)
        reconstructed_tiles = np.empty_like(tiles_flat)
        reconstructed_tiles[flat_dst] = tiles_flat
        reconstructed_array = (
            reconstructed_tiles.reshape(N, M, tile_height, tile_width, *rest)
            .swapaxes(1, 2)
            .reshape(scrambled_array.shape)
        )

    reconstructed_image = Image.fromarray(reconstructed_array, mode=scrambled_image.mode)
    if scrambled_image.mode == "P" and scrambled_image.getpalette() is not None:
        reconstructed_image.putpalette(scrambled_image.getpalette())

    return reconstructed_image

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