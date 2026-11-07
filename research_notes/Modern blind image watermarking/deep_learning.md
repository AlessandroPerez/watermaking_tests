# Deep-learning (neural) blind image watermarking for post-hoc embedding, 2018–2026, and how it compares with classical methods

Research date: 2026-11-03. Every number below was read from the paper or repository linked next to it, through the arXiv/ar5iv HTML full text or the GitHub API/README, unless it is marked **[UNVERIFIED]**. Abbreviations: "bit acc" = fraction of message bits decoded correctly (0.5 = chance); "TPR@x%FPR" = true positive rate at a fixed false positive rate; "dwtDctSvd" / "dwtDct" = the modes of the `invisible-watermark` (ShieldMnt) library, which is the user's library.

User context for reading these notes: 512-bit ECC-coded message, wPSNR 40 dB (PSNR ≈ 36.6 dB), 1024×1024 colour images, dwtDctSvd. It fails at rotation ≥1°, under crop and translation, and on about half of the frames under global colour changes. It survives JPEG down to Q50.

## Q1. Main neural methods: year, payload, PSNR, robustness, and which carry hundreds of bits blindly

### Takeaway
Neural post-hoc watermarking has moved from 30-bit/128×128 research models (HiDDeN 2018) to open 256-bit models that work at any resolution (Meta Video Seal 1.0 and Pixel Seal, 2025) and to a 1024-bit research model (ChunkySeal, Oct/Dec 2025). These run at PSNR ≈ 44–49 dB and keep ≥0.9 bit accuracy under rotation, moderate crops, colour changes, JPEG 40–80 and their combinations. Only a few methods carry hundreds of bits blindly:
- MBRS: 256 bits in the released weights, 625 bits in the paper. It is robust to JPEG but not to geometric attacks.
- InvisMark: 256 bits in the paper; the released weights carry 100 bits.
- Video Seal 1.0: 256 bits.
- Pixel Seal: 256 bits.
- ChunkySeal: 1024 bits.

TrustMark (100), StegaStamp (100), SynthID-O (136, closed), WAM (32) and CIN/HiDDeN/RivaGAN (30–64) carry less.

### Cited Findings

