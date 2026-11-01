
(function () {
  "use strict";

  /**
   * Computes the greatest common divisor of two integers.
   *
   * @param {number} a
   * @param {number} b
   * @returns {number} Greatest common divisor (>= 0)
   */
  function gcd(a, b) {
    let x = Math.abs(Math.trunc(a));
    let y = Math.abs(Math.trunc(b));
    while (y !== 0) {
      const temp = y;
      y = x % y;
      x = temp;
    }
    return x;
  }

  /**
   * Robust Euclidean positive modulo operation.
   * Standard JavaScript `%` operator retains negative signs (e.g. -5 % 3 === -2).
   * This helper normalizes results into the range [0, m - 1].
   *
   * @param {number} n - Dividend
   * @param {number} m - Positive divisor (modulus)
   * @returns {number} Canonical residue in [0, m - 1]
   */
  function mod(n, m) {
    return ((n % m) + m) % m;
  }

  /**
   * Computes the modular multiplicative inverse of a modulo m using
   * the Extended Euclidean Algorithm.
   *
   * For the trivial quotient ring Z/1Z (m === 1), returns 0.
   *
   * @param {number} a - Integer base
   * @param {number} m - Positive modulus (>= 1)
   * @returns {number} Modular inverse in range [0, m - 1]
   * @throws {RangeError} If gcd(a, m) !== 1 when m > 1
   */
  function modInverse(a, m) {
    if (m === 1) {
      return 0;
    }

    let oldR = mod(a, m);
    let r = m;
    let oldS = 1;
    let s = 0;

    while (r !== 0) {
      const quotient = Math.floor(oldR / r);
      const tempR = oldR - quotient * r;
      oldR = r;
      r = tempR;

      const tempS = oldS - quotient * s;
      oldS = s;
      s = tempS;
    }

    if (oldR !== 1) {
      throw new RangeError(
        `Modular inverse does not exist: gcd(${a}, ${m}) = ${oldR} !== 1`
      );
    }

    return mod(oldS, m);
  }

  /**
   * Validates parameters (M, N, a, b, c, d, rm, rn) according to
   * Lan & Wang (2025) Equations 2 and 10.
   *
   * @param {number} M - Grid width (number of tile columns), M >= 1
   * @param {number} N - Grid height (number of tile rows), N >= 1
   * @param {number} a - GRT parameter a >= 0
   * @param {number} b - GRT parameter b >= 0
   * @param {number} c - GRT parameter c >= 0
   * @param {number} d - GRT parameter d >= 0
   * @param {number} rm - Horizontal offset, 0 <= rm < M
   * @param {number} rn - Vertical offset, 0 <= rn < N
   * @returns {{ valid: boolean, reason: string }}
   */
  function validateGRTParameters(M, N, a, b, c, d, rm, rn) {
    const params = [
      ["M", M],
      ["N", N],
      ["a", a],
      ["b", b],
      ["c", c],
      ["d", d],
      ["rm", rm],
      ["rn", rn],
    ];

    for (let i = 0; i < params.length; i++) {
      const [name, val] = params[i];
      if (!Number.isInteger(val)) {
        return {
          valid: false,
          reason: `Parameter ${name} must be an integer`,
        };
      }
    }

    if (M < 1 || N < 1) {
      return {
        valid: false,
        reason: `Grid dimensions M and N must be >= 1, got M=${M}, N=${N}`,
      };
    }

    if (a < 0 || b < 0 || c < 0 || d < 0) {
      return {
        valid: false,
        reason: `Matrix parameters a, b, c, d must be >= 0, got a=${a}, b=${b}, c=${c}, d=${d}`,
      };
    }

    if (rm < 0 || rm >= M || rn < 0 || rn >= N) {
      return {
        valid: false,
        reason: `Offset coordinates (rm, rn) must satisfy 0 <= rm < M and 0 <= rn < N, got rm=${rm} (M=${M}), rn=${rn} (N=${N})`,
      };
    }

    const p = gcd(M, N);
    const h = Math.floor(M / p);
    const v = Math.floor(N / p);
    const det = a * d - b * c;

    // Condition 1: b % h == 0 or c % v == 0
    if (mod(b, h) !== 0 && mod(c, v) !== 0) {
      return {
        valid: false,
        reason: `Violated Lan & Wang Eq (2) Condition 1: expected (b % h === 0 || c % v === 0), got b%h=${mod(b, h)}, c%v=${mod(c, v)}`,
      };
    }

    // Condition 2: gcd(|G|, p) == 1
    if (gcd(det, p) !== 1) {
      return {
        valid: false,
        reason: `Violated Lan & Wang Eq (2) Condition 2: expected gcd(|G|, p) === 1, got gcd(${det}, ${p}) = ${gcd(det, p)}`,
      };
    }

    // Condition 3: gcd(a, h) == 1
    if (gcd(a, h) !== 1) {
      return {
        valid: false,
        reason: `Violated Lan & Wang Eq (2) Condition 3: expected gcd(a, h) === 1, got gcd(${a}, ${h}) = ${gcd(a, h)}`,
      };
    }

    // Condition 4: gcd(d, v) == 1
    if (gcd(d, v) !== 1) {
      return {
        valid: false,
        reason: `Violated Lan & Wang Eq (2) Condition 4: expected gcd(d, v) === 1, got gcd(${d}, ${v}) = ${gcd(d, v)}`,
      };
    }

    return { valid: true, reason: "Valid GRT parameters" };
  }

  /**
   * Computes forward GRT affine coordinate mapping (Lan & Wang 2025, Eq 2 & 10).
   *
   * x_{n+1} = (a * x_n + b * y_n + rm) mod M
   * y_{n+1} = (c * x_n + d * y_n + rn) mod N
   *
   * @param {number} x - Original column index [0, M - 1]
   * @param {number} y - Original row index [0, N - 1]
   * @param {number} M - Grid width (number of tile columns)
   * @param {number} N - Grid height (number of tile rows)
   * @param {number} a - GRT matrix coefficient (0, 0)
   * @param {number} b - GRT matrix coefficient (0, 1)
   * @param {number} c - GRT matrix coefficient (1, 0)
   * @param {number} d - GRT matrix coefficient (1, 1)
   * @param {number} rm - Horizontal translation offset
   * @param {number} rn - Vertical translation offset
   * @returns {[number, number]} Transformed coordinates [x_next, y_next]
   */
  function forwardGRTCoordinate(x, y, M, N, a, b, c, d, rm, rn) {
    if (x < 0 || x >= M || y < 0 || y >= N) {
      throw new RangeError(
        `Coordinate (${x}, ${y}) is outside valid grid bounds [0, ${M}) x [0, ${N})`
      );
    }

    const xNext = mod(a * x + b * y + rm, M);
    const yNext = mod(c * x + d * y + rn, N);
    return [xNext, yNext];
  }

  /**
   * Computes inverse GRT coordinate mapping using exact 4-stage IGRT
   * (Lan & Wang 2025, Eq 12-17).
   *
   * @param {number} xp - Scrambled column index [0, M - 1]
   * @param {number} yp - Scrambled row index [0, N - 1]
   * @param {number} M - Grid width (number of tile columns)
   * @param {number} N - Grid height (number of tile rows)
   * @param {number} a - GRT matrix coefficient (0, 0)
   * @param {number} b - GRT matrix coefficient (0, 1)
   * @param {number} c - GRT matrix coefficient (1, 0)
   * @param {number} d - GRT matrix coefficient (1, 1)
   * @param {number} rm - Horizontal translation offset
   * @param {number} rn - Vertical translation offset
   * @returns {[number, number]} Reconstructed original coordinates [x, y]
   */
  function inverseGRTCoordinate(xp, yp, M, N, a, b, c, d, rm, rn) {
    if (xp < 0 || xp >= M || yp < 0 || yp >= N) {
      throw new RangeError(
        `Coordinate (${xp}, ${yp}) is outside valid grid bounds [0, ${M}) x [0, ${N})`
      );
    }

    const p = gcd(M, N);
    const h = Math.floor(M / p);
    const v = Math.floor(N / p);
    const det = a * d - b * c;

    // Stage 1: Equilateral inverse mapping modulo p (Lan & Wang 2025, Eq 12)
    let x_p = 0;
    let y_p = 0;
    if (p > 1) {
      const detInvP = modInverse(det, p);
      const dx = mod(xp - rm, p);
      const dy = mod(yp - rn, p);
      x_p = mod(detInvP * (d * dx - b * dy), p);
      y_p = mod(detInvP * (-c * dx + a * dy), p);
    }

    // Stage 2: Inverse projection mapping (Lan & Wang 2025, Eq 13 & Table 6)
    const deltaX = (xp - rm) - (a * x_p + b * y_p);
    const deltaY = (yp - rn) - (c * x_p + d * y_p);
    const H = h > 1 ? mod(Math.floor(deltaX / p), h) : 0;
    const V = v > 1 ? mod(Math.floor(deltaY / p), v) : 0;

    // Stage 3: Inverse triangular mapping (Lan & Wang 2025, Eq 14, 15, 16)
    let x_h = 0;
    let y_v = 0;

    const bModH = h > 1 ? mod(b, h) : 0;
    const cModV = v > 1 ? mod(c, v) : 0;

    if (bModH === 0 && cModV === 0) {
      // Case 1 (Diagonal system, Eq 14)
      x_h = h > 1 ? mod(modInverse(a, h) * H, h) : 0;
      y_v = v > 1 ? mod(modInverse(d, v) * V, v) : 0;
    } else if (bModH === 0 && cModV !== 0) {
      // Case 2 (Lower triangular system, Eq 15)
      x_h = h > 1 ? mod(modInverse(a, h) * H, h) : 0;
      y_v = v > 1 ? mod(modInverse(d, v) * (V - c * x_h), v) : 0;
    } else if (bModH !== 0 && cModV === 0) {
      // Case 3 (Upper triangular system, Eq 16)
      y_v = v > 1 ? mod(modInverse(d, v) * V, v) : 0;
      x_h = h > 1 ? mod(modInverse(a, h) * (H - b * y_v), h) : 0;
    } else {
      throw new Error(
        `Invalid GRT parameters: violates Condition 1 ((b % h == 0) || (c % v == 0)). Got b%h=${bModH}, c%v=${cModV}`
      );
    }

    // Stage 4: CRT assembly / Coordinate reconstruction (Lan & Wang 2025, Eq 17)
    const x = x_p + p * x_h;
    const y = y_p + p * y_v;

    return [x, y];
  }

  /**
   * Descrambles a tiled image using Inverse Generalized Rectangular Transform (IGRT)
   * and renders the reconstructed image directly onto an HTML5 Canvas.
   *
   * For each scrambled tile position (xp, yp), the original coordinate (x, y) is
   * computed using inverseGRTCoordinate, and the tile is drawn to the target canvas.
   * Image smoothing is explicitly disabled to guarantee lossless pixel preservation.
   *
   * @param {CanvasImageSource} scrambledImageSource - Scrambled image source (HTMLImageElement, HTMLCanvasElement, etc.)
   * @param {HTMLCanvasElement} targetCanvas - Target canvas element to render reconstructed image
   * @param {number} M - Grid width (number of tile columns)
   * @param {number} N - Grid height (number of tile rows)
   * @param {number} a - GRT matrix coefficient (0, 0)
   * @param {number} b - GRT matrix coefficient (0, 1)
   * @param {number} c - GRT matrix coefficient (1, 0)
   * @param {number} d - GRT matrix coefficient (1, 1)
   * @param {number} rm - Horizontal translation offset
   * @param {number} rn - Vertical translation offset
   */
  function descrambleCanvasGRT(
    scrambledImageSource,
    targetCanvas,
    M,
    N,
    a,
    b,
    c,
    d,
    rm,
    rn
  ) {
    if (!targetCanvas || typeof targetCanvas.getContext !== "function") {
      throw new TypeError("targetCanvas must be a valid HTMLCanvasElement");
    }

    const width =
      scrambledImageSource.naturalWidth || scrambledImageSource.width;
    const height =
      scrambledImageSource.naturalHeight || scrambledImageSource.height;

    if (!width || !height) {
      throw new Error("Unable to determine dimensions of scrambledImageSource");
    }

    if (width % M !== 0 || height % N !== 0) {
      throw new RangeError(
        `Image dimensions (${width}x${height}) must be cleanly divisible by grid dimensions (${M}x${N})`
      );
    }

    // Resize canvas if necessary to match source image
    if (targetCanvas.width !== width) {
      targetCanvas.width = width;
    }
    if (targetCanvas.height !== height) {
      targetCanvas.height = height;
    }

    const ctx = targetCanvas.getContext("2d");
    if (!ctx) {
      throw new Error("Unable to acquire 2D rendering context from targetCanvas");
    }

    // Disable image smoothing for 100% pixel-exact tile spatial blitting
    ctx.imageSmoothingEnabled = false;

    const tileWidth = width / M;
    const tileHeight = height / N;

    // Iterate over every scrambled tile position (xp, yp)
    for (let yp = 0; yp < N; yp++) {
      for (let xp = 0; xp < M; xp++) {
        // Map scrambled tile coordinate (xp, yp) to original position [x, y]
        const [x, y] = inverseGRTCoordinate(xp, yp, M, N, a, b, c, d, rm, rn);

        const srcX = xp * tileWidth;
        const srcY = yp * tileHeight;
        const dstX = x * tileWidth;
        const dstY = y * tileHeight;

        ctx.drawImage(
          scrambledImageSource,
          srcX,
          srcY,
          tileWidth,
          tileHeight,
          dstX,
          dstY,
          tileWidth,
          tileHeight
        );
      }
    }
  }

  // Export module interface
  const GRT = {
    gcd,
    mod,
    modInverse,
    validateGRTParameters,
    forwardGRTCoordinate,
    inverseGRTCoordinate,
    descrambleCanvasGRT,
  };

  // Browser environment export
  if (typeof window !== "undefined") {
    window.GRT = GRT;
    window.inverseGRTCoordinate = inverseGRTCoordinate;
    window.forwardGRTCoordinate = forwardGRTCoordinate;
    window.validateGRTParameters = validateGRTParameters;
    window.descrambleCanvasGRT = descrambleCanvasGRT;
  }

  // Node.js CommonJS environment export
  if (typeof module !== "undefined" && module.exports) {
    module.exports = GRT;
  }
})();
