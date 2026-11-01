## This markdown file is converted from hand-written theoretical background and mathematical derivations on GRT and SRT folders

# SRT and GRT — Handwritten Notes

## Part I: SRT and ISRT (`docs/SRT/1.jpg` – `2.jpg`)

### Page 1 (`docs/SRT/1.jpg`)

#### 1. Forward Special Rectangular Transform (SRT) Formulation
- $\hookrightarrow R = \begin{bmatrix} 1 & r \\ s & rs + 1 \end{bmatrix}$
  - $\hookrightarrow \begin{bmatrix} x \\ y \end{bmatrix}_{n+1} = \begin{bmatrix} 1 & r \\ s & rs + 1 \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix}_n \bmod \begin{bmatrix} M \\ N \end{bmatrix} = R \begin{bmatrix} x \\ y \end{bmatrix}_n \bmod \begin{bmatrix} M \\ N \end{bmatrix}$
  - $\hookrightarrow$ Scalar coordinate equations:
    $$\begin{cases} x_{n+1} = (x_n + r \cdot y_n) \bmod M \\ y_{n+1} = (s \cdot x_n + (rs + 1) \cdot y_n) \bmod N \end{cases}$$

#### 2. Detailed Terminology & Variable Definitions
- $\hookrightarrow M, N$: Image grid dimensions (or tile counts).
  - $M$: Total horizontal pixel dimension (width) or number of tile columns in the grid ($x \in \mathbb{Z}_M = \{0, 1, \dots, M-1\}$).
  - $N$: Total vertical pixel dimension (height) or number of tile rows in the grid ($y \in \mathbb{Z}_N = \{0, 1, \dots, N-1\}$).
- $\hookrightarrow (x_n, y_n)$: Original (plaintext) coordinate pair at iteration $n$.
- $\hookrightarrow (x_{n+1}, y_{n+1})$: Scrambled (ciphertext) coordinate pair at iteration $n+1$.
- $\hookrightarrow p = \gcd(M, N)$: The Greatest Common Divisor of $M$ and $N$.
  - Represents the fundamental shared scale factor or the largest equilateral (square) block dimension underlying the rectangular grid.
- $\hookrightarrow h, v$: The normalized aspect factors.
  - $h = \frac{M}{p}$: Horizontal aspect quotient (width factor).
  - $v = \frac{N}{p}$: Vertical aspect quotient (height factor).
  - The ratio $h : v$ represents the irreducible aspect ratio of the image, satisfying $\gcd(h, v) = 1$.
  - *Example:* For a $768 \times 512$ image, $p = \gcd(768, 512) = 256$, giving $h = 768 / 256 = 3$ and $v = 512 / 256 = 2$ (aspect ratio $3 : 2$).
- $\hookrightarrow r, s \in \mathbb{Z}^+$: Positive integer transformation parameters (shearing keys).
  - $r$: Horizontal shear coefficient, controlling how much the vertical position $y_n$ shifts the horizontal coordinate $x_{n+1}$.
  - $s$: Vertical shear coefficient, controlling how much the horizontal position $x_n$ shifts the vertical coordinate $y_{n+1}$.
- $\hookrightarrow R$: The $2 \times 2$ Special Rectangular Transform permutation matrix.

#### 3. Deconstructing Condition 5: Why We Choose $(r \bmod h = 0 \lor s \bmod v = 0)$ and $\gcd(rs + 1, v) = 1$

##### A. The Modulus Decoupling Condition: We choose $r$ and $s$ such that $(r \bmod h = 0)$ or $(s \bmod v = 0)$
*(Note: Written with a minor typo as $(r \bmod v) = 0$ in original handwritten note; corrected to $(r \bmod h = 0)$ per Lan & Wang Equation 5).*