**HiDDeN (Zhu et al., Stanford, ECCV 2018)**
- Hides L=30 bits in 3×128×128 YUV images. The "Combined" noise model (Dropout, Cropout, Crop p=0.035, Gaussian σ=2, JPEG-Mask/JPEG-Drop) has mean PSNR(Y) 33.55 dB. The Crop-trained model has PSNR(Y) 35.20 dB. — [HiDDeN, arXiv 1807.09937](https://arxiv.org/abs/1807.09937)
- A model trained without noise reaches 50% bit acc (chance) under Crop and JPEG. Training against simulated JPEG raises real-JPEG bit acc to 85%. The Combined model reaches 94% under Cropout (specialised model 97%). The only baseline was the closed commercial Digimarc. — [HiDDeN](https://arxiv.org/abs/1807.09937)
- Later re-evaluations:
  - Meta's 48-bit HiDDeN on COCO, from the WAM paper: rotation ±10° 80.8% bit acc, crop 20% 93.3%, JPEG 50 77.3%, brightness 2.0 96.2%, at PSNR 38.2 dB. — [WAM, arXiv 2411.07231, Tables 1 and 7](https://arxiv.org/abs/2411.07231)
  - Video Seal's evaluation gives HiDDeN PSNR 30.36 dB on SA-1b. — [Video Seal, arXiv 2412.09492, Table 5](https://arxiv.org/abs/2412.09492)

**StegaStamp (Tancik, Mildenhall, Ng; arXiv Apr 2019, CVPR 2020)**
- Embeds 100 bits in 400×400 images. PSNR by message length: 29.88 dB (50 bits), 28.50 dB (100 bits), 26.47 dB (150 bits), 21.79 dB (200 bits).
- With ≥95% bit recovery, BCH gives at least 56 error-corrected bits. Training includes perspective warp, blur, colour, noise and JPEG.
- Real-world print/display→camera test: mean bit acc 98.7% over 1,890 captures (18 display/printer × camera combinations).
- A BiSeNet segmentation network detects and rectifies the marker before decoding.
- Source for all of the above: [StegaStamp, arXiv 1904.05343](https://arxiv.org/abs/1904.05343)

**RivaGAN (Zhang et al., MIT DAI-Lab, arXiv Sep 2019)**
- Video watermark with 32 bits (also 64). PSNR ≈ 42.05–42.71 dB.
- With 32 bits, bit acc is 0.992–0.998 after MJPEG, 0.981–0.998 after a crop to 80%, and 0.981–0.991 after scaling to 80%. — [RivaGAN, arXiv 1909.01285, Table 2](https://arxiv.org/abs/1909.01285)
- Bundled in `invisible-watermark`.
- In W-Bench, RivaGAN at 32 bits has PSNR 40.43 and TPR@0.1%FPR of only 10.12% / 12.50% after stochastic / deterministic regeneration. — [W-Bench/VINE, arXiv 2410.18775, Table 1](https://arxiv.org/abs/2410.18775)

**MBRS (Jia et al., USTC, ACM MM 2021)**
- 64 bits in 128×128 at PSNR 36.49 dB: BER 0.0092% after real JPEG Q50.
- **625 bits in 400×400 at PSNR 39.32 dB, SSIM 0.9504: BER 0.0012% after JPEG Q50.** StegaStamp in the same test (100 bits) had PSNR 32.36 dB and BER 0.2418%. — [MBRS, arXiv 2108.08211, Table 1](https://arxiv.org/abs/2108.08211)
- Without the "diffusion block", Crop (p=0.035) BER is 45.86%. With it (30 bits), BER is 4.15%. — [MBRS Table 2](https://arxiv.org/abs/2108.08211)
- The README says crop robustness is unstable (validation BER for Crop p=3.5% varies from 2% to 25%). It ships a 256-bit model (`MBRS_256_m256`). — [jzyustc/MBRS README](https://github.com/jzyustc/MBRS)
- Its training "crop" is a black mask that keeps pixel positions. "The crop considered by MBRS and CIN is simply a black mask applied on the image, keeping the original pixels at their exact location." Their geometric robustness is therefore "particularly weak". — [Video Seal §4.1](https://arxiv.org/abs/2412.09492); same point in [SyncSeal, arXiv 2509.15208](https://arxiv.org/abs/2509.15208)

**CIN (Ma et al., PKU, ACM MM 2022)**
- 30 bits, 128×128. With the combined noise pool: mean PSNR 39.28 dB, mean acc 99.64%.
- At PSNR 38.51 dB: Cropout 99.99%, Dropout 99.99%, Resize 50% 99.99%, JPEG Q50 99.24%.
- Source: [CIN, arXiv 2212.12678, Tables 1–2](https://arxiv.org/abs/2212.12678)

**FIN (Fang et al., AAAI 2023)**
- Flow-based invertible network with an invertible noise layer for black-box distortions. The abstract claims about 2 dB higher PSNR, more than 4% better extraction after JPEG Q50, and more than 95% accuracy under black-box distortions. **[UNVERIFIED: taken from a search summary of the AAAI page; paper not opened]** — [AAAI page](https://ojs.aaai.org/index.php/AAAI/article/view/25633)
- Retrained by CASIAL (64 bits, 128×128): JPEG 98.87%, but crop & resize 47.92%, shear 49.44%, rotation 49.52%. — [CASIAL, arXiv 2607.26729, Table "benchmark comparisons"](https://arxiv.org/abs/2607.26729)

**SSL watermarking (Fernandez et al., Meta/Inria, ICASSP 2022)**
- Embeds by iteratively optimising the image so that its features in a self-supervised (DINO ResNet-50) space carry the message.
- 30 bits at PSNR 40 dB on YFCC, BER by attack (word error rate in brackets where reported):

  | Attack | BER |
  |---|---|
  | Rotation 25° | 3.3% (WER 43.4%) |
  | Crop 0.5 | 4.8% |
  | Crop 0.1 | 28.9% |
  | Resize 0.7 | 2.1% |
  | Blur 2.0 | 0.5% |
  | JPEG 50 | 20.8% (WER 98.9%) |
  | Brightness 2.0 | 8.7% |
  | Contrast 2.0 | 8.4% |
  | Hue 0.25 | 2.5% |

  Source: [SSL watermarking, arXiv 2112.09581, Table 2](https://arxiv.org/abs/2112.09581)
- Slow: 2.19 s/image — [W-Bench Table 7](https://arxiv.org/abs/2410.18775); 0.45 s/image — [Stable Signature Table 1](https://arxiv.org/abs/2303.15435).

**TrustMark (Bui et al., Adobe; arXiv Nov 2023)**
- 100 bits, model at 256×256. A "resolution scaling" step (compute the residual at 256 px, upscale it, add it to the full-resolution image) lets it work at any resolution.
- Training noise: flip, crop and resize on every sample, plus 2 of 15 perturbations (JPEG, brightness, hue, contrast, sharpness, colour jitter, RGB shift, saturation, grayscale, several blurs, Gaussian noise, posterize).
- PSNR on CLIC / MetFace / DIV2K: TrustMark-Q 43.26 / 42.39 / 45.34 dB; TrustMark-B 41.53 / 40.20 / 43.87 dB.
- Bit acc under random noise: Q 0.95 / 0.95 / 0.96; B 0.97 / 0.97 / 0.97.
- Going from 32 to 200 bits lowers PSNR by 7.5 dB and bit acc by 11%.
- Encode/decode 125 / 25 ms on an RTX 3090.
- Source for all of the above: [TrustMark, arXiv 2311.18297, Tables 1, §4.3](https://arxiv.org/abs/2311.18297)
- The repo describes configurable BCH error correction over the 100 raw bits. — [adobe/trustmark README](https://github.com/adobe/trustmark)
- Independent re-tests:
  - Rotation (0–10°) 68.7% bit acc and Gaussian noise 69.9%. — [InvisMark Table 3](https://arxiv.org/abs/2411.07795)
  - Geometric group 71.4% bit acc (DIV2K: 70.5%). — [WAM Table 2](https://arxiv.org/abs/2411.07231)
  - Rotation 30° 0.50, crop 0.5 0.53. — [SyncSeal Table 4](https://arxiv.org/abs/2509.15208)
  - TrustMark-Q geometric 0.67 / 0.65 and combined 0.54 / 0.53. — [Pixel Seal Table 1](https://arxiv.org/abs/2512.16874)

**InvisMark (Xu et al., Microsoft; arXiv Nov 2024; cited by others as Xu et al. 2025 — venue not verified here)**
- 100-bit model: PSNR 51.4 dB, SSIM 0.998 on both DIV2K and DALL·E 3.
- Evaluation settings: JPEG q≥50; brightness, contrast and saturation at 0.75 / 1.25; rotation 0–10°; RandomResizedCrop scale 0.75–1.0; perspective 0.1; Gaussian noise σ 0.04.
- Bit acc under those attacks: ≥97.3% for every attack (rotation 97.4%, RandomResizedCrop 97.3%, JPEG 99.5%, contrast 99.9% on DIV2K).
- **256-bit model:** PSNR 47.9 / 47.8 dB, SSIM 0.997. Bit acc ≥97.7% for every attack. With a 128-bit UUID plus BCH inside the 256 bits, full-decode success is 98.9% / 92.7% under JPEG, 98.9% / 99.9% under rotation and 95.2% / 99.4% under RandomResizedCrop (DIV2K / DALL·E 3).
- Source for all of the above: [InvisMark, arXiv 2411.07795, Tables 1–6](https://arxiv.org/abs/2411.07795)
- The released checkpoint has **100 bits with no ECC**. — [microsoft/InvisMark README](https://github.com/microsoft/InvisMark)
- Independent re-tests:
  - Pixel Seal paper (94 usable bits): geometric 0.77, combined 0.94 / 0.98. — [Pixel Seal Table 1](https://arxiv.org/abs/2512.16874)
  - SynthID paper: "Spatial" bit acc 76.40%, "Combination worst" 52.60%. — [SynthID-Image Table 3](https://arxiv.org/abs/2510.09263)

**Watermark Anything, WAM (Sander et al., Meta; arXiv Nov 2024, ICLR 2025)**
- Treats watermarking as segmentation: it localises the watermarked pixels and decodes 32 bits. PSNR 38.3 dB on COCO (TrustMark 40.3, HiDDeN 38.2, DCTDWT 37.0).
- Bit acc on COCO (TPR in brackets where reported):

  | Attack | Bit acc |
  |---|---|
  | Crop 20% | 88.8% |
  | Crop 50% | 95.9% |
  | Rotation ±10° | 77.0% (TPR 97.7%) |
  | Perspective 0.5 | 96.0% |
  | Brightness 2.0 | 99.9% |
  | Contrast 2.0 | 99.9% |
  | Hue ±0.1 | 100% |
  | JPEG 50 | 99.0% |
  | Splicing 10% | 94.2–96.5% |

- Can extract five separate 32-bit messages (160 bits in total) from five 10% areas.
- Stated limitation: "WAM's capacity is limited to 32 bits, and training on larger messages is challenging."
- Source for all of the above: [WAM, arXiv 2411.07231, Tables 1, 2, 7; §5.5; §6](https://arxiv.org/abs/2411.07231)

**Video Seal (Fernandez et al., Meta; arXiv Dec 2024)**
- v0.0 carries 96 bits; v1.0 (March 2025) carries 256 bits. — [facebookresearch/videoseal README](https://github.com/facebookresearch/videoseal)
- Image results for v0.0 on SA-1b: PSNR 47.39 dB, SSIM 0.999. Bit acc: valuemetric 0.93, geometric 0.83, compression 0.99, combined 0.91 (log10 p = −18.4).
- Baselines in the same table:
  - TrustMark: geometric 0.65, combined 0.53.
  - MBRS: geometric 0.52, combined 0.50.
  - CIN: geometric 0.52, combined 0.50.
  - WAM: geometric 0.81, combined 0.86.
- Source: [Video Seal Tables 4–5](https://arxiv.org/abs/2412.09492)
- In the Pixel Seal evaluation, Video Seal 1.0 (256 bits) scores PSNR 48.7, geometric 0.83 / 0.82 and combined 0.69 / 0.70. — [Pixel Seal Tables 1–2](https://arxiv.org/abs/2512.16874)
- In ChunkySeal's table, Video Seal 256-bit has PSNR 44.42 dB with an 11.0M-parameter embedder and a 33.0M-parameter extractor. — [ChunkySeal Table 3](https://arxiv.org/abs/2510.12812)

**Pixel Seal (Souček et al., Meta; arXiv 18 Dec 2025) — the current open Meta state of the art**
- **256 bits.** Embedder: U-Net with 43.8M parameters. Extractor: ConvNeXt-v2 Tiny with 33.4M parameters. Trained adversarially only, with no perceptual loss, and with JND attenuation.
- On 1,000 Meta AI images at 1280×1280: PSNR 48.9 dB, SSIM 0.9905.
- Bit acc by group (Meta AI images / SA-1b photos): identity 1.00 / 1.00, valuemetric 0.97 / 0.98, compression 0.98 / 0.99, **geometric 0.95 / 0.93, combined 0.91 / 0.94**. No other method passes 0.84 on geometric.
- Per-attack bit acc on Meta AI images:

  | Attack | Bit acc |
  |---|---|
  | Rotation 5°, 10°, 30°, 45°, 90° | 0.99, 0.99, 0.99, 0.98, 0.99 |
  | Crop 0.32, 0.45, 0.55, 0.63, 0.71, ≥0.77 | 0.58, 0.81, 0.90, 0.95, 0.98, 0.99 |
  | Perspective 0.1 to 0.8 | 1.00 to 0.87 |
  | Brightness 0.1, 0.25, 2.0 | 0.80, 0.98, 0.91 |
  | Contrast 0.1, 2.0 | 0.85, 0.92 |
  | Hue −0.4 to +0.5 | 0.97–1.00 |
  | Grayscale | 1.00 |
  | Gaussian blur, kernel up to 17 | 1.00 |
  | JPEG 40, 50 | 0.96, 0.97 |
  | JPEG 40 + crop 0.71 + brightness 0.5 | 0.86 |
  | Same, with JPEG 60 / JPEG 80 | 0.91 / 0.96 |

- Source for all of the above: [Pixel Seal, arXiv 2512.16874, Tables 1–2 and appendix attack table](https://arxiv.org/abs/2512.16874)

**ChunkySeal (Petrov, Fernandez, Souček, Elsahar; Oxford + Meta; arXiv Oct 2025, v2 20 Dec 2025)**
- **1024 bits (0.0052 bpp).** PSNR 45.32 ± 2.16 dB, SSIM 0.995.
- Bit acc on SA-1B: rotation ≤10° 98.27%, resize 71–95% 99.74%, crop 77–95% 98.25%, brightness 0.5–1.5× 98.99%, contrast 99.54%, JPEG Q50–80 98.79%, overall 99.15%.
- Cost: an embedder of 1,022.7M parameters and an extractor of 773.7M parameters.
- Source: [ChunkySeal, arXiv 2510.12812, Table 3](https://arxiv.org/abs/2510.12812)
- Theory from the same paper:
  - Under a PSNR constraint alone, capacity should exceed 2 bpp.
  - Conservative bounds at PSNR 42 dB for 256×256 images: about 3,013 bits robust to crop-and-rescale 50%, and 904 bits robust to crop-and-rescale 75%.
  - "Recent methods operate far below the achievable bounds, often by orders of magnitude." — [ChunkySeal Table 1, abstract](https://arxiv.org/abs/2510.12812)

**SynthID-Image (Gowal et al., Google DeepMind; arXiv 10 Oct 2025)**
- Post-hoc and model-independent, applied by an encoder after generation. Used on more than 10 billion images and video frames.
- The external variant, SynthID-O, encodes **136 bits** in 512×512 images.
- TPR@0.1%FPR: aggregated 99.98%, "Combination worst" 98.06%, "Spatial worst" 99.97%. Payload bit acc: aggregated 99.59%, Spatial 99.82%. Evaluated without ECC.
- Not open: available "through partnerships".
- Source: [SynthID-Image, arXiv 2510.09263, §8, Tables 1, 3](https://arxiv.org/abs/2510.09263)

**DWSF (arXiv Oct 2023; venue not verified here)**
- Embeds a fixed 128×128 neural watermark in sparse random blocks. A segmentation network locates and rectifies the blocks, and the decoded messages are fused.
- PSNR 42.07 / 47.38 / 46.12 dB (ImageNet / LabelMe / OpenImages).
- Bit acc on ImageNet: rotation ±30° 99.99%, crop 0.7–1.0 98.20%, resize 0.5–2× 98.61%, padding 99.04%, colour jitter 0.5–1.5 99.96%, JPEG 50–100 98.11%.
- On the same attacks, MBRS scores rotation 68.38% and crop 68.68%.
- Source: [DWSF, arXiv 2310.14532, Tables 1–3](https://arxiv.org/abs/2310.14532)
- Payload size not confirmed. The paper discusses a 30-bit example. **[UNVERIFIED payload]**

**CASIAL (arXiv 29 Jul 2026)**
- 64 bits at 128×128, with all 11 baselines retrained under identical settings.
- CASIAL: rotation 99.48%, crop & resize 98.44%, shear 99.52%.
- Retrained baselines at 64 bits on crop & resize / rotation: Video Seal 51.48% / 97.09%, ChunkySeal 82.29% / 87.85%, MBRS 52.34% / 50.78%.
- Source: [CASIAL, arXiv 2607.26729](https://arxiv.org/abs/2607.26729)

### Inferences
- Methods with hundreds of bits that are also robust to geometric attacks exist only from 2024–2025: InvisMark-256 (paper only), Video Seal 1.0, Pixel Seal and ChunkySeal. The earlier high-payload model, MBRS-625, is robust only to non-geometric attacks. A large payload does not imply geometric robustness. It comes from training with real geometric augmentations at scale.
- Published results do not cover exactly 512 bits. Only ChunkySeal (1024) exceeds 512, and it costs about 1.8B parameters. A 512-bit ECC-coded message would fit only in ChunkySeal, or would need two 256-bit models or two passes (untested).
- Neural PSNR defaults (44–51 dB) are much stricter than the user's PSNR of about 36.6 dB. Neural methods are reported at a less visible operating point than the user's dwtDctSvd. Most expose a strength knob (WAM α_JND, Video Seal α_w, TrustMark α_max), so robustness could be traded upward.

### Gaps
- FIN numbers were not read from the paper. DWSF payload is unconfirmed.
- I found no evaluation of any neural model at exactly 512 bits, or of 1024×1024 natural photos at a matched PSNR of 36–37 dB.
- Small-angle rotation (about 1°) is rarely reported separately. Pixel Seal reports 5° and above; InvisMark and ChunkySeal report ranges of 0–10° and ≤10°.
- Pure translation (shift with padding, no content loss) is tested only by DWSF ("Padding": 99.04–100%). Most papers fold it into crop.

## Q2. How the neural papers rate classical baselines (DWT-DCT, DWT-DCT-SVD) against neural ones, especially under geometric and colour attacks

### Takeaway
Every neural paper that includes a classical baseline shows dwtDct or dwtDctSvd near chance (≈50% bit acc) under any geometric change: rotation, crop or resized crop, perspective, flip. It is also weak (≈47–66%) under stronger contrast, saturation, brightness, hue and RGB shifts. It stays strong (≥96%) under Gaussian blur, Gaussian noise, posterize and erasing, where it matches or beats some neural models. Under JPEG the result depends on mode and strength: dwtDctSvd scores 80.8% at q≥50 in InvisMark's test, while dwtDct falls to 49.8% at Q50 in WAM's test. These baselines were always run at library defaults, with no synchronisation and no ECC.

### Cited Findings
- **InvisMark (100 bits, DIV2K / DALL·E 3)**
  - dwtDctSvd has PSNR 38.3 / 40.2 dB; InvisMark 51.4 dB.
  - Bit acc for dwtDctSvd vs InvisMark:

    | Attack | dwtDctSvd | InvisMark |
    |---|---|---|
    | Rotation 0–10° | 52.6 / 54.0% | 97.4 / 98.7% |
    | RandomResizedCrop 0.75–1.0 | 52.4 / 51.7% | 97.3 / 99.8% |
    | Perspective 0.1 | 50.1 / 50.3% | 100 / 100% |
    | Flip | 52.6 / 54.3% | — |
    | Contrast 0.75/1.25 | 62.8 / 56.3% | 99.9 / 99.9% |
    | Saturation 0.75/1.25 | 59.2 / 58.3% | 100 / 100% |
    | RGB shift 0.05 | 53.5 / 47.8% | 100 / 100% |
    | ColorJiggle | 81.4 / 76.3% | 100 / 100% |
    | Brightness 0.75/1.25 | 93.6 / 92.5% | 99.7 / 99.8% |
    | JPEG q≥50 | 80.8 / 79.6% | 99.5 / 97.5% |
    | Gaussian blur | 99.7 / 98.2% | 100% |
    | Gaussian noise σ 0.04 | **98.8 / 96.4%** | 100% |
    | Posterize 4 bits | 99.5 / 98.6% | 100% |
    | Random erasing | 99.8 / 99.1% | — |

  - On Gaussian noise, dwtDctSvd beats TrustMark (69.9 / 65.1%) and StegaStamp (88.9 / 84.8%).
  - The authors' wording: "Traditional watermarking techniques like dwtDctSvd typically struggle in the presence of noise, with a few exceptions such as RandomErasing and GaussianBlur."
  - Source: [InvisMark, Tables 1–3, §3.2](https://arxiv.org/abs/2411.07795)
- **TrustMark (100 bits)**
  - dwtDctSvd: PSNR 39.13 / 38.02 / 41.14 dB on CLIC / MetFace / DIV2K. Bit acc 1.00 / 0.99 / 1.00 clean, but **0.52 / 0.51 / 0.52 after noise**.
  - Every noised sample in this test includes flip, crop and resize, so a near-chance score is expected for an unsynchronised classical method.
  - TrustMark-Q under the same noise: 0.95–0.96.
  - "dwtDctSvd performance is close to random chance for RGB shift."
  - In the ImageNet-C setting (no geometric attacks): dwtDctSvd 0.61 vs TrustMark 0.95, at PSNR 38.96 vs 38.87.
  - Source: [TrustMark, Tables 1–2, §4.3](https://arxiv.org/abs/2311.18297)
- **WAM**
  - Baseline: invisible-watermark DCTDWT (`github.com/ShieldMnt/invisible-watermark`, "the one used in Stable Diffusion"), 48 bits, PSNR 37.0 dB on COCO.
  - Bit acc for DCTDWT vs WAM on COCO:

    | Attack | DCTDWT | WAM |
    |---|---|---|
    | None | 91.4% | — |
    | Crop 20% | 50.2% | 88.8% |
    | Crop 50% | 50.4% | 95.9% |
    | Rotation ±10° | 50.7% | 77.0% |
    | Perspective 0.1 | 51.8% | 99.8% |
    | Horizontal flip | 50.2% | 100% |
    | Brightness 1.5 | 60.9% | — |
    | Brightness 2.0 | 49.4% | 99.9% |
    | Contrast 1.5 | 63.4% | — |
    | Contrast 2.0 | 49.4% | 99.9% |
    | Hue −0.1 | 66.7% | — |
    | Hue +0.1 | 81.2% | — |
    | Saturation 1.5 | 61.7% | — |
    | Saturation 2.0 | 47.4% | 100% |
    | Gaussian blur 3 | 77.0% | — |
    | Median filter 3 | 53.2% | — |
    | JPEG 50 | 49.8% | 99.0% |
    | JPEG 80 | 50.5% | 99.9% |
    | Crop 50% + brightness 1.5 + JPEG 80 | 49.9% | — |

  - Detection TPR: geometric 0.0%, valuemetric 13.6%.
  - Source: [WAM, Tables 1, 2, 7; App. D.3](https://arxiv.org/abs/2411.07231)
  - WAM's DCTDWT is most likely the `dwtDct` mode, not dwtDctSvd. Stable Diffusion's script uses `dwtDct`. **[UNVERIFIED: the mode was not stated explicitly in the WAM text I read]**
- **Stable Signature (ICCV 2023)**
  - Baseline: Dct-Dwt (invisible-watermark, as used by Stable Diffusion), 48 bits at 512×512.
  - Dct-Dwt: PSNR 39.5 / SSIM 0.97. Bit acc: none 0.86, crop to 10% of area 0.52, brightness 2.0 0.51, combined (crop 50% + brightness 1.5 + JPEG 80) 0.51.
  - Neural post-hoc baselines in the same table (PSNR, then bit acc none / crop / brightness / combined):
    - HiDDeN: 32.0 dB; 0.99 / 0.97 / 0.99 / 0.98.
    - FNNS: 32.1 dB; 0.93 / 0.93 / 0.91 / 0.93.
    - SSL: 31.1 dB; 1.00 / 0.73 / 0.93 / 0.66.
  - The neural baselines run 7–8 dB lower in PSNR here.
  - Embedding time: Dct-Dwt 0.14 s/image, HiDDeN 0.11 s/image.
  - Source: [Stable Signature, arXiv 2303.15435, Table 1, §6.4, App. A.4](https://arxiv.org/abs/2303.15435)
- **W-Bench (30 bits, 512×512)**
  - DWTDCT: PSNR 40.46. DWTDCTSVD: PSNR 40.40, SSIM 0.9799.
  - TPR@0.1%FPR for DWTDCTSVD under generative edits:

    | Edit | DWTDCTSVD TPR@0.1%FPR |
    |---|---|
    | Stochastic regeneration | 3.12% |
    | Deterministic regeneration | 1.43% |
    | InstructPix2Pix | 3.82% |
    | UltraEdit (global) | 4.02% |
    | MagicBrush | 30.84% |
    | UltraEdit (local) | 24.56% |
    | ControlNet inpainting | 50.04% |
    | Image-to-video (SVD) | 0.76% |

  - DWTDCT is ≈0% everywhere.
  - Neural results on the same edits: StegaStamp 91.09 / 92.13% and VINE-Robust 99.66 / 99.98% after stochastic / deterministic regeneration.
  - W-Bench's conventional-distortion results for the classical methods appear only as plots (Fig. 9), not tables.
  - Source: [W-Bench/VINE, Table 1, App. D.3](https://arxiv.org/abs/2410.18775)
- **Zhao et al. (NeurIPS 2024)**
  - DwtDctSvd: PSNR 39.38 / SSIM 0.983 on COCO, and the lowest FID of the four methods tested (5.28).
  - VAE and diffusion regeneration attacks "consistently achieve over 99% removal rates for the DctDwtSvd, RivaGAN, and SSL watermarking methods". StegaStamp resists all but strong diffusion.
  - Source: [Zhao et al., arXiv 2306.01953, Table 1, §5.1](https://arxiv.org/abs/2306.01953)
- I found no neural paper that uses the `blind_watermark` library (guofei9987) as a baseline. Every classical baseline I found came from `invisible-watermark`. — the GitHub API lists `blind_watermark` as MIT with about 14.8k stars ([repo](https://github.com/guofei9987/blind_watermark)), but none of the papers above cite it.

### Inferences
- The neural papers' classical baselines fail on geometric and colour attacks in exactly the way the user sees: rotation ≥1°, crop, translation, and global colour changes on about half the frames. This failure is structural, not a matter of tuning. dwtDctSvd decodes block coefficients at fixed positions, with no synchronisation and no invariance to global gain or offset.
- These comparisons are somewhat unfair to classical methods. None adds a classical synchronisation template, an exhaustive search, or ECC, and some use the weaker `dwtDct` mode. They show that unsynchronised DWT-DCT(-SVD) loses to neural methods. They do not show that classical watermarking with synchronisation loses.
- Classical dwtDctSvd is not dominated under noise, blur, posterize, erasing, and JPEG at the user's strength. There the neural advantage is small or absent.

### Gaps
- No paper evaluates dwtDctSvd at 512 bits, at 1024×1024, or at the user's PSNR of about 36.6 dB.
- No neural paper I opened compares against a synchronised classical scheme (template, Fourier–Mellin, or feature-point based).

## Q3. Benchmarks (WAVES, W-Bench, MarkDiffusion, OmniSealBench, others): conclusions on classical vs neural under geometric, colour and regeneration attacks

### Takeaway
The benchmarks agree on three points:
1. Regeneration and generative editing remove most low-perturbation watermarks, classical and neural.
2. Geometric misalignment is the main remaining weakness even for neural methods.
3. Simple colour changes are mostly handled by modern neural methods.

Classical DWT-DCT(-SVD) appears only in W-Bench and OmniSealBench among these benchmarks; in W-Bench it is the worst of 11 methods. WAVES tests only neural and in-generation methods. MarkDiffusion covers only in-generation watermarks and does not apply to post-hoc use.

### Cited Findings
- **WAVES (An et al., 2024; arXiv Jan 2024, v3 Jun 2024)**
  - Covers Tree-Ring, Stable Signature and StegaStamp only, with 26 attacks.
  - Distortion ranges: rotation 9°–45°; resized-crop 10–50% of area; brightness and contrast +20–100%; blur kernel 4–20; noise σ 0.02–0.1; JPEG 90→10. The authors say these are "more conservative than most of the watermark papers".
  - For StegaStamp, rotation is the 5th-strongest attack (average TPR@0.1%FPR 0.357) and resized-crop the 6th (0.540). Brightness and contrast barely affect any of the three (≈0.998).
  - "Stable Signature is vulnerable to almost all regeneration attacks". Tree-Ring is vulnerable to adversarial embedding attacks and rinsing regenerations. "StegaStamp is mildly affected by regenerations".
  - "No single attack excels across all watermarking methods, yet regeneration attacks exhibit some level of consistent effectiveness."
  - Source: [WAVES, arXiv 2401.08573, §3–4, Table 3, App. F.1](https://arxiv.org/abs/2401.08573)
- **W-Bench (Lu et al., ICLR 2025)**
  - 11 methods, including DWTDCT and DWTDCTSVD. Edits: regeneration, global editing, local editing, image-to-video.
  - "Most methods fail to detect watermarks after such edits."
  - The methods that resist Gaussian blur also resist editing, because edits act like blurring in the frequency domain.
  - Best performers: VINE (SDXL-Turbo backbone, 100 bits, PSNR 37.3–40.5), StegaStamp (PSNR 29.65) and MBRS (PSNR 27.37).
  - Image-to-video remains unsolved: at most 39.60% TPR (TrustMark).
  - Source: [W-Bench/VINE, Table 1, §5, App. D.3](https://arxiv.org/abs/2410.18775)
- **MarkDiffusion (Pan et al., arXiv Sep 2025; JMLR vol. 27, 2026)**
  - A toolkit for in-generation watermarks in latent diffusion models: Tree-Ring, Ring-ID, ROBIN, WIND, Gaussian-Shading, PRC, SEAL, VideoShield.
  - It contains no post-hoc or classical methods, so it does not answer the user's question.
  - Source: [MarkDiffusion, arXiv 2509.10569, Table 1](https://arxiv.org/abs/2509.10569); [THU-BPM/MarkDiffusion, Apache-2.0](https://github.com/THU-BPM/MarkDiffusion)
- **Meta OmniSealBench (launched with Video Seal, Dec 2024; repo updated Jan 2026)**
  - Image models include TrustMark, InvisMark, FNNS, MBRS, CIN, SSL, WAM, PixelSeal and **DCTDWT**. The leaderboard is hosted as a Hugging Face Space.
  - Core code is MIT; "for different watermarking models, the LICENSE can vary".
  - Source: [facebookresearch/omnisealbench README](https://github.com/facebookresearch/omnisealbench); [leaderboard](https://huggingface.co/spaces/facebook/omnisealbench)
- **Local watermark robustness benchmark (arXiv 15 Sep 2026)**
  - Covers MaskWM, WAM, OmniGuard, TrustMark and PixelSeal across 55 transformations, each with and without SyncSeal.
  - "Signal distortions are often tolerated by the strongest methods, while geometric misalignment and generative local edits, such as inpainting and outpainting, can completely impair payload recovery."
  - "Geometric misalignment causes the sharpest reduction in payload recovery."
  - SyncSeal "partly restores" what geometric misalignment removes, but adds "a further fidelity cost across every evaluated method".
  - Outpainting reduces payload recovery to chance.
  - Source: [What Breaks Local Watermarks?, arXiv 2609.16832](https://arxiv.org/abs/2609.16832)
- **SynthID-Image's own benchmark of open post-hoc models at 512×512 (TPR@0.1%FPR, "Spatial worst")**
  - InvisMark 50.06%, StegaStamp 15.25%, TrustMark-Q 25.76%, Video Seal 1.0 51.62%, WAM 76.04%, SynthID-O 99.97%.
  - In "Color worst", StegaStamp (99.79%), TrustMark-Q (98.93%) and Video Seal 1.0 (99.69%) do well. InvisMark (69.58%) and TrustMark-P (66.32%) do not.
  - Source: [SynthID-Image, Table 1](https://arxiv.org/abs/2510.09263)

### Inferences
- Benchmarks other than the authors' own (WAVES, W-Bench, the SynthID evaluation, the local benchmark) consistently rank geometric transformations and generative edits as the hard cases, even for neural methods. Strong neural geometric robustness is recent, from InvisMark, Pixel Seal and ChunkySeal (2024–2025). It has not yet been confirmed by an independent benchmark at matching settings. For example, SynthID's test gives InvisMark 50% TPR on "Spatial worst", while InvisMark's own paper reports ≥97% bit acc.
- On regeneration, the classical dwtDctSvd is removed almost completely, and so are most neural methods at moderate strength. The exceptions are StegaStamp, VINE and MBRS in W-Bench, which pay for it with heavy distortion (PSNR 27–37 dB).

### Gaps
- I could not extract numeric OmniSealBench leaderboard results, including DCTDWT's rank. The leaderboard is a dynamic Hugging Face Space.
- "What Limits Robustness in Deep Image Watermarking" (arXiv 2609.01050, Sep 2026) has no HTML version and was not read. A search snippet says geometrically robust multi-bit schemes "operate at payloads of the order of tens to about one thousand bits". **[UNVERIFIED]**

## Q4. Known weaknesses of neural watermarks

### Takeaway
Neural watermarks have five main weaknesses:
1. Removal by diffusion/VAE regeneration, by adversarial perturbation, and (for content-agnostic schemes) by averaging.
2. Forgery, by transplanting a residual onto another image.
3. Payloads limited to a few hundred bits in practice.
4. Poor generalisation: robustness depends on the training augmentations, and published numbers often fall in independent tests.
5. GPU and memory cost: 10M–1.8B parameters versus a CPU-only classical transform.

They also produce visible artifacts in flat regions despite high PSNR. Classical dwtDctSvd shares the removal weaknesses and is more exposed to averaging and forgery, because its pattern does not depend on image content.

### Cited Findings
- **Regeneration and purification**
  - Theory: for low-perturbation watermarks, diffusion purification creates a fundamental trade-off between evasion and spoofing errors. — [Saberi et al., arXiv 2310.00076](https://arxiv.org/abs/2310.00076)
  - DwtDctSvd, RivaGAN and SSL are removed more than 99% of the time. — [Zhao et al.](https://arxiv.org/abs/2306.01953)
  - InvisMark falls to chance at attacked PSNR ≈ 25 dB. — [InvisMark §3.3](https://arxiv.org/abs/2411.07795)
  - WAM's tests at 32 bits:

    | Method | DiffPure, PSNR 24.9 | VAE attack, PSNR 25.5 |
    |---|---|---|
    | WAM | 49.1% | 53.7% |
    | TrustMark | 54.3% | 98.1% |
    | MBRS | 64.8% | 97.7% |
    | CIN | 61.9% | 67.6% |
    | DWTDCT | 49.5% | 49.5% |

    Source: [WAM Table 9](https://arxiv.org/abs/2411.07231)
- **Adversarial attacks**
  - TrustMark under I-FGSM (ε=8/255): bit acc 0.629, with the image degraded to PSNR 23.48. TrustMark's own learned remover (TrustMark-RM) reaches 0.553 bit acc at PSNR 48.48. — [TrustMark Table 3](https://arxiv.org/abs/2311.18297)
  - UnMarker is a universal attack that needs no detector feedback. It disrupts spectral amplitudes, "defeats traditional schemes", and lowers the best detection rate on semantic watermarks to 43%. — [UnMarker, arXiv 2405.08363](https://arxiv.org/abs/2405.08363)
  - WAVES grey-box embedding attacks push Tree-Ring's TPR@0.1%FPR to nearly zero. — [WAVES](https://arxiv.org/abs/2401.08573)
- **Forgery and steganalysis**
  - Copying the watermark residual onto a new image: InvisMark still decodes 97.6% of bits; TrustMark 67.0%. InvisMark proposes binding the watermark to content with a fingerprint stored in the C2PA manifest. — [InvisMark Table 4](https://arxiv.org/abs/2411.07795)
  - Averaging many watermarked images exposes content-agnostic patterns, which can then be removed or, for Tree-Ring, forged. After averaging, DwtDctSvd drops to 0.5722 accuracy, Gaussian Shading to 0.5615 bit acc, and RoSteALS to 0.2444 bit acc. Content-adaptive methods (HiDDeN, RivaGAN, SSL, StegaStamp) stay above 0.95. The extracted DwtDctSvd pattern "resemble[s] vertical lines like barcodes". — [Yang et al., NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/67b2e2e895380fa6acd537c2894e490e-Abstract.html)
- **Payload limits**
  - "WAM's capacity is limited to 32 bits, and training on larger messages is challenging." — [WAM §6](https://arxiv.org/abs/2411.07231)
  - TrustMark: going from 32 to 200 bits costs 7.5 dB of PSNR and 11% of bit acc. — [TrustMark §4.3](https://arxiv.org/abs/2311.18297)
  - StegaStamp: PSNR 28.5 dB at 100 bits and 21.79 dB at 200 bits. — [StegaStamp Table 2](https://arxiv.org/abs/1904.05343)
  - "The capacity of current robust methods remains limited to the scale of only a few hundred bits." 1024 bits needed about 1.8B parameters. — [ChunkySeal](https://arxiv.org/abs/2510.12812)
- **Generalisation and dependence on training augmentations**
  - HiDDeN without noise training: 50% under crop and JPEG. — [HiDDeN](https://arxiv.org/abs/1807.09937)
  - MBRS and CIN, trained with a mask-only "crop", score ≈0.50 under real geometric attacks. — [Video Seal](https://arxiv.org/abs/2412.09492); [SyncSeal Table 4](https://arxiv.org/abs/2509.15208)
  - InvisMark "were unable to replicate TrustMark's reported results for SSL and StegaStamp". — [InvisMark §3.2](https://arxiv.org/abs/2411.07795)
  - InvisMark's own rotation result (97.4%) contrasts with SynthID's "Spatial" bit acc of 76.40% and Pixel Seal's geometric 0.77. — [SynthID Table 3](https://arxiv.org/abs/2510.09263); [Pixel Seal Table 1](https://arxiv.org/abs/2512.16874)
  - FIN, retrained by CASIAL, keeps 98.87% under JPEG but drops to 47.92% under crop & resize. — [CASIAL](https://arxiv.org/abs/2607.26729)
- **Visibility despite high PSNR**
  - "Most are visible under close inspection, especially in flat areas, like the skies." — [Video Seal §4.2](https://arxiv.org/abs/2412.09492)
  - Video Seal 0.0's high PSNR (53.7 dB) "is due to its very localized artifacts, which yield, on average, a high metric value but are very visible". — [Pixel Seal §5.2](https://arxiv.org/abs/2512.16874)
  - InvisMark artifacts appear in clear blue skies. — [InvisMark §3.5](https://arxiv.org/abs/2411.07795)
  - TrustMark has lower PSNR and accuracy on cluttered images. — [TrustMark §4.6](https://arxiv.org/abs/2311.18297)
- **Compute cost**

  | Method | Embed GFLOPs | Extract GFLOPs | CPU embed time (s per second of video) |
  |---|---|---|---|
  | HiDDeN | 22.4 | 39.0 | 0.67 |
  | MBRS | 32.2 | 27.0 | 1.99 |
  | CIN | 16.6 | 17.9 | 1.04 |
  | TrustMark | 10.3 | 4.1 | 0.64 |
  | WAM | 42.6 | 68.7 | 3.64 |
  | Video Seal | 42.0 | 3.1 | 1.14 |

  Source: [Video Seal Table 6](https://arxiv.org/abs/2412.09492)
  - GPU time per image: VINE 0.0795 s using 4,982 MB of GPU memory; SSL 2.19 s. W-Bench omitted DWTDCT, DWTDCTSVD and RivaGAN from its timing table because their implementations are CPU-only. — [W-Bench Table 7](https://arxiv.org/abs/2410.18775)
  - ChunkySeal: 1,022.7M + 773.7M parameters. — [ChunkySeal Table 3](https://arxiv.org/abs/2510.12812)
- **Detection statistics**
  - Neural decoder bits on unwatermarked images are not i.i.d.: before whitening, one bit was 1 in 95% of images. Theoretical false-positive rates need whitening or empirical checks. — [Stable Signature App. B.5](https://arxiv.org/abs/2303.15435)

### Inferences
- Under regeneration, neural methods are not reliably better than classical. Both fail at moderate purification strength. Only heavily distorting models (StegaStamp, MBRS, VINE) survive mild regeneration.
- Security point for the user's setup: dwtDctSvd is content-agnostic, and the user embeds the same fixed 512-bit message in every image. That is exactly the case where averaging steganalysis reveals and removes or forges the pattern (see Yang et al.). This is an inference; the paper tested random or fixed keys per method, not this exact protocol.

### Gaps
- No paper quantifies averaging or forgery attacks against Pixel Seal, ChunkySeal or Video Seal 1.0.

## Q5. In-generation watermarks (a different setting; brief)

### Takeaway
Stable Signature, Tree-Ring, Gaussian Shading and similar methods watermark during diffusion generation, so they cannot be applied to existing photographs. They are noted here only for context. SynthID-Image, often grouped with them, is actually post-hoc but closed.

### Cited Findings
- **Stable Signature (Meta, ICCV 2023)** fine-tunes the latent-diffusion VAE decoder to embed 48 bits. Generation PSNR relative to the unwatermarked model is ≈30 dB. Bit acc: none 0.99, crop to 10% 0.95, brightness 2.0 0.97, combined 0.92. — [Stable Signature, Table 1](https://arxiv.org/abs/2303.15435) It is "vulnerable to almost all regeneration attacks". — [WAVES](https://arxiv.org/abs/2401.08573)
- **Tree-Ring and Gaussian Shading** place the watermark in the initial diffusion noise.
  - Tree-Ring is vulnerable to adversarial embedding attacks and rinsing regeneration. — [WAVES](https://arxiv.org/abs/2401.08573)
  - Both are content-agnostic and vulnerable to averaging steganalysis. — [Yang et al.](https://proceedings.neurips.cc/paper_files/paper/2024/hash/67b2e2e895380fa6acd537c2894e490e-Abstract.html)
  - Gaussian Shading is brittle to geometric transformations. — [SyncSeal](https://arxiv.org/abs/2509.15208)
  - Both are implemented in MarkDiffusion. — [MarkDiffusion](https://arxiv.org/abs/2509.10569)
- **SynthID-Image** is "post-hoc, model-independent", deployed on more than 10 billion images and frames, and not open-source. — [SynthID-Image](https://arxiv.org/abs/2510.09263)

### Inferences
- None of these can watermark the user's existing 1024×1024 photos. SynthID-Image technically could, but it is not available.

### Gaps
- Payload figures for Tree-Ring and Gaussian Shading were not verified here (Tree-Ring is commonly described as zero-bit detection; Gaussian Shading as multi-bit). **[UNVERIFIED]**

## Q6. Hybrid approaches: synchronisation plus neural decoding, or neural geometric correction plus classical embedding

### Takeaway
The most relevant hybrid is Meta's **SyncSeal** (Sep 2025). It is a standalone neural synchronisation watermark: it is embedded after any primary watermark, predicts the geometric transform, and inverts it before the primary decoder runs. It turned near-chance geometric robustness into 0.83–1.00 bit acc for CIN, TrustMark and WAM. It was not tested on a classical primary watermark. Other hybrids:
- **DWSF:** neural segmentation-based block synchronisation plus a neural decoder plus message fusion.
- **StegaStamp:** a segmentation network detects and rectifies the marker before decoding.
- **WMAR and template schemes:** template or corner-message synchronisation.

I found no published, evaluated pipeline of "neural geometric correction + classical DWT-DCT-SVD embedding".

### Cited Findings
- **SyncSeal (Fernandez, Souček, et al., Meta; arXiv 18 Sep 2025; cited as Fernandez et al. 2026)**
  - Embedder plus an extractor that regresses the transformation parameters, trained end-to-end with a discriminator.
  - Quality and speed: PSNR 43.9 dB, SSIM 0.994; 12 ms to embed and 12 ms to extract.
  - Average corner error in pixels (Rotate 10° / Crop 0.7 / Perspective 0.1):
    - SyncSeal (blind): 0.5 / 3.8 / 6.6.
    - SIFT + RANSAC (non-blind, needs the original): 1.8 / 1.6 / 1.5.
    - WMAR (blind): 5.5 / 55.1 / 49.3.
  - Bit acc without → with SyncSeal on 512×512 SA-1b images (Rotation 30° / Crop 0.5 / Perspective 0.3):

    | Primary watermark | Without SyncSeal | With SyncSeal |
    |---|---|---|
    | CIN | 0.49 / 0.50 / 0.50 | 1.00 / 0.83 / 0.84 |
    | MBRS | 0.50 / 0.50 / 0.50 | 0.88 / 0.57 / 0.63 |
    | TrustMark | 0.50 / 0.53 / 0.51 | 0.99 / 0.92 / 0.97 |
    | WAM | 0.50 / 0.99 / 0.68 | 1.00 / 0.97 / 0.98 |

  - Synchronisation "can be applied on top of existing watermarking methods".
  - Source for all of the above: [SyncSeal, arXiv 2509.15208, Tables 3–4, §4.4](https://arxiv.org/abs/2509.15208)
- **Independent check of SyncSeal (Sep 2026):** its benefit "varies widely across methods and transformations". It adds a fidelity cost to every method, and it improved MaskWM under several geometric transformations. — [arXiv 2609.16832](https://arxiv.org/abs/2609.16832)
- **Earlier synchronisation schemes, as surveyed by SyncSeal:**
  - DWSF: dispersed blocks plus synchronisation module.
  - Wang et al.: checkerboard template plus template-enhanced networks; detects crop size but not location.
  - LECA "SyncNet": predicts templates to estimate scale and offset.
  - WMAR: WAM-embedded corner messages.
  - SyncSeal's verdict on these: "not robust against the full range of geometric transformations and/or depend on template-matching algorithms."
  - Source: [SyncSeal §2](https://arxiv.org/abs/2509.15208)
- **DWSF** results with its neural synchronisation: rotation ±30° 99.99%, crop 98.20%, resize 0.5–2× 98.61%, padding/translation 99.04%, at PSNR 42–47 dB. — [DWSF Table 3](https://arxiv.org/abs/2310.14532)
- **StegaStamp** uses a BiSeNet segmentation network to "detect and rectify StegaStamps within a wide field of view image before decoding". — [StegaStamp §3](https://arxiv.org/abs/1904.05343)

### Inferences
- In principle, SyncSeal could sit in front of the user's unmodified dwtDctSvd: embed dwtDctSvd, then SyncSeal; at decode time, predict and invert the geometry, then run the dwtDctSvd decoder. This would address rotation, crop and translation without changing the classical library. It is untested. Risks:
  - SyncSeal's added signal, about 44 dB PSNR on its own, lowers total PSNR below the user's 36.6 dB.
  - The two signals could interfere.
  - Residual misalignment of a few pixels at 256-px scale (crop error 3.8 px) may still break a block-DCT decoder that needs pixel-exact alignment.
- It would not fix global colour changes, which need a gain- and offset-invariant decoder or colour normalisation. That is a different failure mode.

### Gaps
- SyncSeal code and weights: the `facebookresearch/videoseal` README I fetched does not mention SyncSeal. I could not confirm where it is released or under what licence.
- No paper evaluates neural synchronisation in front of a DWT-DCT(-SVD) watermark.

## Q7. Released code and weights from reputable organisations, with licences

### Takeaway
Meta, Adobe and Microsoft release usable post-hoc models under MIT. Meta's `videoseal` repository is the strongest option: Video Seal 1.0 (256 bits), Pixel Seal (256 bits) and ChunkySeal (1024 bits), all MIT. Adobe TrustMark (100 bits, MIT for code and model files, BCH built in) and Microsoft InvisMark (100-bit weights, MIT repo) follow. Google's SynthID-Image is not released. Several academic models are non-commercial or have no licence.

### Cited Findings
- **Meta `facebookresearch/videoseal` (MIT)**
  - Ships Video Seal v0.0 (96 bits, legacy), **Video Seal v1.0 (256 bits; March 2025)**, **PixelSeal (256 bits; Dec 2025)** and **ChunkySeal (1024 bits; Dec 2025)**, with model cards and checkpoint URLs.
  - "All models, training code, and evaluation tools released under MIT license." Last push 2026-07-02.
  - Source: [repo README](https://github.com/facebookresearch/videoseal); licence from the GitHub API.
- **Meta `facebookresearch/watermark-anything` (MIT)**
  - Code and a new SA-1B-trained model (32 bits) released under MIT on 12 Dec 2024. The paper's original COCO model is under a non-commercial licence. — [repo README](https://github.com/facebookresearch/watermark-anything)
- **Meta, other repositories**
  - `ssl_watermarking`: CC-BY-NC. — [README](https://github.com/facebookresearch/ssl_watermarking)
  - `stable_signature`: mostly CC-BY-NC. — [README](https://github.com/facebookresearch/stable_signature)
  - `omnisealbench`: MIT core; model licences vary. — [README](https://github.com/facebookresearch/omnisealbench)
- **Adobe `adobe/trustmark` (MIT)**
  - "The MIT license covers both the code in this repo and the model files". 100-bit payload with configurable error correction. Repo active (pushed 2026-11-03).
  - Variants referenced elsewhere: Q, B, C (40 bits, used by WAM) and P.
  - Source: [README](https://github.com/adobe/trustmark); [WAM App. D.3](https://arxiv.org/abs/2411.07231); [Pixel Seal](https://arxiv.org/abs/2512.16874)
- **Microsoft `microsoft/InvisMark` (MIT)**
  - Pretrained weights "with 100 encoded bits and no ECC included", downloaded from OneDrive. The 256-bit model from the paper is not listed. — [README](https://github.com/microsoft/InvisMark)
- **Google:** SynthID-Image is not open. The external SynthID-O variant is "available through partnerships". — [SynthID-Image](https://arxiv.org/abs/2510.09263)
- **Other repositories (licences from the GitHub API)**

  | Repository | Licence |
  |---|---|
  | `tancik/StegaStamp` | MIT |
  | `DAI-Lab/RivaGAN` | MIT |
  | `ShieldMnt/invisible-watermark` | MIT (includes RivaGAN) |
  | `guofei9987/blind_watermark` | MIT |
  | `jzyustc/MBRS` | no licence (weights on Google Drive) |
  | `rmpku/CIN` | no licence |
  | `Shilin-LU/VINE` | NTU "Dual License Agreement — Non-Commercial Use Only" |
  | `THU-BPM/MarkDiffusion` | Apache-2.0 |
  | `XuandongZhao/WatermarkAttacker` | MIT |
  | `umd-huang-lab/WAVES` | no licence |

  Sources: [StegaStamp](https://github.com/tancik/StegaStamp), [RivaGAN](https://github.com/DAI-Lab/RivaGAN), [invisible-watermark](https://github.com/ShieldMnt/invisible-watermark), [MBRS](https://github.com/jzyustc/MBRS), [CIN](https://github.com/rmpku/CIN), [VINE LICENSE](https://github.com/Shilin-LU/VINE)

### Inferences
- For the user's rule "every algorithm from an established library, used unmodified", the cleanest neural candidates are the `videoseal` package (`videoseal.load("pixelseal")`, `"videoseal"` or `"chunkyseal"`) and the `trustmark` pip package. Both are MIT, come from large organisations, and include weights. Of these, only ChunkySeal can hold 512+ bits in one pass.

### Gaps
- I did not verify the licence text inside each released checkpoint file, beyond the README statements.

## Q8. Bottom line: is neural overwhelmingly better than the user's classical dwtDctSvd, and where?

### Takeaway
- **Yes, overwhelmingly, for geometric attacks** (rotation, crop, resize, perspective, flip, and translation via crop or padding). In published tests, dwtDctSvd and dwtDct sit at 50–55% bit acc, while 2024–2026 neural models reach 0.93–0.99. Pixel Seal does this at 256 bits and ChunkySeal at 1024 bits, both near 45–49 dB PSNR.
- **Yes, for global colour changes** (contrast, saturation, RGB shift, strong brightness, hue). dwtDctSvd scores 47–66% versus 0.9–1.0 for neural models.
- **No, for JPEG ≥Q50, Gaussian noise, blur, posterize and erasing.** dwtDctSvd is already at 80–99.8% there, comparable to or better than several neural models (TrustMark under noise: 69.9%).
- **No, for regeneration or diffusion purification.** Both fail at moderate strength.
- **Payload is a real constraint:** only ChunkySeal (1024 bits, about 1.8B parameters) matches the user's 512 bits in a single open model.

### Cited Findings
- **Geometric attacks**
  - dwtDctSvd: rotation 0–10° 52.6%, RandomResizedCrop 52.4%, perspective 50.1%. InvisMark on the same attacks: 97.4%, 97.3%, 100%. — [InvisMark Table 3](https://arxiv.org/abs/2411.07795)
  - dwtDct: crop 20% 50.2% and rotation ±10° 50.7%, vs WAM 88.8% and 77.0%. — [WAM Table 7](https://arxiv.org/abs/2411.07231)
  - Pixel Seal (256 bits): rotation 5–90° 0.98–0.99; crop 0.55 0.90, 0.71 0.98. — [Pixel Seal appendix](https://arxiv.org/abs/2512.16874)
  - ChunkySeal (1024 bits): rotation ≤10° 98.27%, crop 77–95% 98.25%, resize 71–95% 99.74%. — [ChunkySeal Table 3](https://arxiv.org/abs/2510.12812)
- **Colour attacks**
  - dwtDctSvd: contrast 62.8%, saturation 59.2%, RGB shift 53.5%, ColorJiggle 81.4%. InvisMark on the same attacks: 99.9%, 100%, 100%, 100%. — [InvisMark Table 3](https://arxiv.org/abs/2411.07795)
  - dwtDct: brightness 2.0 49.4%, contrast 2.0 49.4%, saturation 2.0 47.4%, hue −0.1 66.7%. — [WAM Table 7](https://arxiv.org/abs/2411.07231)
  - Pixel Seal: brightness 2.0 0.91, contrast 2.0 0.92, hue ±0.4 ≥0.97. — [Pixel Seal](https://arxiv.org/abs/2512.16874)
- **Signal-processing attacks (no clear neural advantage)**
  - dwtDctSvd: Gaussian noise 98.8%, Gaussian blur 99.7%, posterize 99.5%, JPEG q≥50 80.8%. TrustMark-Q: noise 69.9%, JPEG 89.7%. — [InvisMark Table 3](https://arxiv.org/abs/2411.07795)
  - Neural JPEG-50 results: Pixel Seal 0.97 — [Pixel Seal](https://arxiv.org/abs/2512.16874); WAM 99.0% — [WAM](https://arxiv.org/abs/2411.07231); MBRS-625 BER 0.0012% — [MBRS](https://arxiv.org/abs/2108.08211).
- **Combinations**
  - dwtDct under crop 50% + brightness 1.5 + JPEG 80: 49.9%. — [WAM Table 7](https://arxiv.org/abs/2411.07231)
  - Stable Signature's comparison, combined attack: Dct-Dwt 0.51 vs HiDDeN 0.98. — [Stable Signature Table 1](https://arxiv.org/abs/2303.15435)
  - Pixel Seal under JPEG 40 + crop 0.71 + brightness 0.5: 0.86; at JPEG 80: 0.96. — [Pixel Seal](https://arxiv.org/abs/2512.16874)
- **Regeneration:** DWTDCTSVD TPR@0.1%FPR is 1.4–3.1% after regeneration. Most neural methods also lose most of their detection there; only StegaStamp (91–92%), VINE (91–99.98%) and MBRS (99.4–99.5%) hold up, with PSNR 27–40 dB. — [W-Bench Table 1](https://arxiv.org/abs/2410.18775)

### Inferences
- The user's three observed failures (rotation ≥1°, crop/translation, global colour on about half the frames) are where neural methods are overwhelmingly better: roughly 50% versus more than 90% bit accuracy in every comparison found.
- For JPEG, noise and blur, the user's current method is adequate. Switching to a neural method would not bring a large gain there.
- There are two non-ML-preferred paths. These are inferences, not tested results:
  - Keep dwtDctSvd and add synchronisation: a classical template or invariant domain, or SyncSeal as a learned add-on. Add colour normalisation or invariant features for colour attacks.
  - Accept a neural embedder where geometric robustness is required: Pixel Seal or Video Seal 1.0 at 256 bits (512 coded bits would need two 256-bit carriers or a lower code rate), or ChunkySeal at 1024 bits.
- Caveat when comparing at matched quality: neural defaults run at PSNR 44–49 dB, against the user's ≈36.6 dB. At the user's looser budget, neural methods would have extra robustness margin, but they would also become more visible. The papers note that PSNR understates the visibility of neural artifacts in flat regions.

### Gaps
- No head-to-head test at 512 bits, 1024×1024 and matched PSNR between dwtDctSvd (with or without synchronisation) and any neural model. This would have to be measured in the user's own harness.
- No independent confirmation yet of ChunkySeal's or Pixel Seal's geometric results outside Meta's own papers. CASIAL retrained ChunkySeal at 64 bits / 128×128 and got crop & resize 82.29% and rotation 87.85%, which is lower than Meta's 1024-bit high-resolution results. — [CASIAL](https://arxiv.org/abs/2607.26729)
