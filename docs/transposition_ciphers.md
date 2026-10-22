# Transposition Ciphers: Comprehensive Technical Guide

A **Transposition Cipher** is a method of encryption where the characters of a plaintext message are rearranged (permuted) according to a predefined system, geometric pattern, or secret key. Unlike substitution ciphers, the identity and frequency of each character remain unchanged; only their positions are altered.

---

## 1. Classification & Fundamentals

### Is a Transposition Cipher Symmetric?
**Yes.** Transposition ciphers are strictly **symmetric-key cryptosystems**. Both the sender (encryptor) and receiver (decryptor) must share and agree on the identical secret parameter, which can be:
- A numeric key representing a permutation order (e.g., `(3, 1, 4, 2)`).
- A keyword whose alphabetical letter order determines column permutations (e.g., `"ZEBRA"` -> `[5, 2, 1, 4, 3]`).
- Geometric dimensions or physical properties (e.g., number of rails in a fence, or cylinder diameter of a Scytale).

### Encryption vs. Decryption Mechanism
- **Encryption:** A bijective mapping function `pi` maps each position `i` in the plaintext to a new position `pi(i)` in the ciphertext:
  ```text
  Ciphertext[pi(i)] = Plaintext[i]
  ```
- **Decryption:** The inverse mapping function `pi_inv` (where `pi_inv(pi(i)) = i`) restores each character to its original position:
  ```text
  Plaintext[i] = Ciphertext[pi_inv(i)]
  ```

---

## 2. Mathematical Foundations

### 2.1 Permutation Groups and Symmetric Group S_n
Let `X = {1, 2, 3, ..., n}` be a set of `n` indices representing the positions of letters in a block of plaintext.
A transposition operation is mathematically defined as a element of the **symmetric group** `S_n`:
```text
pi : X -> X
```
Because `pi` is a bijection (one-to-one and onto), every character has a unique source index and destination index.

#### Example (Two-line Cauchy notation):
For a block of size 5:
```text
     ( 1  2  3  4  5 )
pi = ( 3  5  1  2  4 )
```
- Character at index 1 moves to index 3.
- Character at index 2 moves to index 5.
- Character at index 3 moves to index 1.
- Character at index 4 moves to index 2.
- Character at index 5 moves to index 4.

#### Inverse Permutation:
```text
         ( 1  2  3  4  5 )
pi_inv = ( 3  4  1  5  2 )
```

### 2.2 Cycle Notation
Any permutation in `S_n` can be decomposed into disjoint cycles:
```text
pi = (1 3)(2 5 4)
```
- `(1 3)`: positions 1 and 3 swap with each other (a cycle of length 2).
- `(2 5 4)`: 2 -> 5 -> 4 -> 2 (a cycle of length 3).
- The order (period) of `pi` is the least common multiple of its cycle lengths: `lcm(2, 3) = 6`. Applying the encryption key 6 consecutive times returns the message to plaintext.

### 2.3 Permutation Matrices
A permutation of length `n` can be represented as an `n x n` orthogonal binary matrix `P`, where each row and column contains exactly one `1`:
```text
Vector_ciphertext = P * Vector_plaintext
Vector_plaintext = P^T * Vector_ciphertext
```
Because `P` is orthogonal, the inverse permutation matrix is simply the transpose: `P_inv = P^T`.

---

## 3. The Family of Transposition Ciphers

Here are the primary algorithms that belong to the Transposition family.

```
Transposition Ciphers
├── Physical / Mechanical
│   └── Scytale
├── Geometric Path / Route
│   ├── Rail Fence Cipher (Zig-Zag)
│   └── Route Cipher (Grid Spiral / Alternating)
├── Columnar Family
│   ├── Simple (Complete) Columnar Transposition
│   ├── Irregular (Incomplete) Columnar Transposition
│   └── Myszkowski Transposition (Handles duplicate letters in key)
├── Multiple / Product Transposition
│   └── Double Transposition (Military-grade hand cipher)
└── Block-Based
    └── Permutation / Block Transposition
```

---

### 3.1 Scytale Cipher (Physical Transposition)

* **Origin:** Ancient Greece (used by Spartans during wars).
* **Key:** The diameter (circumference) of the rod, which corresponds to the number of rows `r` or columns `c`.