- **Purpose:** Eliminates cross-modulus wrap contamination during decryption.
- **Why this condition is necessary:**
  When $M \neq N$, the forward transformation wraps around two distinct modular boundaries:
  $$\begin{cases} x_n + r \cdot y_n = x_{n+1} + k_1 M & \text{where } k_1 = \left\lfloor \frac{x_n + r y_n}{M} \right\rfloor \text{ (horizontal wrap count)} \\ s \cdot x_n + (rs + 1) y_n = y_{n+1} + k_2 N & \text{where } k_2 = \left\lfloor \frac{s x_n + (rs + 1) y_n}{N} \right\rfloor \text{ (vertical wrap count)} \end{cases}$$
  To invert the transformation and isolate $y_n$, we eliminate $x_n$ by computing $(y_{n+1} - s \cdot x_{n+1})$:
  $$y_{n+1} - s \cdot x_{n+1} = \left[ s x_n + (rs + 1) y_n - k_2 N \right] - s \left[ x_n + r y_n - k_1 M \right] = y_n - k_2 N + s k_1 M$$
  Taking this equation modulo $N$:
  $$(y_{n+1} - s \cdot x_{n+1}) \equiv y_n + s k_1 M \pmod N$$
  Notice the contaminated term $+ s k_1 M \pmod N$. We do not know the integer wrap count $k_1$ during decryption because computing $k_1$ requires the original coordinate $(x_n, y_n)$.
- **How choosing $s \bmod v = 0$ eliminates $k_1$:**
  We choose $s$ to be an exact integer multiple of $v$, so $s = k_s \cdot v$ for some integer $k_s \ge 1$.
  Substituting $M = p \cdot h$ and $N = p \cdot v$:
  $$s k_1 M = (k_s \cdot v) \cdot k_1 \cdot (p \cdot h) = (k_s \cdot k_1 \cdot h) \cdot (p \cdot v) = (k_s \cdot k_1 \cdot h) \cdot N$$
  Taking this modulo $N$:
  $$(k_s \cdot k_1 \cdot h) \cdot N \equiv 0 \pmod N$$
  The unknown wrap count $k_1$ vanishes completely!
  As a result:
  $$(y_{n+1} - s \cdot x_{n+1}) \equiv y_n \pmod N \implies y_n = (y_{n+1} - s \cdot x_{n+1}) \bmod N$$
- **Dual choice:** Symmetrically, if we instead choose $r$ such that $r \bmod h = 0$ (i.e. $r = k_r \cdot h$), the cross-modulus error term $r k_2 N \equiv 0 \pmod M$ vanishes in the dual direction, allowing $x_n$ to be derived first.

##### B. The Diagonal Coprimality Condition: We choose $s$ such that $\gcd(rs + 1, v) = 1$
- **Purpose:** Guarantees bijectivity along the vertical quotient ring $\mathbb{Z}_v$.
- **Why this condition is necessary:**
  The lower-right diagonal element is $d = rs + 1$. In the vertical coordinate projection modulo $v$, the multiplier $(rs + 1)$ maps row coordinates to row coordinates.
  If $\gcd(rs + 1, v) > 1$, $(rs + 1)$ would share common factors with $v$, lacking a modular inverse modulo $v$. Multiple row indices would map into the same row modulo $v$, causing coordinate collisions.
  Enforcing $\gcd(rs + 1, v) = 1$ guarantees that the vertical coordinate mapping is a complete permutation without row collisions.

#### 4. Why the Naïve Matrix Inverse Fails
- $\hookrightarrow R^{-1} \neq \begin{bmatrix} rs + 1 & -r \\ -s & 1 \end{bmatrix}$ *(naïve matrix inverse crossed out)*
  - Over continuous space $\mathbb{R}^2$ or on a uniform square grid $\mathbb{Z}_N^2$, the standard inverse is $R^{-1} = \begin{bmatrix} rs + 1 & -r \\ -s & 1 \end{bmatrix}$ because $\det(R) = 1$.
  - However, on a non-square domain $\mathbb{Z}_M \times \mathbb{Z}_N$ with $M \neq N$, multiplying the vector $[x_{n+1}, y_{n+1}]^T$ by $R^{-1}$ creates mixed linear combinations:
    $$x_n' = ((rs + 1) x_{n+1} - r y_{n+1}) \bmod M$$
    Because $x_{n+1}$ was reduced modulo $M$ while $y_{n+1}$ was reduced modulo $N$, their integer wrap boundaries are mismatched. This causes naïve matrix inversion to produce incorrect coordinates for all pixels except the origin.

