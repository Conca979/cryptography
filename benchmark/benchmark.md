# Benchmark

## Setup

| Item | Value |
| --- | --- |
| Server | Python 3.10, Pillow, NumPy, `src/cryptography/grt_server.py` (`scramble_image_grt`) |
| Client | Node.js v22 (V8), `src/cryptography/igrt_client.js` (`descrambleBuffer32IGRT`) |
| Runs | 5 warmup, 30 measured iterations (`WARMUP`, `ITERS`) |
| Keys | Fixed seed (`SEED = 2026`), validated with `validate_grt_parameters` |

| Scenario | Image | Resolution | Grid (M x N) | Padded size | Tile size | Tiles |
| --- | --- | --- | --- | --- | --- | --- |
| SD 480p | `docs/images/t1_SD_480p.png` | 480 x 854 | 30 x 25 | 480 x 875 | 16 x 35 | 750 |
| HD 720p | `docs/images/t5_HD_720p.png` | 720 x 1280 | 36 x 40 | 720 x 1280 | 20 x 32 | 1440 |
| FHD 1080p | `docs/images/t2_FHD_1080p.png` | 1920 x 1080 | 40 x 40 | 1920 x 1080 | 48 x 27 | 1600 |

The SD image height (854) is not divisible by 25, so it is padded by edge replication to 875 before tiling. The padded image is used as the baseline in all tables, so reported overheads come from scrambling only.

## Notebooks

Each notebook has a configuration cell (`SCENARIOS`, `WARMUP`, `ITERS`, `SEED`) at the top; edit it to change images, grids, or run counts. Raw results are written to `benchmark/results/*.json`.

| Notebook | Produces |
| --- | --- |
| `01_latency.ipynb` | Table 1: server encryption, client decryption, roundtrip latency |
| `02_memory.ipynb` | Table 2: raw buffer size and peak server heap |
| `03_compression.ipynb` | Table 3: PNG, WebP (lossless), JPEG (quality 90) size overhead |
| `04_t5_visual_verification.ipynb` | Regenerates `t5_scrambled.png` and `t5_restored.png` (to `docs/images/` and `figures/`) and verifies MSE = 0 |

## Results

### Table 1: Execution latency (mean +- std, ms)

| Scenario | Grid | Tiles | Server Enc. | Client Dec. | Roundtrip |
| --- | --- | --- | --- | --- | --- |
| SD 480p | 30 x 25 | 750 | 3.18 +- 0.14 | 0.57 +- 0.14 | 3.74 |
| HD 720p | 36 x 40 | 1440 | 7.32 +- 0.81 | 1.11 +- 0.06 | 8.43 |
| FHD 1080p | 40 x 40 | 1600 | 15.13 +- 1.16 | 2.72 +- 0.28 | 17.84 |

### Table 2: Memory footprint

| Scenario | Padded size | Raw (KB) | Peak heap (KB) | Ratio |
| --- | --- | --- | --- | --- |
| SD 480p | 480 x 875 | 1230.5 | 2463.6 | 2.00x |
| HD 720p | 720 x 1280 | 2700.0 | 5405.4 | 2.00x |
| FHD 1080p | 1920 x 1080 | 6075.0 | 12162.0 | 2.00x |

### Table 3: Compression overhead (original to GRT, KB)

| Scenario (Grid) | Tile | PNG | WebP (lossless) | JPEG (q=90) |
| --- | --- | --- | --- | --- |
| SD 480p (30 x 25) | 16 x 35 | 904.7 to 918.4 (+1.52%) | 604.0 to 638.2 (+5.65%) | 192.9 to 202.5 (+5.01%) |
| HD 720p (36 x 40) | 20 x 32 | 2047.4 to 2066.9 (+0.95%) | 1353.7 to 1419.2 (+4.83%) | 439.5 to 470.0 (+6.95%) |
| FHD 1080p (40 x 40, Tile GRT) | 48 x 27 | 3497.2 to 3515.6 (+0.52%) | 2291.8 to 2450.4 (+6.92%) | 641.2 to 736.4 (+14.85%) |
| FHD 1080p (1920 x 1080, Pixel Shuffle) | 1 x 1 | 3497.2 to 6070.1 (+73.57%) | 2291.8 to 5116.0 (+123.23%) | 641.2 to 1719.3 (+168.12%) |

## Notes

- Latency varies by machine and load; rerun `01_latency.ipynb` to refresh. Memory and compression values are deterministic for a fixed seed.
- Client latency is measured in Node.js V8 on the raw 32-bit buffer, excluding image decoding and Canvas painting.
- Section 4 of `report.tex` is synchronized with these tables and the 36 x 40 `t5` grid caption.