#### How it works:
1. A strip of parchment is wrapped helically around a cylinder of circumference `k`.
2. The message is written lengthwise along the cylinder.
3. When unrolled, the letters appear scrambled across intervals of `k`.

```text
Plaintext: "HELP ME I AM UNDER ATTACK" (ignoring spaces: "HELPMEIAMUNDERATTACK", length 20)
Circumference (Rows) = 4

Grid layout (written row by row):
Row 0: H  E  L  P  M
Row 1: E  I  A  M  U
Row 2: N  D  E  R  A
Row 3: T  T  A  C  K

Read column by column:
Col 0: H E N T
Col 1: E I D T
Col 2: L A E A
Col 3: P M R C
Col 4: M U A K

Ciphertext: "HENTE IDTLA EAPMR CMUAK"
```

---

### 3.2 Rail Fence Cipher (Zig-Zag)

* **Concept:** Text is written in a descending and ascending diagonal ("zig-zag") across `d` imaginary rails, then read off row by row.
* **Key:** Integer `d` (number of rails/depth).

#### Algorithm (Encryption):
1. Create `d` empty strings (one for each rail).
2. Traverse through the characters of the plaintext, placing each into the current rail.
3. Move down until the bottom rail is reached, then reverse direction upward until the top rail is reached.
4. Concatenate the contents of all rails from top to bottom.

#### Concrete Example:
```text
Plaintext: "DEFEND THE EAST WALL" (no spaces: "DEFENDTHEEASTWALL", length 17)
Rails = 3

Pattern:
Rail 0: D . . . N . . . E . . . T . . . L
Rail 1: . E . E . D . H . E . S . W . L .
Rail 2: . . F . . . T . . . A . . . A . .

Row 0: D N E T L
Row 1: E E D H E S W L
Row 2: F T A A

Ciphertext: "DNETL EEDHE SWLFT AA"
```

#### Decryption:
1. Reconstruct the zig-zag coordinate matrix of size `d x n`.
2. Place placeholder markers `*` at each position where a character belongs.
3. Fill the markers with the ciphertext characters row-by-row.
4. Read the text following the zig-zag path.

---

### 3.3 Route Cipher

* **Concept:** The message is written into a grid of predetermined dimensions `rows x cols` row by row (or column by column), but read out following an agreed non-linear "route".
* **Key:** Grid dimensions `(r, c)` and a designated route descriptor (e.g., "Counter-clockwise inward spiral starting from top-right").

#### Concrete Example:
```text
Plaintext: "RETREAT TO NORTH RIDGE NOW" (length 23, pad with 'X' -> 24)
Grid: 4 rows x 6 columns

Grid:
R  E  T  R  E  A
T  T  O  N  O  R
T  H  R  I  D  G
E  N  O  W  X  X

Route: Clockwise inward spiral starting from Top-Left:
1. Top row:       R, E, T, R, E, A
2. Right col:     R, G, X
3. Bottom row:    X, W, O, N, E
4. Left col:      T, T
5. Next inner:    T, O, N, O, D, I, R, H

Ciphertext: "RETRE ARGX XWONE TTT ON ODI RH"
```

---

### 3.4 Simple (Complete) Columnar Transposition

* **Concept:** Plaintext is written into a grid row by row. Columns are labeled with the letters of a secret keyword. The columns are then read out in the alphabetical order of the keyword letters.
* **Key:** A secret word (e.g., `"GERMAN"`). Length of key = number of columns.
* **Condition:** "Complete" means the text length is an exact multiple of the key length (or padded to fit).

#### Concrete Example:
```text
Plaintext: "MEET ME AFTER THE BALL" (length 18, pad with 'X' to 18)
Keyword: "ZEBRAS"

Keyword Alphabetical Order:
Z  E  B  R  A  S
6  2  1  5  0  4   (indices 0 to 5)

Column order to read: A(0), B(1), E(2), R(3), S(4), Z(5)
Alphabetic rank:
Key:      Z  E  B  R  A  S
Rank:     6  3  2  5  1  4

Grid (3 rows x 6 cols):
Z  E  B  R  A  S
---------------
M  E  E  T  M  E
A  F  T  E  R  T
H  E  B  A  L  L

Reading columns by Rank (1 to 6):
Col 1 (A): M R L
Col 2 (B): E T B
Col 3 (E): E F E
Col 4 (S): E T L
Col 5 (R): T E A
Col 6 (Z): M A H

Ciphertext: "MRL ETB EFE ETL TEA MAH"
```