#### 5. Step-by-Step Inverse (ISRT - Equation 6)
- $\hookrightarrow \begin{cases} y_n = (y_{n+1} - s \cdot x_{n+1}) \bmod N \\ x_n = (x_{n+1} - r \cdot y_n) \bmod M \end{cases}$
  - **Step 1:** Compute $y_n$ directly using $(y_{n+1} - s \cdot x_{n+1}) \bmod N$. This is possible because the cross-modulus condition eliminated the $k_1$ wrap term.
  - **Step 2:** Substitute the recovered $y_n$ into the horizontal equation:
    $$x_{n+1} \equiv x_n + r \cdot y_n \pmod M \implies x_n = (x_{n+1} - r \cdot y_n) \bmod M$$
  - Inversion requires only 2 multiplications, 2 subtractions, and 2 modulos, executing in exact $\mathcal{O}(1)$ time.

### Page 2 (`docs/SRT/2.jpg`)

#### 6. Determinant, Area Preservation, and Bijectivity Proof
- $\hookrightarrow$ **The Determinant $\det(R) = 1$:**
  $$\det(R) = 1 \cdot (rs + 1) - r \cdot s = rs + 1 - rs = 1$$
- $\hookrightarrow$ **Strict Area Preservation:**
  - The matrix $R$ is unimodular ($\det(R) = 1$), placing it in the special linear group $\mathrm{SL}(2, \mathbb{Z})$.
  - In geometric terms, the transformation preserves the coordinate grid's discrete phase space area.
  - The total number of coordinate positions ($M \times N$) is strictly conserved.
  - The operation functions strictly as a pure spatial permutation (rearranging tiles or pixels) rather than scaling, interpolating, or compressing the image.
- $\hookrightarrow$ **Bijectivity (One-to-One and Onto):**
  Having $\det(R) = 1$ combined with Condition 5 guarantees exact mathematical reversibility:
  - **Injective (One-to-One):** No two original coordinates $(x_1, y_1) \neq (x_2, y_2)$ collide into the same destination coordinate $(x', y')$. Zero pixel or tile overwriting occurs.
  - **Surjective (Onto):** Every destination coordinate in the $M \times N$ domain is mapped to by exactly one source coordinate. No empty holes or unmapped pixels exist.
  - **Lossless Inversion:** Guarantees $100\%$ lossless reversible decryption ($\text{MSE} = 0.0, \text{PSNR} = \infty$).

#### 7. The Invariant Fixed-Point Vulnerability (Motivation for GRT)
- $\hookrightarrow$ **The Stationary Origin Flaw:**
  Because the Special Rectangular Transform (SRT) is a linear homogeneous transformation without an affine translation vector, evaluating the forward transform at coordinate $(x_n, y_n) = (0, 0)$ yields:
  $$\begin{cases} x_{n+1} = (1 \cdot 0 + r \cdot 0) \bmod M = 0 \\ y_{n+1} = (s \cdot 0 + (rs + 1) \cdot 0) \bmod N = 0 \end{cases}$$
  Consequently, the origin coordinate always maps to itself:
  $$[0, 0]^T \to [0, 0]^T$$
- $\hookrightarrow$ **Security Implication in Anti-Scraping Image Protection:**
  In tile transposition systems, **the top-left tile at $(0, 0)$ never moves**, regardless of how many iterations or what values of $(r, s)$ are used.
  An automated web scraper or computer vision puzzle solver can immediately identify the top-left tile as an uncorrupted anchor to align neighboring tiles and reconstruct the image.
- $\hookrightarrow$ **Transition to Generalized Rectangular Transform (GRT):**
  This vulnerability motivates the upgrade to GRT in Part II, which introduces a dynamic translation offset vector $(r_m, r_n)$ to displace $(0, 0) \to (r_m, r_n)$, ensuring that every tile in the grid is displaced.

## Part II: GRT and IGRT (`docs/GRT/1.jpg` – `12.jpg`)

### Page 1: The Fundamental Setup (`docs/GRT/1.jpg`)

Let $p = \gcd(M, N)$
- $\hookrightarrow M$ and $N$ are the image horizontal pixel size and vertical pixel size, respectively.
- $\hookrightarrow p$: shared scale factor.

Then we propose the ratio $h : v$, which is the irreducible aspect ratio of an image:
- $\hookrightarrow h = \frac{M}{p} \ ; \ v = \frac{N}{p}$
- $\hookrightarrow$ For e.g.: a $1920 \times 1080$ image has the $h : v = 16 : 9$ ratio (with $p = 120$).

#### The Forward Rectangular Transform is:

$$\begin{bmatrix} x' \\ y' \end{bmatrix} = \left( \begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} + \begin{bmatrix} r_m \\ r_n \end{bmatrix} \right) \bmod \begin{bmatrix} M \\ N \end{bmatrix} \qquad \text{(I)}$$

