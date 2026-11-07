
(function () {
  "use strict";

  // Computes the greatest common divisor of two integers.
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

  //  Positive Euclidean modulo in [0, m - 1].
  function mod(n, m) {
    return ((n % m) + m) % m;
  }

  // Modular multiplicative inverse of a modulo m via Extended Euclidean Algorithm.
  function modInverse(a, m) {
    if (m === 1) return 0;

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

  //    Precomputes 1D TypedArray Lookup Tables (LUTs) for 4-Stage IGRT decryption
  //    (Lan & Wang 2025, Eq. 12-17). Hoists all gcd/modInverse/modulo operations
  //    outside the 2D grid loop.
  // Scalar inverse GRT coordinate mapping (Decryption, Lan & Wang 2025 Eq. 12-17)
  function inverseGRTCoordinate(xp, yp, M, N, a, b, c, d, rm, rn) {
    if (xp < 0 || xp >= M || yp < 0 || yp >= N) {
      throw new RangeError('Coordinates out of bounds: (' + xp + ', ' + yp + ') for grid ' + M + 'x' + N);
    }
    const p = gcd(M, N);
    const h = (M / p) | 0;
    const v = (N / p) | 0;
    const det = a * d - b * c;

    let x_p = 0;
    let y_p = 0;
    if (p > 1) {
      const detInvP = modInverse(det, p);
      const dx = mod(xp - rm, p);
      const dy = mod(yp - rn, p);
      x_p = mod(detInvP * (d * dx - b * dy), p);
      y_p = mod(detInvP * (-c * dx + a * dy), p);
    }

    const deltaX = (xp - rm) - (a * x_p + b * y_p);
    const deltaY = (yp - rn) - (c * x_p + d * y_p);
    const H = h > 1 ? mod(Math.floor(deltaX / p), h) : 0;
    const V = v > 1 ? mod(Math.floor(deltaY / p), v) : 0;

    const bModH = h > 1 ? mod(b, h) : 0;
    const cModV = v > 1 ? mod(c, v) : 0;
    const aInvH = h > 1 ? modInverse(a, h) : 0;
    const dInvV = v > 1 ? modInverse(d, v) : 0;

    let x_h = 0;
    let y_v = 0;
    if (bModH === 0 && cModV === 0) {
      x_h = h > 1 ? mod(aInvH * H, h) : 0;
      y_v = v > 1 ? mod(dInvV * V, v) : 0;
    } else if (bModH === 0 && cModV !== 0) {
      x_h = h > 1 ? mod(aInvH * H, h) : 0;
      y_v = v > 1 ? mod(dInvV * (V - c * x_h), v) : 0;
    } else {
      y_v = v > 1 ? mod(dInvV * V, v) : 0;
      x_h = h > 1 ? mod(aInvH * (H - b * y_v), h) : 0;
    }

    const x = x_p + p * x_h;
    const y = y_p + p * y_v;
    return [x, y];
  }

  function buildIGRTLookupTables(M, N, a, b, c, d, rm, rn) {
    const p = gcd(M, N);
    const h = (M / p) | 0;
    const v = (N / p) | 0;
    const det = a * d - b * c;

    const detInvP = p > 1 ? modInverse(det, p) : 0;
    const aInvH = h > 1 ? modInverse(a, h) : 0;
    const dInvV = v > 1 ? modInverse(d, v) : 0;

    const bModH = h > 1 ? mod(b, h) : 0;
    const cModV = v > 1 ? mod(c, v) : 0;
    if (bModH !== 0 && cModV !== 0) {
      throw new Error(
        `Invalid GRT parameters: expected (b % h === 0 || c % v === 0), got b%h=${bModH}, c%v=${cModV}`
      );
    }
    const caseType = bModH === 0 && cModV === 0 ? 1 : bModH === 0 ? 2 : 3;

    // 1D X-axis LUTs (length M)
    const dx0Arr = new Int32Array(M);
    const dxDArr = new Int32Array(M);
    const dxCArr = new Int32Array(M);
    const dModP = p > 1 ? mod(detInvP * d, p) : 0;
    const negBModP = p > 1 ? mod(-detInvP * b, p) : 0;
    const negCModP = p > 1 ? mod(-detInvP * c, p) : 0;
    const aModP = p > 1 ? mod(detInvP * a, p) : 0;

    for (let xp = 0; xp < M; xp++) {
      const dx0 = xp - rm;
      dx0Arr[xp] = dx0;
      if (p > 1) {
        const dx = ((dx0 % p) + p) % p;
        dxDArr[xp] = (dModP * dx) % p;
        dxCArr[xp] = (negCModP * dx) % p;
      }
    }

    // 1D Y-axis LUTs (length N)
    const dy0Arr = new Int32Array(N);
    const dyBArr = new Int32Array(N);
    const dyAArr = new Int32Array(N);
    for (let yp = 0; yp < N; yp++) {
      const dy0 = yp - rn;
      dy0Arr[yp] = dy0;
      if (p > 1) {
        const dy = ((dy0 % p) + p) % p;
        dyBArr[yp] = (negBModP * dy) % p;
        dyAArr[yp] = (aModP * dy) % p;
      }
    }

    // Folded Stage 2 + Stage 3 quotient lookup tables
    const minQx = -((h + a + b + 2) | 0);
    const maxQx = (h + 2) | 0;
    const offsetQx = -minQx;
    const xhFromQx = new Int32Array(maxQx - minQx + 1);
    for (let qx = minQx; qx <= maxQx; qx++) {
      const H = h > 1 ? ((qx % h) + h) % h : 0;
      xhFromQx[qx + offsetQx] = h > 1 ? (aInvH * H) % h : 0;
    }

    const minQy = -((v + c + d + 2) | 0);
    const maxQy = (v + 2) | 0;
    const offsetQy = -minQy;
    const yvFromQy = new Int32Array(maxQy - minQy + 1);
    for (let qy = minQy; qy <= maxQy; qy++) {
      const V = v > 1 ? ((qy % v) + v) % v : 0;
      yvFromQy[qy + offsetQy] = v > 1 ? (dInvV * V) % v : 0;
    }

    const cxhTerm = new Int32Array(h);
    for (let xh = 0; xh < h; xh++) {
      cxhTerm[xh] = v > 1 ? (dInvV * (v - ((c * xh) % v))) % v : 0;
    }

    const byvTerm = new Int32Array(v);
    for (let yv = 0; yv < v; yv++) {
      byvTerm[yv] = h > 1 ? (aInvH * (h - ((b * yv) % h))) % h : 0;
    }

    const pxhArr = new Int32Array(h);
    for (let xh = 0; xh < h; xh++) pxhArr[xh] = p * xh;

    const pyvArr = new Int32Array(v);
    for (let yv = 0; yv < v; yv++) pyvArr[yv] = p * yv;

    return {
      p,
      h,
      v,
      caseType,
      dx0Arr,
      dxDArr,
      dxCArr,
      dy0Arr,
      dyBArr,
      dyAArr,
      offsetQx,
      xhFromQx,
      offsetQy,
      yvFromQy,
      cxhTerm,
      byvTerm,
      pxhArr,
      pyvArr,
    };
  }

    // Descrambles a 32-bit RGBA pixel buffer (Uint32Array view over ImageData.data.buffer)
    // using the 1D-LUT vectorized 4-Stage IGRT.
  function descrambleBuffer32IGRT(
    src32,
    dst32,
    width,
    height,
    M,
    N,
    a,
    b,
    c,
    d,
    rm,
    rn
  ) {
    const tileW = (width / M) | 0;
    const tileH = (height / N) | 0;

    const {
      p,
      h,
      v,
      caseType,
      dx0Arr,
      dxDArr,
      dxCArr,
      dy0Arr,
      dyBArr,
      dyAArr,
      offsetQx,
      xhFromQx,
      offsetQy,
      yvFromQy,
      cxhTerm,
      byvTerm,
      pxhArr,
      pyvArr,
    } = buildIGRTLookupTables(M, N, a, b, c, d, rm, rn);

    for (let yp = 0; yp < N; yp++) {
      const dy0 = dy0Arr[yp];
      const dyB = dyBArr[yp];
      const dyA = dyAArr[yp];
      const srcBaseY = yp * tileH;

      for (let xp = 0; xp < M; xp++) {
        const dx0 = dx0Arr[xp];
        let x_p = 0;
        let y_p = 0;
        if (p > 1) {
          x_p = dxDArr[xp] + dyB;
          if (x_p >= p) x_p -= p;
          y_p = dxCArr[xp] + dyA;
          if (y_p >= p) y_p -= p;
        }

        const qx = ((dx0 - (a * x_p + b * y_p)) / p) | 0;
        const qy = ((dy0 - (c * x_p + d * y_p)) / p) | 0;

        let x_h = xhFromQx[qx + offsetQx];
        let y_v = yvFromQy[qy + offsetQy];

        if (caseType === 2) {
          y_v += cxhTerm[x_h];
          if (y_v >= v) y_v -= v;
        } else if (caseType === 3) {
          x_h += byvTerm[y_v];
          if (x_h >= h) x_h -= h;
        }

        const x = x_p + pxhArr[x_h];
        const y = y_p + pyvArr[y_v];

        if (tileW === 1 && tileH === 1) {
          dst32[y * width + x] = src32[yp * width + xp];
        } else {
          const dstBaseY = y * tileH;
          const srcBaseX = xp * tileW;
          const dstBaseX = x * tileW;
          for (let r = 0; r < tileH; r++) {
            const sOff = (srcBaseY + r) * width + srcBaseX;
            const dOff = (dstBaseY + r) * width + dstBaseX;
            for (let col = 0; col < tileW; col++) {
              dst32[dOff + col] = src32[sOff + col];
            }
          }
        }
      }
    }
  }

    // Descrambles a tiled image using 1D-LUT vectorized 4-Stage IGRT and renders
    // the reconstructed image onto an HTML5 Canvas.
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
    rn,
    origWidth,
    origHeight
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

    const finalWidth = (typeof origWidth === "number" && origWidth > 0 && origWidth <= width) ? origWidth : width;
    const finalHeight = (typeof origHeight === "number" && origHeight > 0 && origHeight <= height) ? origHeight : height;

    // 1. Canvas is initially sized to full width x height to read the complete scrambled image without clipping
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

    ctx.imageSmoothingEnabled = false;

    if (typeof ctx.getImageData === 'function' && typeof ctx.createImageData === 'function' && typeof ctx.putImageData === 'function') {
      ctx.drawImage(scrambledImageSource, 0, 0, width, height);
      const srcImageData = ctx.getImageData(0, 0, width, height);
      const dstImageData = ctx.createImageData(width, height);

      const src32 = new Uint32Array(
        srcImageData.data.buffer,
        srcImageData.data.byteOffset,
        width * height
      );
      const dst32 = new Uint32Array(
        dstImageData.data.buffer,
        dstImageData.data.byteOffset,
        width * height
      );

      descrambleBuffer32IGRT(
        src32,
        dst32,
        width,
        height,
        M,
        N,
        a,
        b,
        c,
        d,
        rm,
        rn
      );

      // 2. If original unpadded dimensions are specified and smaller than grid, resize canvas and crop cleanly
      if (finalWidth !== width || finalHeight !== height) {
        targetCanvas.width = finalWidth;
        targetCanvas.height = finalHeight;
        const finalImageData = ctx.createImageData(finalWidth, finalHeight);
        const final32 = new Uint32Array(finalImageData.data.buffer);
        for (let r = 0; r < finalHeight; r++) {
          final32.set(dst32.subarray(r * width, r * width + finalWidth), r * finalWidth);
        }
        ctx.putImageData(finalImageData, 0, 0);
      } else {
        ctx.putImageData(dstImageData, 0, 0);
      }
    } else {
      const tileWidth = (width / M) | 0;
      const tileHeight = (height / N) | 0;
      for (let yp = 0; yp < N; yp++) {
        for (let xp = 0; xp < M; xp++) {
          const [x, y] = inverseGRTCoordinate(xp, yp, M, N, a, b, c, d, rm, rn);
          ctx.drawImage(
            scrambledImageSource,
            xp * tileWidth,
            yp * tileHeight,
            tileWidth,
            tileHeight,
            x * tileWidth,
            y * tileHeight,
            tileWidth,
            tileHeight
          );
        }
      }
      if (finalWidth !== width || finalHeight !== height) {
        const croppedData = ctx.getImageData(0, 0, finalWidth, finalHeight);
        targetCanvas.width = finalWidth;
        targetCanvas.height = finalHeight;
        ctx.putImageData(croppedData, 0, 0);
      }
    }
  }

  const GRT = {
    gcd,
    mod,
    modInverse,
    inverseGRTCoordinate,
    buildIGRTLookupTables,
    descrambleBuffer32IGRT,
    descrambleCanvasGRT,
  };

  if (typeof window !== "undefined") {
    window.GRT = GRT;
    window.descrambleCanvasGRT = descrambleCanvasGRT;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = GRT;
  }
})();