---

### 3.5 Irregular (Incomplete) Columnar Transposition

* **Concept:** The message length `n` is **not** an exact multiple of the key length `k`, and **no padding** is added.
* **Significance:** Leaving empty spaces in the final row makes cryptanalysis significantly harder because columns have unequal lengths:
  - First `n mod k` columns have length `ceil(n / k)`.
  - Remaining columns have length `floor(n / k)`.

#### Concrete Example:
```text
Plaintext: "ATTACK POSTPONED UNTIL TWO AM" (length 25, no spaces)
Key: "TIMER" (Length 5)
Key Rank:
T  I  M  E  R
5  2  3  1  4

Grid:
T  I  M  E  R
-------------
A  T  T  A  C
K  P  O  S  T
P  O  N  E  D
U  N  T  I  L
T

Column lengths:
Length of key = 5. Total chars = 25.
25 / 5 = exactly 5 characters per column.

If message length was 23:
- Cols 0, 1, 2 have 5 characters.
- Cols 3, 4 have 4 characters.
The decryptor must account for these variable column lengths when splitting the ciphertext back into columns.
```

---

### 3.6 Myszkowski Transposition

* **Problem Solved:** How to handle duplicate letters in the keyword without arbitrary tie-breaking.
* **Invented by:** Émile Victor Théodore Myszkowski (1902).
* **Rule:**
  - Distinct letters are read column-by-column as usual.
  - Duplicate letters are assigned the **same numerical rank**. When their turn comes, their characters are read **row-by-row** (horizontally across the matching columns) instead of column-by-column!

#### Concrete Example:
```text
Key: "BANANA"
Letters:  B  A  N  A  N  A
Ranks:    2  1  3  1  3  1

Ranks assigned:
- All 'A's get Rank 1 (columns 1, 3, 5)
- 'B' gets Rank 2 (column 0)
- All 'N's get Rank 3 (columns 2, 4)

Plaintext: "WE ARE DISCOVERED FLEE AT ONCE" (no spaces, 26 chars)

Grid:
B  A  N  A  N  A
2  1  3  1  3  1
----------------
W  E  A  R  E  D
I  S  C  O  V  E
R  E  D  F  L  E
E  A  T  O  N  C
E

Read Rank 1 (Columns 1, 3, 5 row-by-row):
Row 0: E, R, D
Row 1: S, O, E
Row 2: E, F, E
Row 3: A, O, C
-> "E R D S O E E F E A O C"

Read Rank 2 (Column 0 column-by-column):
-> "W I R E E"

Read Rank 3 (Columns 2, 4 row-by-row):
Row 0: A, E
Row 1: C, V
Row 2: D, L
Row 3: T, N
-> "A E C V D L T N"

Ciphertext: "ERDSOEEFEAOC WIRE E AECVDLTN"
```

---

### 3.7 Double Transposition Cipher

* **Overview:** A product cipher that applies two successive columnar transpositions, typically with two different keys (or the same key twice).
* **Historical Significance:** Regarded as one of the most secure hand ciphers ever designed. Used extensively during World War I, World War II (by the French Resistance, SOE, and German Abwehr), and the Cold War by intelligence operatives.
* **Why it is secure against hand cryptanalysis:**
  - A single transposition preserves bigrams within columns.
  - A double transposition breaks apart the adjacency of letters in both dimensions, dispersing letters across the entire text block.

```text
Plaintext ──> [ Columnar Transposition Key 1 ] ──> Intermediate ──> [ Columnar Transposition Key 2 ] ──> Ciphertext
```

---

### 3.8 Block / Permutation Cipher

* **Concept:** The message is split into fixed-length blocks of size `m`. A fixed permutation vector `pi` is applied independently to each block.
* **Formulation:**
  ```text
  Key = (pi(0), pi(1), ..., pi(m-1))
  ```