- $\hookrightarrow \begin{cases} x' = (ax + by + r_m) \pmod M \\ y' = (cx + dy + r_n) \pmod N \end{cases} \qquad \text{(I)}$
- $\hookrightarrow x', y'$: new positions from $x$ and $y$.
- $\hookrightarrow a, b, c$ and $d \in \mathbb{Z}_M^+$ and must satisfy 4 conditions:
  - $\hookrightarrow$ **(1)** $(b \bmod h = 0)$ or $(c \bmod v = 0)$
  - $\hookrightarrow$ **(2)** $\gcd(\|G\|, p) = 1$
    - $\hookrightarrow$ The rectangular transformation matrix:
      $$G = \begin{bmatrix} a & b \\ c & d \end{bmatrix} \ ; \ \|G\| = \det(G)$$
  - $\hookrightarrow$ **(3)** $\gcd(a, h) = 1$
  - $\hookrightarrow$ **(4)** $\gcd(d, v) = 1$

### Page 2: Deconstructing the 4 Conditions (`docs/GRT/2.jpg`)

#### (1) $(b \bmod h = 0)$ or $(c \bmod v = 0)$
- $\hookrightarrow$ Prevents the horizontal and vertical moduli from contaminating each other.
- $\hookrightarrow$ **Mathematical proof:**
  - $\hookrightarrow$ When doing decryption (inverting the forward transform):
    $$\begin{cases} ax + by = x' + k_1 M & \text{where } k_1\text{: horizontal wrap counts} \\ cx + dy = y' + k_2 N & \text{where } k_2\text{: vertical wrap counts} \end{cases}$$
  - When solving for $x$:
    - $\hookrightarrow (ad - bc)x = dx' - by' + d k_1 M - b k_2 N$
  - Reducing modulo $M$:
    - $\hookrightarrow (ad - bc)x \equiv dx' - by' - b k_2 N \pmod M$
  - We can see that $b k_2 N \not\equiv 0 \pmod M$. To find $x$, we need $k_2$, but:
    $$k_2 = \left\lfloor \frac{cx + dy}{N} \right\rfloor$$
    - $\hookrightarrow$ To find $k_2$, we need the original $(x, y)$ — which is the very first thing we are trying to decrypt.
  - So the condition $(b \bmod h = 0)$ eliminates the term "$b k_2 N$" by:
    - $\hookrightarrow$ Substitute $N = p v$, $M = p h$, and $b = k_b \cdot h$:
      1. $b k_2 N = k_2 (k_b h)(p v) = k_2 \cdot k_b v \cdot M$
      2. Now reduce modulo $M$:
         $$k_2 k_b v \cdot M \equiv 0 \pmod M$$
         $\implies$ The unknown wrap count $k_2$ vanishes completely.
- $\hookrightarrow$ If instead $c \bmod v = 0$, the identical cancellation happens in decryption for the $y$-condition.

### Page 3: Condition (2) (`docs/GRT/3.jpg`)

#### (2) $\gcd(\|G\|, p) = 1$
- $\hookrightarrow$ **Purpose:** Guarantees that the matrix is non-singular (invertible) over the shared divisor $p$.
- $\hookrightarrow$ **Step-by-step Mathematical Derivation:**
  1. From (I), since $M = p \cdot h$ and $N = p \cdot v$ are both multiples of $p$, take both forward equations (encryption) and reduce them to $\bmod p$:
     $$\begin{cases} x' \equiv ax + by \pmod p \\ y' \equiv cx + dy \pmod p \end{cases}$$
     $\hookrightarrow$
     $$\begin{cases} (ad - bc)x \equiv dx' - by' \pmod p \\ (ad - bc)y \equiv -cx' + ay' \pmod p \end{cases}$$
     Since the matrix determinant is $\|G\| = \det(G) = (ad - bc)$:
     $$\begin{cases} \|G\| \cdot x \equiv dx' - by' \pmod p \\ \|G\| \cdot y \equiv -cx' + ay' \pmod p \end{cases}$$
  2. To solve for $(x \bmod p)$ and $(y \bmod p)$, we must divide by $\|G\|$ modulo $p$ — a.k.a. the modular multiplicative inverse, $\|G\|^{-1} \bmod p$, which exists iff $\gcd(\|G\|, p) = 1$.
