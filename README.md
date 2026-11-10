> The course report source is [`report.tex`](report.tex) and [`report.pdf`](report.pdf). To compile it, the images it references must be present in the [`figures/`](figures/) folder. Upload the corresponding files from `figures/` before building.

# Project Structure and File Index

Course project for Introduction to Cryptography. The system protects web images against automated scraping by permuting image tiles with the Generalized Rectangular Transform (GRT) on the server and restoring them in the browser with its 4-stage inverse (IGRT).

- Encryption: `src/cryptography/grt_server.py` (Python)
- Decryption: `src/cryptography/igrt_client.js` (JavaScript, HTML5 Canvas)

Requirements: Python 3.10, [`uv`](https://docs.astral.sh/uv/), and Node.js (only for the benchmark notebooks, which run the client decoder).

# Benchmark

## Setup
```bash
uv sync
```


The notebooks in `benchmark/` reproduce the experimental tables of the report. Run them from the `benchmark/` folder; the first code cell holds the configuration (images, grids, run counts, seed).

| Notebook | Output |
| --- | --- |
| `01_latency.ipynb` | Server encryption and client decryption latency |
| `02_memory.ipynb` | Peak server memory footprint |
| `03_compression.ipynb` | PNG, WebP and JPEG size overhead, including a pixel-level shuffle baseline |
| `04_t5_visual_verification.ipynb` | Regenerates the scrambled and restored `t5` images and verifies lossless recovery |

Results are summarized in `benchmark/benchmark.md` and saved as JSON in `benchmark/results/`.

## Repository Layout

```
.
├── report.tex                      Course report (LaTeX)
├── figures/                        Figures used by report.tex
├── pyproject.toml, uv.lock         Python dependencies
├── src/cryptography/
│   ├── grt_server.py               Key generation, validation, padding, tile encryption
│   ├── igrt_client.js              4-stage IGRT decryption, 1D lookup tables, Canvas rendering
│   └── main.ipynb                  Interactive demo
├── benchmark/                      Benchmark notebooks, summary, and results
└── docs/
    ├── benchmark_report.md         Earlier benchmark write-up
    ├── references.md               Bibliography
    ├── srt_and_grt_handwritten_notes.md   SRT and GRT derivation notes
    ├── diagrams/                   Draw.io sources and PDF exports (architecture, IGRT stages)
    ├── images/                     Test images and generated scrambled or restored outputs
    └── papers/                     Reference papers (PDF)
```

## Test Images

| File | Resolution |
| --- | --- |
| `docs/images/t1_SD_480p.png` | 480 x 854 |
| `docs/images/t5_HD_720p.png` | 720 x 1280 |
| `docs/images/t2_FHD_1080p.png` | 1920 x 1080 |
| `docs/images/t3.png` | 736 x 1129 (origin-displacement figure) |
