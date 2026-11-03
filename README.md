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
* **Message.** One pseudo-random 512-bit message, fixed by the seed, is used for
  every code, image and stage, including calibration. It is recorded in each
  run's `config.json`. Only embedding and scoring use it: the extractor and the
  decoders never see it.
* **Trials.** Each code × attack runs on the 10 test images: 60 attacked
  extractions per code and set. The same chain on the *unwatermarked* covers
  gives false positives.
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

Extended test of the ten best configurations (about 8.5 hours on 6 cores; a killed run
resumes from the last finished image):

```bash
mkdir -p results/top10 && cp results/imwm_fixed/calibration.json results/top10/
.venv/bin/python -m wmecc.experiment run --config configs/top10.yaml
.venv/bin/python -m wmecc.experiment sweep --config configs/top10.yaml
.venv/bin/python -m wmecc.extended --config configs/top10.yaml
```

Stages: `calibrate`, `select`, `run`, `sweep`, `analyze`. Outputs go to `results/imwm_fixed/`
and `results/imwm_fixed_moderate/`, with tables and figures in their `analysis/`
folders. The first run is `configs/imwm.yaml` and `configs/imwm_moderate.yaml`
(`results/imwm_svd*`); running those configs again also adds the codes registered
since, because they use `codes: null`.

### Results