- $\hookrightarrow$ **What if $\gcd(\|G\|, p) > 1$?**
  - $\hookrightarrow$ We cannot divide by $\|G\| \pmod p$, which causes multiple $(x, y)$ pairs to produce the exact same $(x' \bmod p, y' \bmod p)$, permanently overwriting pixels.

### Page 4: Conditions (3) & (4) (`docs/GRT/4.jpg`)

#### (3) & (4) $\gcd(a, h) = 1$ and $\gcd(d, v) = 1$
- $\hookrightarrow$ **Purpose:** Guarantees a **one-to-one column mapping** across the horizontal aspect ratio $h$ and a **one-to-one row mapping** across the vertical aspect ratio $v$, respectively.
- $\hookrightarrow$ **Mathematical Derivation:**
  1. From (I), reduce the forward equations to modulo $h$ and $v$:
     $$\begin{cases} x' \equiv ax + by \pmod h \\ y' \equiv cx + dy \pmod v \end{cases}$$
     - **Case 1 $\rightarrow$** If $b \bmod h = 0$ from Condition 1:
       - $\hookrightarrow b \equiv 0 \pmod h \implies by \equiv 0 \pmod h$
       - $\hookrightarrow$ We can completely recover the exact integer $x \in \{0, \dots, M - 1\}$ first. Then since $x$ is now a known constant, we simply subtract $cx$ from both sides:
         $$\begin{cases} x' \equiv ax \pmod h \\ (y' - cx) \equiv dy \pmod v \end{cases}$$
     - **Case 2 $\rightarrow$** If we choose $c \bmod v = 0$, we can find $y$ first, then:
       $$\begin{cases} (x' - by) \equiv ax \pmod h \\ y' \equiv dy \pmod v \end{cases}$$
  2. In both cases, to recover $(x \bmod h)$ from $(x' \bmod h)$ or $(x' - by \bmod h)$, we must divide by $a$ modulo $h$ (multiply by $a^{-1} \bmod h$).
  3. In both cases, to recover $(y \bmod v)$ from $(y' \bmod v)$ or $(y' - cx \bmod v)$, we must divide by $d$ modulo $v$ (multiply by $d^{-1} \bmod v$).
  - $\implies$ By what we have learnt from our course, the conclusion is:
    $$\begin{cases} \gcd(a, h) = 1 \\ \gcd(d, v) = 1 \end{cases}$$

### Page 5: Generalized Rectangular Transform (GRT) (`docs/GRT/5.jpg`)

- $\hookrightarrow$ Continuing with what we have defined in (I) and its 4 conditions for our GRT, we introduce the GRT:
  - $\hookrightarrow$ The RT matrix (rectangular transform matrix) $G = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$: its determinant $\|G\|$ can be either positive or negative, and it is **not necessarily equal to 1**.
  - $\hookrightarrow$ Note that the 4 parameters $(a, b, c \text{ and } d)$ must satisfy the 4 conditions we have proved above in order to ensure the existence of periodicity for decryption.
  - $\hookrightarrow$ Additionally, an offset $(r_m, r_n) \in \mathbb{Z}_M^+ \times \mathbb{Z}_N^+$ can be introduced to prevent the fixed-point transformation effect, as the pixel position $[0, 0]$ would otherwise always map to itself without any change.
    - $\hookrightarrow$ **What $(r_m, r_n)$ actually contributes?**
      - $\hookrightarrow$ **A. Fixes the "Frozen Top-Left Corner" problem**
        - In any pure matrix transformation without an offset:
          $$\begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} 0 \\ 0 \end{bmatrix} \pmod{\begin{bmatrix} M \\ N \end{bmatrix}} = \begin{bmatrix} 0 \\ 0 \end{bmatrix}$$
        - Without $(r_m, r_n)$: coordinate $(0, 0)$ is an invariant fixed point; it never moves.
        - With $(r_m, r_n)$: the origin is displaced to $(r_m, r_n)$, ensuring that every tile, including all 4 corners, is displaced.
      - $\hookrightarrow$ **B. Prevents Trivial Linear Solving (known-plaintext attack)**
        - $\hookrightarrow$ If an attacker identifies the destination of just 2 tiles (for e.g., where $(1, 0)$ and $(0, 1)$ landed), they can reconstruct the entire matrix $G = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$ instantly using modulo division.

