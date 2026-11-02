# Watermark solutions

Tests of various water-marking solutions.

## Experiment: error-correcting codes for blind image watermarking at equal distortion

**Question.** A 512-bit message is protected by an error-correcting code
(ECC), embedded in an image, attacked, and extracted **blindly**: the
extractor knows neither the original image nor the message. Which ECC
reconstructs the exact message most often, and can the decoder tell whether a
watermark is present at all? Codes produce codewords of different lengths `n`.
Each code gets one embedding strength, calibrated on 100 images to **wPSNR = 40 dB**.

```
512-bit message ─► ECC encode (n bits) ─► embed (strength s_code) ─► attack ─► blind extract ─► ECC decode ─► m̂, valid
```

Everything that implements an algorithm comes from an established library.
Project code only connects the pieces:

| Component | Library |
|---|---|
| Watermark | [invisible-watermark](https://github.com/ShieldMnt/invisible-watermark) `dwtDctSvd` |
| Repetition, Hamming(7,4) | [komm](https://github.com/rwnobrega/komm) |
| BCH, Reed–Solomon | [galois](https://github.com/mhostetter/galois) |
| Convolutional (Viterbi), 5G-NR LDPC, 5G polar (CRC-aided SCL), LTE turbo | [Sionna](https://github.com/NVlabs/sionna) 2.x (PyTorch) |
| Soft-information model | scikit-learn `GaussianMixture` |
| Attacks | OpenCV, Pillow, scikit-image |
| PSNR / SSIM | scikit-image |

wPSNR has no library implementation, so it is computed from its definition in
`wmecc/metrics.py`.

### Watermark and blind extraction (`wmecc/watermark/imwm.py`)

* **Embedding.** The library's `dwtDctSvd` method quantizes the largest
  singular value of the DCT of every 4x4 block of the Haar-LL band of the
  chroma (U) channel. The library is used unmodified.
* **Layout.** The library would put bit `j mod n` in block `j`, which places
  all the votes of a bit in one column when `n` is a multiple of 256 and makes
  robustness depend on `n`. The library is given one bit per block instead,
  through a keyed permutation, so the votes of a bit are spread over the whole
  image. There are two layouts, set by `votes_per_bit`:
  * **Fixed votes** (`votes_per_bit: 8`, the main experiment): every coded bit
    gets 8 blocks and the other blocks keep their original pixels. A longer code
    marks more of the image, so its strength must fall to stay at 40 dB. Eight is
    the most that fits the longest codes (2048 × 8 = 16384 blocks).
  * **Shared blocks** (`votes_per_bit: null`, the first run): the bits share all
    16384 blocks. Every code marks the same area and gets the same strength, and
    a longer code pays through fewer votes per bit (16384/n).
* **Strength.** For each code, a search on each of the 100 images finds the
  strength whose wPSNR is closest to 40 dB. The mean of those 100 values is the
  code's one strength for every image. The decoder knows it (a system
  parameter, like `n`).
* **Blind extraction.** Attacked images are resized to the embedding frame
  (1024x1024). The library's `decode_frame` gives the 0/1 vote of every block.
  A 2-component Gaussian mixture with shared variance (scikit-learn), fitted to
  the per-bit vote fractions of that same image, gives a linear LLR per coded
  bit. Hard-decision decoders see only the sign, reduced to a binary symmetric
  channel.
* **wPSNR.** `10·log10(255²/mean((NVF·ΔRGB)²))`, with `NVF = 1/(1+θσ²_local)`,
  `θ = D/σ²_max`, `D = 75` and a 3×3 window on the original's luminance
  (Voloshynovskiy et al. 1999). The error is averaged over R, G and B because
  the library embeds in chroma.

### Design

* **Images.** DIV2K validation, center-cropped to 1024×1024. All 100 images
  calibrate the strength. Ten of them are the test images (0801, 0811, …,
  0891), since the set has no others. Ten different images (0806, 0816, …,
  0896) run the attack pilot.
* **Attacks.** One per category from the brief. In the first run the pilot
  measured the uncoded baseline under every setting (`pilot.csv`), and each
  category took the setting whose raw BER was closest to a target: 15% for the
  hard set (`configs/imwm.yaml`), 2% for the moderate set
  (`configs/imwm_moderate.yaml`). Lossless PNG is excluded. A no-attack control
  is added. The fixed-votes configs pin those same attacks, so the runs compare
  directly.
* **Trials.** Each code × attack runs on the 10 test images, each with a random
  512-bit message: 60 attacked extractions per code and set. The same chain on
  the *unwatermarked* covers gives false positives.
* **Metrics.** Exact recovery count, message BER, raw coded-bit BER, and the
  `valid` flag of BCH, RS, LDPC and polar on watermarked and unwatermarked
  images.

### Running

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install --no-deps sionna invisible-watermark   # skip sionna-rt / onnx extras
# DIV2K validation HR -> data/raw/div2k/DIV2K_valid_HR/ (see wmecc/data.py)
.venv/bin/python -c "from wmecc.data import prepare_covers; prepare_covers()"
.venv/bin/python -m wmecc.experiment all --config configs/imwm_fixed.yaml
# moderate set: copy strengths.csv to results/imwm_fixed_moderate, so that calibrate resumes, then
.venv/bin/python -m wmecc.experiment all --config configs/imwm_fixed_moderate.yaml
.venv/bin/python -m pytest -q
```

Stages: `calibrate`, `select`, `run`, `analyze`. Outputs go to `results/imwm_fixed/`
and `results/imwm_fixed_moderate/`, with tables and figures in their `analysis/`
folders. The first run is `configs/imwm.yaml` and `configs/imwm_moderate.yaml`
(`results/imwm_svd*`); running those configs again also adds the codes registered
since, because they use `codes: null`.

### Results

Full write-up: [results document](https://claude.ai/artifact/C1VdEpuetkR9WEGbDwEycz).

* **Strength.** With 8 blocks per coded bit, strength falls with length: 125 at
  n = 512, about 85 at n = 1024, 56 at n = 2048. At one fixed strength per code,
  wPSNR on the test images ranges from 37.89 to 42.77 dB. The n = 2048 codes use
  the same layout as the first run and reproduce its strengths exactly.
* **Exact recovery out of 60**, moderate / hard set. With no attack, 36 of the 37
  configurations recover 10/10; no ECC recovers 8/10.

  | Code | r3/4 | r2/3 | r1/2 | r1/3 | r1/4 |
  |---|---:|---:|---:|---:|---:|
  | LDPC | 55 / 36 | 54 / 31 | 58 / 34 | 58 / 31 | 55 / 23 |
  | Polar | 55 / 32 | 54 / 30 | 58 / 34 | – | 55 / 24 |
  | Turbo | – | – | 57 / 35 | 58 / 34 | – |
  | Convolutional | – | – | 56 / 30 | 54 / 26 | – |
  | BCH | – | 41 / 21 | 44 / 22 | 38 / 17 | – |
  | Reed–Solomon, erasures | – | 43 / 23 | 40 / 19 | 34 / 14 | – |
  | Reed–Solomon | – | 41 / 21 | 38 / 16 | 28 / 11 | – |
  | Reed–Solomon, interleaved (depth 4) | – | 31 / 11 | 32 / 9 | 23 / 8 | – |
  | Repetition | – | – | 28 / 8 | 27 / 11 | 28 / 14 |

  No ECC scores 23 / 6 and Hamming(7,4), r4/7, 41 / 20.

* **Trade-off.** A longer code has more redundancy but less strength, so it starts
  with more raw errors. LDPC under WebP 60 goes from 8/10 at r3/4 to 10/10 at
  r1/4. Under salt & pepper 5% it goes from 8/10 to 0/10.
* **Reed–Solomon.** The decoder matches exact theory. It scores low because one
  wrong bit costs a whole byte and the errors are scattered bits. Interleaving
  makes it worse, since errors are already scattered and a frame fails if any
  word fails. Errors-and-erasures decoding adds 2 to 6 recoveries on moderate
  attacks.
* **Limits.** Rotation of 5° or more, cropping and translation stay near 50%
  raw BER because the library has no synchronization. Rotation 1° defeats every
  code, so the hard set's ceiling is 50. Global color changes are this method's
  weak point. With 10 images, the order inside the top group is not resolved.
* **First run.** With shared blocks every code had a strength of about 56 and the
  best scores were 57 / 25. Below n = 2048, soft-decoded LDPC, polar, turbo and
  convolutional codes, BCH and Reed–Solomon all held or gained with fixed votes.
  The n = 2048 codes are unchanged, since their layout is the same.
* **Earlier run.** `results/imwm` used `dwtDct`, which quantizes one raw LL
  sample per block with no DCT and fails from JPEG 90 down. It also read
  resized images at their new size and let code length affect robustness. Its
  numbers should not be used.