#### Example:
```text
Block size m = 4
Key = (2, 0, 3, 1)  (meaning: out[0]=in[2], out[1]=in[0], out[2]=in[3], out[3]=in[1])

Plaintext: "HELP US TODAY!" -> ["HELP", "USTO", "DAYX"]

Block 1 "HELP":
- in[2] = 'L' -> out[0]
- in[0] = 'H' -> out[1]
- in[3] = 'P' -> out[2]
- in[1] = 'E' -> out[3]
Result: "LHPE"

Block 2 "USTO" -> "TUSO"
Block 3 "DAYX" -> "YD mould -> YDXA"
```

---

## 4. Key Formats & Step-by-Step Decryption Walkthrough

### 4.1 What Does the Key Look Like?
In a transposition cipher, the key never acts as an arithmetic masking value (like an XOR key in stream ciphers or one-time pads). Instead, it serves as a **geometric guide or ordering vector** that specifies how character positions are rearranged.

```
Key Representations
├── Keyword String (e.g., "WORK", "ZEBRAS")
│   └── Converted into an alphabetical ranking vector [3, 1, 2, 0]
├── Permutation Vector / Tuple (e.g., (2, 0, 3, 1))
│   └── Directly defines output index positions per block
└── Geometric Integer / Dimension (e.g., rails = 3, diameter = 4)
    └── Defines the height or period of traversal paths
```

#### Key Type 1: Keyword String
* **Format:** A natural language word or phrase (e.g., `"WORK"`).
* **Conversion to Rank Vector:** The letters are sorted alphabetically, and each character is assigned its 0-indexed (or 1-indexed) rank:
  ```text
  Key:            W    O    R    K
  Col Index:      0    1    2    3
  Sorted:         K    O    R    W
  Order of Read:  3    1    2    0
  ```
  *(Column 3 is read 1st, Column 1 is read 2nd, Column 2 is read 3rd, Column 0 is read 4th).*

#### Key Type 2: Permutation Vector / Tuple
* **Format:** An explicit sequence of index numbers, e.g., `pi = (2, 0, 3, 1)`.
* **Application:** Used in block transposition where each 4-character chunk `B[0..3]` has its positions shuffled: `B[0] -> position 2`, `B[1] -> position 0`, etc.

#### Key Type 3: Geometric Integer
* **Format:** A single positive integer `d` (e.g., `rails = 3`).
* **Application:** In Rail Fence or Scytale, this integer determines the number of rows or boundary heights through which the trajectory oscillates.

---

### 4.2 How to Decrypt into Original Text: Concrete Walkthroughs

### Walkthrough A: Decrypting Columnar Transposition

* **Input Ciphertext:** `"ATNTKATAWACD"` (12 characters)
* **Secret Key:** `"WORK"` (Length = 4)

#### Step 1: Calculate Grid Dimensions
```text
Total message length (n) = 12
Number of columns (c)    = len("WORK") = 4
Number of rows (r)       = n / c = 12 / 4 = 3
```
Because the message is complete (12 is divisible by 4), **each column holds exactly 3 characters**.

#### Step 2: Establish the Alphabetical Column Order
Sort the key letters alphabetically to determine the order in which columns were extracted during encryption:
```text
Key Letter:    W      O      R      K
Original Col:  0      1      2      3
Sort Order:   4th    2nd    3rd    1st
```
The columns were extracted in the sequence: **Col 3 ('K'), then Col 1 ('O'), then Col 2 ('R'), then Col 0 ('W')**.

#### Step 3: Slice Ciphertext into Column Segments
Since each column has length 3, slice the ciphertext sequentially:
```text
Ciphertext: " A T N   T K A   T A W   A C D "
Slices:
  Slice 1 (Col 3, 'K'): "ATN"
  Slice 2 (Col 1, 'O'): "TKA"
  Slice 3 (Col 2, 'R'): "TAW"
  Slice 4 (Col 0, 'W'): "ACD"
```

#### Step 4: Reconstruct the Original Grid
Place each slice vertically into its **original column index**:
```text
Col 0 (W)    Col 1 (O)    Col 2 (R)    Col 3 (K)
 [ACD]        [TKA]        [TAW]        [ATN]
-----------------------------------------------
   A            T            T            A      <-- Row 0
   C            K            A            T      <-- Row 1
   D            A            W            N      <-- Row 2
```