### Page 6: Linearity vs. Affine Transformation (`docs/GRT/6.jpg`)

        - $\hookrightarrow$ **Without $(r_m, r_n)$, the transformation is strictly linear (pure matrix multiplication):**
          - $\hookrightarrow f(v) = G \cdot v \pmod m$
          - $\hookrightarrow$ And $f(u + v) = A(u + v) = Au + Av = f(u) + f(v)$
          - $\hookrightarrow$ **Example of plaintext attack on this case:**
            - If an attacker discovers where just 2 tiles landed:
              - $\hookrightarrow u = (1, 0)$ moved to position $f(u) = (5, 10)$
              - $\hookrightarrow v = (0, 1)$ moved to position $f(v) = (7, 20)$
            - Because of linearity, where does tile $(x, y)$ go?
              - $\hookrightarrow$ Since $(1, 1) = u + v$
                - $\hookrightarrow f(1, 1) = f(u) + f(v) = (12, 30)$
              - $\hookrightarrow$ Then tile $(x, y) = x \cdot u + y \cdot v$
                - $\hookrightarrow f(x, y) = x \cdot f(u) + y \cdot f(v)$
                - $\implies$ The entire scrambled image layout can be derived by taking combinations of known tile outputs.
                - $\implies$ It collapses a problem that should take billions of years into a 2-variable linear system solvable in microseconds.
        - $\hookrightarrow$ **With $(r_m, r_n)$, turn the transformation into an affine map:**
          - $\hookrightarrow f(v) = Av + r \pmod m$
          - $\hookrightarrow f(u + v) = A(u + v) + r = Au + Av + r$
          - $\hookrightarrow f(u) + f(v) = (Au + r) + (Av + r) = Au + Av + 2r$
          - $\implies f(u + v) \neq f(u) + f(v) \ ; \ f(u + v) = f(u) + f(v) - r$
          - $\hookrightarrow$ Because of the extra $-r$ term, for each image request, the resulting tile layout looks completely different every time.

### Page 7: Extending the Coverage of the Transformation Matrix (`docs/GRT/7.jpg`)

- $\hookrightarrow$ **We extend the coverage of the transformation matrix in the GRT:**
  - $\hookrightarrow$ We extend $G$ by multiplying 2 integers $(e, f)$ to create a new extended matrix $G$, with:
    $$\begin{cases} \gcd(e, M) = 1 \\ \gcd(f, N) = 1 \end{cases}$$
    $$G = \begin{bmatrix} ea & eb \\ fc & fd \end{bmatrix}$$
    *(From now on, when we mention $G$, we will refer to this one.)*
  - $\hookrightarrow$ By examining the 4 conditions, we can prove that it is indeed a valid transformation matrix as detailed below:
    - $\hookrightarrow$ **Condition 1.** $(eb \bmod h = 0)$ or $(fc \bmod v = 0)$
      - $\hookrightarrow$ This statement is correct as $e, f \ge 1$ and since $(b \bmod h = 0)$ or $(c \bmod v = 0)$.
    - $\hookrightarrow$ **Condition 2.** $\gcd(ef\|G\|, p) = 1$
      - $\hookrightarrow$ Recall that since $\gcd(M, N) = p$, $h = \frac{M}{p}$, and $v = \frac{N}{p}$, we know that $(e, h), (e, p), (f, v)$ and $(f, p)$ are coprime:
        - $\hookrightarrow$ **Proof:**
          $$\left.\begin{aligned} \text{Since } \gcd(e, M) &= 1 \\ \text{And } M &= h \cdot p \end{aligned}\right\} \implies \begin{cases} \gcd(e, h) = 1 \\ \gcd(e, p) = 1 \end{cases}$$
          $$\left.\begin{aligned} \text{Since } \gcd(f, N) &= 1 \\ \text{And } N &= v \cdot p \end{aligned}\right\} \implies \begin{cases} \gcd(f, v) = 1 \\ \gcd(f, p) = 1 \end{cases}$$
      - $\hookrightarrow$ **Proof:**
        - $\hookrightarrow \gcd(ef\|G\|, p) = \gcd(\|G\|, p) \cdot \gcd(ef, p)$
        - $\hookrightarrow$ And $\begin{cases} \gcd(e, p) = 1 \\ \gcd(f, p) = 1 \end{cases} \implies \gcd(ef, p) = 1 \implies \text{verified.}$