Full write-up: [results document](https://claude.ai/artifact/C1VdEpuetkR9WEGbDwEycz).

* **Strength.** With 8 blocks per coded bit, strength falls with length: 126 at
  n = 512, about 85 at n = 1024, 56 at n = 2048. Codes of equal length share one
  strength, the mean of all their searches. wPSNR on the test images ranges from
  37.90 to 42.20 dB.
* **Exact recovery out of 60**, moderate / hard set. With no attack, 45 of the 46
  configurations recover 10/10; no ECC recovers 9/10.

  | Code | r3/4 | r2/3 | r1/2 | r1/3 | r1/4 |
  |---|---:|---:|---:|---:|---:|
  | LDPC | 54 / 33 | 52 / 30 | 57 / 33 | 58 / 32 | 56 / 24 |
  | Polar | 56 / 33 | 49 / 28 | 58 / 35 | – | 57 / 25 |
  | Turbo | – | – | 56 / 34 | 58 / 33 | – |
  | Convolutional | – | – | 55 / 31 | 57 / 29 | – |
  | BCH | – | 41 / 23 | 42 / 18 | 38 / 16 | – |
  | Reed–Solomon, erasures | – | 37 / 16 | 41 / 20 | 35 / 14 | – |
  | Reed–Solomon | – | 34 / 12 | 41 / 18 | 30 / 13 | – |
  | Reed–Solomon, interleaved (depth 4) | – | 32 / 9 | 37 / 14 | 25 / 9 | – |
  | Repetition | – | – | 27 / 9 | 29 / 12 | 20 / 8 |

  No ECC scores 22 / 5 and Hamming(7,4), r4/7, 34 / 16.

  | Concatenated code | n | Rate | Moderate / hard |
  |---|---:|---:|---:|
  | RS(72,64) + convolutional r1/2 | 1164 | 0.44 | 58 / 33 |
  | RS(72,64) + turbo r1/2 | 1160 | 0.44 | 58 / 32 |
  | RS(80,64) + convolutional r1/2 | 1292 | 0.40 | 56 / 33 |
  | RS(72,64) + LDPC | 1024 | 0.50 | 56 / 31 |
  | BCH t = 8 + LDPC | 1024 | 0.50 | 56 / 30 |
  | RS(96,64) + convolutional r1/2, BCJR and erasures | 1548 | 0.33 | 56 / 23 |
  | Four RS(24,16) + convolutional r1/2 | 1548 | 0.33 | 54 / 23 |
  | RS(96,64) + convolutional r1/2 | 1548 | 0.33 | 54 / 22 |

* **Extended test of the top 10** (`configs/top10.yaml`, `results/top10/analysis`).
  The ten configurations with the most moderate + hard recoveries, plus no ECC, at
  the same message and strengths. They were tested on all 100 images under the 77 attack
  settings that the uncoded pilot could still read: 7,700 attacked frames per code,
  plus 7,800 unwatermarked ones (no attack included). A sweep repeats the watermarked frames on 20 fresh
  images at 0.992, 0.996, 1.004 and 1.008 times each strength, within the standard
  error of the calibrated means.

  | Code | n | Recovered (95 % interval) | Moderate / hard, per 60 | False passes of 7,800 |
  |---|---:|---:|---:|---:|
  | Turbo r1/2 | 1032 | 85.1 % (83.4–86.7) | 57.4 / 36.1 | no check |
  | Polar r1/2 | 1024 | 85.0 % (83.4–86.6) | 57.1 / 36.6 | 32 |
  | Polar r3/4 | 684 | 84.8 % (83.1–86.4) | 55.8 / 35.7 | 31 |
  | LDPC r1/2 | 1024 | 84.3 % (82.7–85.9) | 56.8 / 35.6 | 0 |
  | Turbo r1/3 | 1548 | 84.2 % (82.5–85.8) | 57.3 / 33.3 | no check |
  | RS(72,64) + turbo | 1160 | 83.7 % (82.0–85.4) | 56.8 / 34.4 | 0 |
  | LDPC r1/3 | 1536 | 83.7 % (82.0–85.3) | 57.0 / 33.3 | 0 |
  | RS(80,64) + conv., erasures | 1292 | 83.6 % (81.8–85.3) | 56.6 / 33.2 | 2 |
  | RS(72,64) + conv. | 1164 | 83.4 % (81.7–85.2) | 56.7 / 33.1 | 2 |
  | RS(80,64) + conv. | 1292 | 83.3 % (81.6–85.0) | 56.5 / 32.6 | 0 |
  | No ECC | 512 | 60.9 % (56.7–64.7) | 27.1 / 5.0 | no check |

  * **A tie at this resolution.** The ten are within 1.8 points; every one beats no ECC
    by 22 to 24. Resampling images, the top three lead the concatenated codes and
    LDPC r1/3 by 1.1 to 1.8 points. But a change of strength under 1 % moves single
    codes by 0.8 to 2.9 points and reshuffles the order (turbo r1/3 is first at
    0.992 and last of the ten at 1.008), so the gaps between lengths are not a
    property of the code.
  * **Equal length is a clean comparison.** Polar r1/2 beats LDPC r1/2 (same n and
    strength) by 0.7 points (0.4 to 1.0), and by 0.65 to 1.1 at every strength of the
    sweep. Erasures add 0.25 points to RS(80,64) + convolutional, and gain at every strength.
  * **Where codes differ.** All ten recover at least 99 of 100 on 45 of the 77 attacks.
    Rate decides the rest: under salt & pepper 5 % the r1/2 codes recover about 90 of
    100 and the r1/3 codes about 50; under WebP 45 polar r3/4 recovers 47 and turbo
    r1/3 88. Global color changes cause 79 % of all failures, about half the frames for
    every code. Rotation of 1° defeats them all.
  * **Checks.** Polar's 11-bit CRC with a list of 8 passes 0.41 % of unwatermarked frames
    (32 of 7,800, spread over 27 images), as 8/2048 predicts; the earlier 1 in 2,240 was
    too few frames per code. The two polar codes also passed 5 watermarked frames with a
    wrong message, and RS(72,64) + convolutional 1. LDPC, RS(72,64) + turbo and RS(80,64) + convolutional had no false or wrong pass
    (under 0.05 % at 95 %).
  * **No carry-over.** On the 80 images that neither chose the codes nor the attacks,
    each of the ten is within 0.6 points of its 100-image score. On the original six
    attacks the 10-image scores hold up: polar r1/2 had 58 / 35 and now 57.1 / 36.6,
    RS(72,64) + convolutional had 58 / 33 and now 56.7 / 33.1.
  * **Recommendation.** LDPC r1/2 when the decoder's pass decides whether a watermark is
    present: 84.3 % with no false pass. Polar r1/2 recovers 0.7 points more but would
    flag about 1 in 250 unmarked images; turbo has no check at all.

* **Trade-off.** A longer code has more redundancy but less strength, so it starts
  with more raw errors. LDPC under WebP 60 goes from 7/10 at r3/4 to 10/10 at
  r1/4. Under salt & pepper 5% it goes from 8/10 to 0/10.
* **Reed–Solomon.** The decoder matches exact theory. It scores low alone because
  one wrong bit costs a whole byte and the errors are scattered bits. As the outer
  code of a concatenation it reaches the top group, because the inner decoder
  leaves it short bursts. Alone, interleaving is worse in all 12 paired comparisons,
  by 2 to 8 recoveries. Inside a concatenation it neither helps nor hurts.
  Errors-and-erasures decoding adds 0 to 6 recoveries on moderate attacks.
* **Concatenation.** An outer RS code lifts convolutional r1/2 by 2 to 3 recoveries
  and gives it, and turbo, a built-in check. Taking redundancy from LDPC for an
  outer code does not pay: LDPC r1/2 alone scores as well or better at the same n.
* **Sensitivity.** Under blur + JPEG 50, raw BER changes by up to 8× for a change
  of 0.25 in strength, so one strength per length is what makes codes of equal
  length comparable. Codes of different lengths still differ by this luck: the
  r2/3 column sits on a bad value. A second message at the same strengths moved
  scores by 1.2 on average and at most 6, and flipped 3.5% of frames, nearly all
  on weaker codes.
* **Checks.** 1 of 2,240 unwatermarked frames passed a check on the moderate set
  and none on the hard set; the pass was polar r2/3. One watermarked frame passed
  with a wrong message: hard-decoded polar r1/2, also seen with the second message.
  Polar has an 11-bit CRC. LDPC and the concatenated codes had neither kind of
  error.
* **Limits.** Rotation of 5° or more, cropping and translation stay near 50%
  raw BER because the library has no synchronization. Rotation 1° defeats every
  code, so the hard set's ceiling is 50. Global color changes are this method's
  weak point. With 10 images, the order inside the top group is not resolved.
* **First run.** With shared blocks every code had a strength of about 56 and the
  best scores were 57 / 25. Below n = 2048, soft-decoded LDPC, polar, turbo and
  convolutional codes held or gained on moderate attacks and gained 6 to 11 on hard
  ones with fixed votes. That run gave each code and image its own message, and it
  can be reproduced from commit `3d6d55a`.
* **Earlier run.** `results/imwm` used `dwtDct`, which quantizes one raw LL
  sample per block with no DCT and fails from JPEG 90 down. It also read
  resized images at their new size and let code length affect robustness. Its
  numbers should not be used.