#### Step 5: Read Off Row-by-Row
Read horizontally across the rows from left to right:
```text
Row 0: A T T A
Row 1: C K A T
Row 2: D A W N

Result: "ATTACKATDAWN" -> "ATTACK AT DAWN"
```

---

### Walkthrough B: Decrypting the Rail Fence Cipher

* **Input Ciphertext:** `"DNETLEEDHESWLFTAA"` (17 characters)
* **Secret Key:** `d = 3` rails

#### Step 1: Map the Zig-Zag Coordinates
Construct an empty matrix of size `3 x 17` and trace the zig-zag bounce path, placing a marker `*` at each position where a letter belongs:
```text
Rail 0: * . . . * . . . * . . . * . . . *   (5 markers)
Rail 1: . * . * . * . * . * . * . * . * .   (8 markers)
Rail 2: . . * . . . * . . . * . . . * . .   (4 markers)
```

#### Step 2: Fill Markers with Ciphertext Characters
Fill the marked positions row-by-row with the incoming ciphertext:
```text
Ciphertext: "DNETL" (5 chars) -> Rail 0
Rail 0: D . . . N . . . E . . . T . . . L

Ciphertext: "EEDHESWL" (8 chars) -> Rail 1
Rail 1: . E . E . D . H . E . S . W . L .

Ciphertext: "FTAA" (4 chars) -> Rail 2
Rail 2: . . F . . . T . . . A . . . A . .
```

#### Step 3: Trace the Zig-Zag to Read Plaintext
Follow the bouncing diagonal coordinates:
```text
(0,0)->'D', (1,1)->'E', (2,2)->'F', (1,3)->'E', (0,4)->'N', (1,5)->'D', (2,6)->'T', (1,7)->'H', ...
Result: "DEFENDTHEEASTWALL" -> "DEFEND THE EAST WALL"
```

---

### Walkthrough C: Decrypting Block / Permutation Ciphers

* **Key (Encryption Vector):** `pi = (2, 0, 3, 1)` for block size `m = 4`.
* **Input Block (Ciphertext):** `"LHPE"`

#### Step 1: Calculate the Inverse Permutation Vector (`pi_inv`)
```text
Original position (i):    0    1    2    3
Encrypted target (pi(i)): 2    0    3    1

Invert the mapping:
Where does index 0 come from? -> Index 1
Where does index 1 come from? -> Index 3
Where does index 2 come from? -> Index 0
Where does index 3 come from? -> Index 2

=> pi_inv = (1, 3, 0, 2)
```

#### Step 2: Apply `pi_inv` to the Ciphertext Block
```text
Ciphertext block: "LHPE"
C[0]='L', C[1]='H', C[2]='P', C[3]='E'

P[0] = C[pi_inv[0]] = C[1] = 'H'
P[1] = C[pi_inv[1]] = C[3] = 'E'
P[2] = C[pi_inv[2]] = C[0] = 'L'
P[3] = C[pi_inv[3]] = C[2] = 'P'

Result: "HELP" (Original plaintext block restored)
```

---

### 4.3 Reference Implementation in Python

Below is a complete, modular implementation of Columnar Transposition (both Encryption and Decryption):