### Page 8: Conditions 3 & 4 and General Inverse Form (`docs/GRT/8.jpg`)

    - $\hookrightarrow$ **Conditions 3 and 4.**
      - $\hookrightarrow$ Since $(e, h)$ and $(f, v)$ are coprime:
        - $\hookrightarrow \gcd(ea, h) = \gcd(e, h) \cdot \gcd(a, h) = 1$
        - $\implies$ This leads to $\gcd(ea, h) = 1$ and $\gcd(fd, v) = 1$ eventually.
  - $\hookrightarrow$ The expanded matrices make it more difficult for a malicious attacker to deduce the transformation matrix, thereby providing higher security compared to using the original matrix.

#### General Inverse Form: Introducing an Inverse Generalized Rectangular Transformation (IGRT)
- $\hookrightarrow$ **The proposed IGRT scheme consists of 4 significant features:**
  - $\hookrightarrow$ **First**, given a valid RT matrix ($G$), IGRT provides a bijection to reversely map the transformed pixel position $(x', y')$ back to the original pixel position $(x, y)$.
  - $\hookrightarrow$ **Second**, it can decrypt the image without any prior information about the periodicity of the matrix $G$.
  - $\hookrightarrow$ **Third**, it is general enough to decrypt a square image if we impose the condition $M = N$.
  - $\hookrightarrow$ **Lastly**, due to the inverse manner, the decryption is much more effective and efficient than the conventional periodic-decryption process.

### Page 9: IGRT Stages 1 & 2 (`docs/GRT/9.jpg`)

- $\hookrightarrow$ **The IGRT scheme consists of 4 stages including the inverse equilateral mapping, inverse projection mapping, inverse triangular mapping, and inverse translation as detailed below:**
  - $\hookrightarrow$ **Stage 1. Inverse equilateral mapping**
    - $\hookrightarrow$ **Purpose:** Recover the remainder component $(x_p, y_p)$ modulo the common factor $p$.
    - $\hookrightarrow$ **Inputs:**
      - Ciphered coordinate: $\begin{bmatrix} x' \\ y' \end{bmatrix} \in \mathbb{Z}_M \times \mathbb{Z}_N$
      - Translation offset: $\begin{bmatrix} r_m \\ r_n \end{bmatrix} \in \mathbb{Z}_M \times \mathbb{Z}_N$
      - Matrix parameters: $a, b, c, d$
      - Common factor: $p = \gcd(M, N)$
      - Modular determinant inverse: $G_{[p]}^{-1} = (ad - bc)^{-1} \bmod p$
    - $\hookrightarrow$ **Expected output:**
      - Equilateral remainder vector: $\begin{bmatrix} x_p \\ y_p \end{bmatrix} \in \mathbb{Z}_p \times \mathbb{Z}_p$
      - $0 \le x_p < p \ ; \ 0 \le y_p < p$
    - $\hookrightarrow$ **Mathematical operation:**
      $$\begin{bmatrix} x_p \\ y_p \end{bmatrix} = G_{[p]}^{-1} \begin{bmatrix} d & (p - 1)b \\ (p - 1)c & a \end{bmatrix} \begin{bmatrix} x' - r_m \\ y' - r_n \end{bmatrix} \bmod p$$
    - $\hookrightarrow$ **Programmatic implementation:**
      - $\hookrightarrow$ `(insert code here)`
  - $\hookrightarrow$ **Stage 2. Inverse projection mapping**
    - $\hookrightarrow$ **Inputs:**
      - Ciphered coordinate: $\begin{bmatrix} x' \\ y' \end{bmatrix}$
      - Translation offset: $\begin{bmatrix} r_m \\ r_n \end{bmatrix}$
      - Equilateral remainders: $\begin{bmatrix} x_p \\ y_p \end{bmatrix}$ derived from Stage 1

### Page 10: IGRT Stage 2 (cont.) & Stage 3 (`docs/GRT/10.jpg`)

      - Matrix parameters: $a, b, c, d$
      - Quotient factors: $h = \frac{M}{p} \ , \ v = \frac{N}{p}$
    - $\hookrightarrow$ **Expected output:**
      - Projection vector: $\begin{bmatrix} H \\ V \end{bmatrix}$
      - $0 \le H < h \ ; \ 0 \le V < v$
    - $\hookrightarrow$ **Mathematical operation:**
      $$\begin{bmatrix} H \\ V \end{bmatrix} = \left( \begin{bmatrix} x' - r_m \\ y' - r_n \end{bmatrix} - \begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} x_p \\ y_p \end{bmatrix} \right) \bmod \begin{bmatrix} h \\ v \end{bmatrix}$$
      - **Note:** In the paper *(insert paper here)*, the extra term
        $$+ \begin{bmatrix} \left\lceil \frac{a \cdot p}{h} \right\rceil \cdot h + \left\lceil \frac{b \cdot p}{h} \right\rceil \cdot h \\ \left\lceil \frac{c \cdot p}{v} \right\rceil \cdot v + \left\lceil \frac{d \cdot p}{v} \right\rceil \cdot v \end{bmatrix}$$
        simply serves as positive offsets to prevent negative numerators prior to the modulo operation.
      - `(Insert code implementation here)`
  - $\hookrightarrow$ **Stage 3. Inverse Triangular mapping**
    - $\hookrightarrow$ **Inputs:**
      - Projection vector: $\begin{bmatrix} H \\ V \end{bmatrix}$ (derived from Stage 2)
      - Modular inverse: $a_{[h]}^{-1} = a^{-1} \bmod h$ and $d_{[v]}^{-1} = d^{-1} \bmod v$
    - $\hookrightarrow$ **Expected output:**
      - Quotient vector: $\begin{bmatrix} x_h \\ y_v \end{bmatrix}$
      - $0 \le x_h < h$ and $0 \le y_v < v$

### Page 11: IGRT Stage 3 Operations & Stage 4 (`docs/GRT/11.jpg`)

    - $\hookrightarrow$ **Mathematical operation:**
      - $\hookrightarrow$ **Case 1. (Diagonal Matrix)** ($b \bmod h = 0$ and $c \bmod v = 0$)
        $$\begin{bmatrix} x_h \\ y_v \end{bmatrix} = \begin{bmatrix} a_{[h]}^{-1} \cdot H \\ d_{[v]}^{-1} \cdot V \end{bmatrix} \bmod \begin{bmatrix} h \\ v \end{bmatrix}$$
        - `(insert code implementation here)`
      - $\hookrightarrow$ **Case 2. (Lower-Triangular Matrix — compute $x_h$ first)** ($b \bmod h = 0$ and $c \bmod v \neq 0$)
        $$\begin{bmatrix} x_h \\ y_v \end{bmatrix} = \begin{bmatrix} a_{[h]}^{-1} \cdot H \\ d_{[v]}^{-1} (V - c \cdot x_h) \end{bmatrix} \bmod \begin{bmatrix} h \\ v \end{bmatrix}$$
        - `(insert code implementation here)`
      - $\hookrightarrow$ **Case 3. (Upper-Triangular Matrix — we must compute $y_v$ first)** ($b \bmod h \neq 0$ and $c \bmod v = 0$)
        $$\begin{bmatrix} y_v \\ x_h \end{bmatrix} = \begin{bmatrix} d_{[v]}^{-1} \cdot V \\ a_{[h]}^{-1} (H - b \cdot y_v) \end{bmatrix} \bmod \begin{bmatrix} v \\ h \end{bmatrix}$$
        - `(Insert code implementation here)`
  - $\hookrightarrow$ **Stage 4. Coordinate Assembly**
    - $\hookrightarrow$ Reconstruct the original coordinate $(x, y)$.
    - $\hookrightarrow$ **Inputs:**
      - Equilateral remainder: $\begin{bmatrix} x_p \\ y_p \end{bmatrix}$ from Stage 1
      - Quotient components: $\begin{bmatrix} x_h \\ y_v \end{bmatrix}$ from Stage 3
      - Scaling factor: $p = \gcd(M, N)$

### Page 12: IGRT Stage 4 Operation (`docs/GRT/12.jpg`)

    - $\hookrightarrow$ **Mathematical operation:**
      $$\begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} x_p \\ y_p \end{bmatrix} + \begin{bmatrix} p \cdot x_h \\ p \cdot y_v \end{bmatrix}$$
    - $\hookrightarrow$ **Expected output:**
      - Plaintext coordinate: $\begin{bmatrix} x \\ y \end{bmatrix}^T$
      - $0 \le x < M$ and $0 \le y < N$