```python
def encrypt_columnar(plaintext: str, key: str) -> str:
  # Remove spaces or preprocess if needed
  text = plaintext.replace(" ", "")
  num_cols = len(key)
  
  # Pad text with 'X' to fill the rectangular grid completely
  remainder = len(text) % num_cols
  if remainder != 0:
    text += "X" * (num_cols - remainder)
    
  num_rows = len(text) // num_cols
  
  # Fill the grid row-by-row
  grid = [text[i * num_cols : (i + 1) * num_cols] for i in range(num_rows)]
  
  # Sort columns alphabetically by key character
  sorted_col_indices = sorted(range(num_cols), key=lambda i: key[i])
  
  # Read columns in alphabetical order
  ciphertext = []
  for col_idx in sorted_col_indices:
    for row in grid:
      ciphertext.append(row[col_idx])
      
  return "".join(ciphertext)


def decrypt_columnar(ciphertext: str, key: str) -> str:
  num_cols = len(key)
  num_rows = len(ciphertext) // num_cols
  
  # Sort key letters to determine column extraction order
  sorted_col_indices = sorted(range(num_cols), key=lambda i: key[i])
  
  # Distribute ciphertext chunks back to their respective columns
  cols = {}
  current_idx = 0
  for col_idx in sorted_col_indices:
    cols[col_idx] = ciphertext[current_idx : current_idx + num_rows]
    current_idx += num_rows
    
  # Read out reconstructed grid row-by-row
  plaintext = []
  for r in range(num_rows):
    for c in range(num_cols):
      plaintext.append(cols[c][r])
      
  return "".join(plaintext)


if __name__ == "__main__":
  message = "ATTACKATDAWN"
  secret_key = "WORK"
  
  enc = encrypt_columnar(message, secret_key)
  dec = decrypt_columnar(enc, secret_key)
  
  print(f"Original:   {message}")
  print(f"Encrypted:  {enc}")
  print(f"Decrypted:  {dec}")
```

---

## 5. Summary Table of the Transposition Family

| Cipher Name | Key Type | Grid Structure | Order of Readout | Distinctive Feature |
| :--- | :--- | :--- | :--- | :--- |
| **Scytale** | Cylinder diameter `k` | Fixed circumference | Down columns | Oldest physical device |
| **Rail Fence** | Number of rails `d` | Zig-zag diagonal | Row by row | Alternating bounce direction |
| **Route** | Matrix dims + path | Rectangular grid | Spiral / diagonal / etc. | Arbitrary reading route |
| **Complete Columnar** | Keyword / Key order | Fixed rectangle | Columns sorted alphabetically | Requires padding |
| **Irregular Columnar** | Keyword / Key order | Incomplete rectangle | Columns sorted alphabetically | Irregular column lengths |
| **Myszkowski** | Keyword with repeats | Rectangular grid | Combined row/col readout | Handles repeated letters |
| **Double Transposition** | Two keywords | Two sequential grids | Two columnar passes | Resists simple anagramming |
| **Block Permutation** | Permutation vector `pi` | Blocks of size `m` | Per-block index shuffle | Direct precursor to P-boxes |

---

## 6. Cryptanalysis & Vulnerabilities

While transposition ciphers disguise the structure of messages, they exhibit clear statistical signatures:

### 6.1 Frequency Analysis Preservation
Because no characters are substituted:
- **Unigram letter frequencies are 100% preserved.**
- If you compute the frequency of letters in the ciphertext, the letters `E`, `T`, `A`, `O`, `I`, `N` will appear at the exact same frequencies as in normal language plaintext.
- This immediately tells a cryptanalyst that the cipher is a **pure transposition**, not a substitution.

### 6.2 Anagramming
- **Single Transposition:** Cryptanalysts write the ciphertext into columns of various guessed widths. Because vowels and consonants must combine into valid digraphs (e.g., `TH`, `HE`, `IN`, `ER`), columns can be slid against each other to maximize high-probability bigram and trigram frequency scores until valid words emerge.
- **Multiple Anagramming (Double Transposition):** If two messages of identical length are encrypted with the same double transposition key, they can be aligned and solved simultaneously by cross-referencing valid linguistic combinations in both messages.

---

## 7. Modern Legacy: Transposition in Modern Ciphers

In modern block ciphers, classical transposition evolved into **Permutation Boxes (P-boxes)** and **Diffusion Layers**:
1. **Claude Shannon's Principles (1949):** A secure cipher requires two foundational properties:
   - **Confusion:** Masking the relationship between key and ciphertext (implemented via **Substitution** / S-boxes).
   - **Diffusion:** Spreading the influence of each plaintext bit across many ciphertext bits (implemented via **Transposition / Permutation**).
2. **DES (Data Encryption Standard):**
   - Uses bit-level transpositions: Initial Permutation (`IP`), Inverse Initial Permutation (`IP^-1`), Expansion Permutation (`E`), and the Round Permutation (`P-box`).
3. **AES (Advanced Encryption Standard):**
   - Uses byte-level transposition: The **`ShiftRows`** layer cyclically rotates the bytes of each row in the 4x4 state matrix.

