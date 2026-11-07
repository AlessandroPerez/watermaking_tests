# Classical (non-ML) blind image watermarking resilient to geometric / desynchronization attacks, 2005–2026

Scope: classical (no neural network) blind methods, 2005–2026, judged against the user's setup. That setup is a 512-bit ECC-coded message at wPSNR 40 dB (PSNR about 36.6 dB) in 1024×1024 colour images, embedded with invisible-watermark `dwtDctSvd`, which has no synchronization. Rotation of 5° or more, cropping and translation currently give about 50% raw BER.

Labels used below:
- **Verification:** **[V-full]** means the number was read in the full text. **[V-abs]** means it was read in the abstract or publisher metadata. **[UNVERIFIED]** means it came from a search snippet or secondary description, or I could not open the source.
- **Payload type:** **1-bit** means detection only (present/absent). **multi-bit** means the method carries a message.
- **BER conversion:** Ma et al. (2021) report "BEQ", the number of wrong bits out of 64 with no ECC. I converted BEQ to BER by dividing by 64; those conversions are mine.

---

## 1. Invariant-domain methods (Zernike / pseudo-Zernike, orthogonal moments, PHT/PHFM, Bessel–Fourier, quaternion and fractional moments, Fourier–Mellin / log-polar): best payload and robustness, and weaknesses

### Takeaway
Moment and Fourier–Mellin methods handle global rotation and scaling well. The best verified multi-bit moment result is about 160 bits on 256×256 at 42.5 dB with BER around 10⁻³ under 3–45° rotation (Xin, Zernike, 2005 thesis, basis of Xin–Liao–Pawlak 2007). Their recurring weakness is cropping and translation, because moments are computed about a centre or over the whole image; random bending and aspect-ratio change are also problems. Fourier–Mellin/ULPM (Kang 2010), re-implemented at 64 bits, gives about 8–9% BER at 5–30° rotation, 28% at 50% cropping and about 50% under aspect-ratio change. Neither family on its own fixes the user's rotation + crop + translation problem at 512 bits.

### Cited Findings
**Zernike / pseudo-Zernike (ZM/PZM)**
- **Pre-2005 baseline.** Kim & Lee (2003) "Invariant image watermark using Zernike moments", IEEE TCSVT. — [OpenAlex record / DOI](https://doi.org/10.1109/tcsvt.2003.815955) [V-abs title only]
- **Xin's 2005 PhD thesis (Univ. Manitoba), the basis of Xin, Liao & Pawlak, Pattern Recognition 40(12), 2007.** [V-full] — [Xin thesis PDF](https://mspace.lib.umanitoba.ca/bitstreams/072619e9-e7c0-4104-878e-f9590ebd8163/download); [PR 2007 DOI](https://doi.org/10.1016/j.patcog.2007.05.004)
  - **Type and method:** multi-bit, quantization of ZM/PZM magnitudes.
  - **Rotation:** 160-bit random messages on a 256×256 image at an average PSNR of 42.5 dB (ZM) and 46.4 dB (PZM). Over 15 rotation angles θ ∈ {3°, 6°, …, 45°}, the maximum BER was on the order of 10⁻³ (100 trials per angle). Bilinear rotation was used, with the black borders partially cropped back to the same size.
  - **Scaling:** tested with 80- and 160-bit payloads, for downscaling from 256×256 to 128–248 px followed by rescaling back to 256×256.
  - **Flipping:** BER 0.
  - **Payload range:** 64–256 bits were tested. More bits means lower PSNR, or higher BER at a fixed PSNR.
- **Xin thesis StirMark 3.1 table (Table 4.3).** [V-full; the column alignment was reconstructed from PDF text extraction, so check it against the PDF before quoting]
  - **Setup:** 512×512 images. The message is embedded in a centred unit disk of 256 px diameter, located at the decoder by a 16-bit auxiliary sequence. Payload is 64 information bits plus 16 auxiliary bits. Reported values are mean BER, and "−1" means extraction failed.
  - **Cropping:** 10%, 20% and 50% gave BER 0. 75% failed.
  - **Rotation:** −0.25° gave 0.0215. −2°, 10° and 90° gave 0.
  - **Scaling:** 0.25 failed. 0.5 gave 0.0020. 0.75, 0.9, 1.5 and 2.0 gave 0.
  - **Aspect ratio:** x0.8 gave 0.0020, x0.9 gave 0, y1.1 gave 0.0137.
  - **Line removal:** removing 17 rows/5 columns gave 0.0430.
  - **Failures:** shearing x=5% failed, and StirMark random bending failed.
  - **Author's summary:** the data "cannot be extracted in several cases including excessive scaling and cropping, shearing and random ba[e]nd".
  - **Source:** [Xin thesis](https://mspace.lib.umanitoba.ca/bitstreams/072619e9-e7c0-4104-878e-f9590ebd8163/download)
- **Numerical accuracy is a core weakness.** Xin found that "some of the Zernike moments computed in the conventional Cartesian way are inherently inaccurate, and hence not rotationally invariant". The design therefore avoids those moments and introduces polar-coordinate computation with interpolation-based resampling. — [Xin thesis abstract](https://mspace.lib.umanitoba.ca/bitstreams/072619e9-e7c0-4104-878e-f9590ebd8163/download) [V-full]

**Legendre / affine moment invariants (Zhang et al., IEEE TIP 2011)** [V-full] — [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3378516/)
- **Type:** 1-bit. The authors call this a "weak point": detection compares an invariant distance to a threshold.
- **Setup:** 8 grey images of 256×256 at PSNR about 40 dB. Embedding uses 210 moments (order M = 20).
- **Results:** detection rate 1 for 45° rotation, scaling 0.8 and two affine matrices. Detection rate **0 for 10% cropping**, against the authors' own method and Alghoniemy's.
- **Stated limitation:** it is "not robust to image cropping and histogram equalization, a common problem for the moment-based watermark algorithms".

**Polar harmonic transforms and other orthogonal moments** (papers located, but numbers not opened)
- Li, Li, Abraham & Pan, "Geometrically invariant image watermarking using Polar Harmonic Transforms", Information Sciences 199, 2012. Multi-bit, per its title and venue. — [DOI](https://doi.org/10.1016/j.ins.2012.02.062) [V-abs metadata only; payload and BER UNVERIFIED]
- Ma, Chang, Wang, Li, Wang & Shi, "Robust image watermarking using invariant accurate polar harmonic Fourier moments and chaotic mapping", Signal Processing 172, 2020. — [DOI](https://doi.org/10.1016/j.sigpro.2020.107544) [metadata only; numbers UNVERIFIED]
- Wang, Niu, Yang, Wang & Wang, "A new robust color image watermarking using local quaternion exponent moments", Information Sciences, 2014. — [DOI](https://doi.org/10.1016/j.ins.2014.02.158) [metadata only]
- Wang, Wang, Zhang & Xia, "Geometric correction based color image watermarking using fuzzy least squares support vector machine and Bessel K form distribution", Signal Processing, 2016 online / 2017. This is the Chunpeng Wang / Xingyuan Wang line of moment-based geometric correction. — [DOI](https://doi.org/10.1016/j.sigpro.2016.12.010) [metadata only]
- Wang, Yang & Cui, "An SVM-based robust digital image watermarking against desynchronization attacks", Signal Processing, 2008. This is the Xiang-Yang Wang / Hong-Ying Yang line, which learns geometric parameters for correction. — [DOI](https://doi.org/10.1016/j.sigpro.2008.03.005) [metadata only]
- Golabi et al., "Robust watermarking against geometric attacks using partial calculation of radial moments and interval phase modulation", Information Sciences, 2014. — [DOI](https://doi.org/10.1016/j.ins.2013.11.020) [metadata only]

**Fractional and quaternion moments, 2018–2026**
- **Hosny & Darwish (MTAP 2022).** Multi-channel fractional-order exponent moments, PHTs and RHFMs, with a 1D Sine chaotic map; embeds multiple watermarks in colour images. The abstract argues that "most of these schemes used inefficient, traditional computation methods of the moments, resulting in an inaccurate and inefficient performance". — [DOI / Springer OA](https://doi.org/10.1007/s11042-022-12282-8) [V-abs; payload and BER UNVERIFIED because the Springer full text was blocked]
- **Fu et al. (IEEE TCSVT 2023).** Robust *reversible* watermarking with fractional-order ZM/PZM. The abstract states that "existing [RRW] schemes basically cannot resist geometric attacks", and embeds in low-order FoZM/FoPZM. — [DOI](https://doi.org/10.1109/tcsvt.2023.3279116) [V-abs]
- **Sun, Zhang & Zhang (IET Image Processing 2026).** Robust reversible Tchebichef-moment watermarking. It embeds inside the inscribed circle and applies "a resynchronisation method tailored to the specific type of attack" before extraction. — [DOI](https://doi.org/10.1049/ipr2.70265) [V-abs]
- **Much recent moment work is zero-watermarking, not embedding.** Example: Xia et al., IEEE Access 2019, "null-watermarking" with precise quaternion PHFM. It "achieves the copyright protection without changing the original medical image", and claims robustness to scaling, rotation, aspect-ratio change and flipping. Further examples: Xia et al., KBS 2020 (local QPHFM multiple zero-watermarking) and Niu et al., JMIV 2022 (quaternion log-polar RHFM zero-watermarking). — [Xia 2019 IEEE Access](https://doi.org/10.1109/access.2019.2935174) [V-full abstract]; [Xia 2020 KBS](https://doi.org/10.1016/j.knosys.2020.106568) [title]; [Niu 2022 JMIV](https://doi.org/10.1007/s10851-022-01084-0) [title]

**Fourier–Mellin / log-polar**
- **Kang, Huang & Zeng, "Efficient general print-scanning resilient data hiding based on uniform log-polar mapping" (ULPM), IEEE TIFS 5(1), 2010.** [V-abs] — [DOI](https://doi.org/10.1109/tifs.2009.2039604)
  - **Type:** blind, multi-bit.
  - **Method:** ULPM is applied to the DFT *index* (u,v), and the bit is embedded directly in the Cartesian DFT coefficient. This "completely removes the interpolation distortion and the interference distortion" of earlier inverse-log-polar designs.
  - **Claims:** robustness to geometric distortion and general print-scan, plus efficient blind resynchronization.
- **Kang's ULPM re-implemented by Ma et al. (IEEE TCSVT 2021).** [V-full]
  - **Setup:** 64 bits with no ECC, PSNR 41.03 dB, 108 images (8 USC-SIPI colour and 100 BOSSBase grey).
  - **Rotation:** BEQ/64 was 2.35 at 1° (3.7%), 4.83 at 5° (7.6%), 5.93 at 30° (9.3%), 8.29 at 45° (12.9%) and 24.39 at 90° (38%).
  - **Cropping:** 8.11 at 25% (12.7%), 17.96 at 50% (28%) and 28.01 at 75% (44%).
  - **Scaling:** 11.79 at 0.5 (18%) and 18.80 at 2.0 (29%).
  - **Aspect ratio:** 0.9×1.1 gave 32.4 (about 50%, i.e. failure).
  - **Shearing:** 0.05 shear gave 28–31 (failure).
  - **JPEG QF50:** 1.28 (2%).
  - **Source:** [Ma et al. arXiv 2007.10240](https://arxiv.org/abs/2007.10240)
- **Fourier–Mellin and moment features break under random bending.** Ma et al. argue: "Frequency values and moments which are calculated from the whole image will also change severely after RBA, which severely limits the performance of these watermarking schemes." — [Ma et al. 2021](https://arxiv.org/abs/2007.10240) [V-full]
- **Pre-2005 log-polar baseline.** Lin, Wu, Bloom, Cox, Miller & Lui (2001) is RST-resilient, but Kawano & Kawamura state: "However, it is not resistant to cropping." — [Kawano & Kawamura arXiv 2601.18385](https://arxiv.org/abs/2601.18385) [V-full via HTML]
- **Image normalization (moment-based affine normalization).** Dong, Brankov, Galatsanos, Yang & Davoine (IEEE TIP 14(12), 2005) use a normalization invariant to affine transforms with multi-bit DS-CDMA embedding in the DCT, which is blind. Their mesh-based random-bending correction "is suitable for private watermarking applications, where the original image is necessary". — [HAL record / abstract](https://hal.science/hal-00086383) [V-abs]
- **Ma et al.'s verdict on normalization methods:** they "have weak performance under cropping distortions. Because cropping changes the moments calculated from the whole image. Meanwhile, most image normalization based methods have only one-bit capacity and high computational cost." — [Ma et al. 2021](https://arxiv.org/abs/2007.10240) [V-full]

### Inferences
- **Payload:** moment methods top out at roughly 100–200 bits on small (256²) discs. The verified best is about 160 bits at PSNR ≥ 42 dB, with rotation-only BER around 10⁻³. That is below the user's 512 coded bits.
- **Synchronisation needs a fixed centre:** they need the disc centre and radius to be recoverable, so arbitrary translation and asymmetric cropping break them. Xin's centred-disc design survives *centred* StirMark cropping up to 50%; the user's attack model includes off-centre crops and translations.
- **Fit with the user's setup:** the user's message is carried by `dwtDctSvd`, so an invariant-domain method would mean replacing the embedder rather than wrapping it. That conflicts with the user's rule to use library implementations only, with the watermark library unmodified.
- **ULPM as a Fourier–Mellin representative:** at 64 bits it already shows 7–13% raw BER at 5–45° and 28% at 50% crop. That is not enough at 8× the payload, even with ECC.
- **Zero-watermarking:** a large share of the 2018–2025 "geometrically invariant moment" literature is zero-watermarking. The image is not modified, and a feature/ownership share is registered externally. It cannot carry a 512-bit message *in* the image, so it is irrelevant to the user's goal.

### Gaps
- I could not open Xin–Liao–Pawlak PR 2007, Li et al. 2012 (PHT), Ma B. et al. 2020 (accurate PHFM), Wang C. et al. 2017, Wang X.-Y. et al. 2014, or Hosny & Darwish 2022. Their payload/BER tables are unverified; Elsevier and Springer full texts were blocked.
- No verified source for a moment-based scheme carrying ≥256 bits while surviving off-centre cropping plus rotation.
- Tsougenis et al., "Performance evaluation of moment-based watermarking methods: A review" (J. Systems & Software, 2012), was not accessible. — [DOI](https://doi.org/10.1016/j.jss.2012.02.045)

---

## 2. Template / pilot-based resynchronization and periodic (self-referencing, ACF) watermarks: are they still competitive, and how were they attacked?

### Takeaway
Explicit DFT-peak templates (Pereira & Pun, 2000) were broken by the template-estimation-and-removal attack (Herrigel, Voloshynovskiy & Rytsar, 2001). Their performance also hinges on template detection accuracy. Periodic, self-referencing watermarks (Kutter, 1998/99; Voloshynovskiy, Deguillaume & Pun, 2001) are resilient to that template attack. In 2021 the ACF scheme was still the strongest baseline for global and local geometric attacks at 64 bits: about 1% BER at 5° rotation and 50% crop, and 0% under aspect-ratio change. Symmetry-based self-reference (Ma et al., 2021) improved on it to about 0–0.25% BER for 5–45° rotation, 0% for 25–50% crop and ≤1% for StirMark random bending. Pilot grids remain an active line (Kawamura group 2024–2026), and NAWE (2026) still uses a periodic carrier with ACF+RANSAC lattice synchronization. For the user's rotation + crop + translation problem, this family is the most directly relevant.

### Cited Findings
- **Template attack (pre-2005 baseline).** The attack "estimates the corresponding template points in the FFT domain and then removes them using local interpolation". It was demonstrated against commercial watermark products and works with little quality loss. — [Herrigel, Voloshynovskiy & Rytsar 2001, UNIGE archive](https://archive-ouverte.unige.ch/unige:47768) [V-abs]
- **Ma et al. (2021) on templates:** "the performance of template based watermark highly depends on the detection accuracy of the template. Besides, such watermark is vulnerable to template removal attack [Herrigel 2001]." — [Ma et al. 2021](https://arxiv.org/abs/2007.10240) [V-full]
- **Ma et al. (2021) on periodic schemes:** "A watermark unit is periodically tiled … the period can be detected by auto-correlation function (ACF) or magnitude spectrum (MS) … Voloshynovskiy et al. proposed using local ACF to detect and restore local geometric distortions. Moreover, as stated in the paper proposing template removal attack, methods in this category are resilient to this attack." — [Ma et al. 2021](https://arxiv.org/abs/2007.10240) [V-full]
- **Head-to-head at 64 bits, no ECC, PSNR about 41 dB, 108 images (Ma et al., 2021).** [V-full; BER = BEQ/64, my conversion] — [Ma et al. 2021](https://arxiv.org/abs/2007.10240)
  - **Schemes compared:**
    - **V_ACF:** Voloshynovskiy, Deguillaume & Pun, "Multibit digital watermarking robust against local nonlinear geometrical distortions", ICIP 2001. A pre-2005 baseline, still the best periodic reference here.
    - **Ma 2021:** symmetry/auto-convolution synchronization.

  | Attack | V_ACF (2001) | Ma 2021 |
  |---|---|---|
  | Rotation 0.25° | 3.34 (5.2%) | 0.09 |
  | Rotation 5° | 0.75 (1.2%) | 0.05 (0.07%) |
  | Rotation 30° | 0.26 (0.4%) | 0.14 (0.2%) |
  | Rotation 45° | 0.51 (0.8%) | 0.16 (0.25%) |
  | Rotation 90° | 0.17 | 0.07 |
  | Crop 25% (both dims) | 0.66 (1.0%) | 0 |
  | Crop 50% | 0.69 (1.1%) | 0 |
  | Crop 75% (128×128 of 512×512 kept) | 9.82 (15%) | 5.54 (8.7%) |
  | Scaling 0.5–2.0 | ≤ 0.08 | 0 |
  | Aspect ratio 0.9×1.1, 1.5×0.8, 0.7×1.8 | 0 | 0 |
  | Shear up to 0.05 | ≤ 0.41 | 0 |
  | StirMark RBA strength 0.5 | 0.25 | 0.12 |
  | StirMark RBA strength 1.0 | 9.37 (14.6%) | 0.60 (0.9%) |
  | Crop 25% + rotation 30° | 1.12 (1.75%) | 0.16 (0.25%) |
  | JPEG QF50 | 0.21 | 0.16 |
  | 5×5 average filter | 14.75 (23%) | 13.66 (21%) |

  - **Ma 2021 method:** blind, multi-bit. The watermark unit is flipped to make it symmetric, embedded additively in the spatial domain, and synchronized with an auto-convolution function at the decoder.
  - **Weakness of both:** strong low-pass filtering, as the 5×5 average-filter row shows.
- **Ma 2021 publication details:** IEEE TCSVT 31(12): 4826–4839, Dec 2021, DOI 10.1109/TCSVT.2021.3055255. Authors are Zehua Ma, Weiming Zhang, Han Fang, Xiaoyi Dong, Linfeng Geng and Nenghai Yu (USTC). — [arXiv abstract page](https://arxiv.org/abs/2007.10240) [V-abs]
- **NAWE (Chaban, Kinakh, Rouzaire & Voloshynovskiy, arXiv, Sept 2026).** [V-full HTML] — [arXiv 2609.25972](https://arxiv.org/abs/2609.25972)
  - **Synchronization:** a periodic, perceptually masked carrier tiled over the image. The ACF is computed via Wiener–Khinchin on the residual, RANSAC fits lattice bases to give 2×2 affine hypotheses, and the image is inverse-warped with tiles folded and averaged. Translation, modulo the tile period, comes from cross-correlation with 68 keyed sync bits.
  - **Coding:** Polar code at rate 1/4 with a 16-bit CRC.
  - **Payloads:** 16–256 bits; the reference is 48 bits, so the Polar input is 64.
  - **Test setup:** 512×512 COCO images at PSNR 40 dB (swept 34–48 dB).
  - **Classical vs neural:** it is hybrid, using a pretrained neural denoiser as host estimator, but Wiener and BM3D variants are classical. BM3D (σ = 18) lands within about 0.01 BER of the neural denoisers.
  - **Results reported:** reference-condition BER of 0.07 across 34 attack arms. Qualitatively, translation and flip are "at the plotting floor" and rotation, shear and resizing have low BER. Exact per-attack BERs were not given in text, only in plots.
  - **Weakness:** "denoise and blurs, are excellent watermark suppressors".
- **Pilot grid for scaling (Kawano & Kawamura, IEICE Trans. Inf. & Syst. E107-D(9), 2024).** [V-full] — [Yamaguchi Univ. repository PDF](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741); [DOI](https://doi.org/10.1587/transinf.2023EDP7222)
  - **Method:** a grid-shaped pilot signal estimates the scaling rate. SIFT-anchored DFT regions carry the message.
  - **Setup and results:** see Section 5.
  - **Stated principle:** "redundancy is not effective against geometric attacks. The type and strength of geometric attacks need to be estimated."
  - **Cost:** the pilot costs about 3.4 dB PSNR.
  - **Related pilot work cited in that paper:** Su, Chang & Wu (IEEE TIFS 8(12), 2013), interest points plus extended pilot signals; and Álvarez-Rodríguez & Pérez-González (Signal Processing: Image Communication 17(8), 2002), an analysis of pilot-based synchronization for still images (pre-2005 baseline).
- **Grid pilot for full affine estimation (Kawano & Kawamura, arXiv Jan 2026; accepted to APSIPA Trans. Signal & Information Processing).** [V-full via HTML; BERs read from box plots, so approximate] — [arXiv 2601.18385](https://arxiv.org/abs/2601.18385)
  - **Pilot design:** a three-valued (−1/0/+1) grid pilot is embedded by QIM in the U channel. A Radon transform estimates grid angle and interval, giving the full transformation matrix up to a 180° ambiguity.
  - **Message and quality:** 300-bit watermark with **no ECC**. PSNR 38.29 dB without the pilot and 37.25 dB with it.
  - **High-res images (1080×1080 crops from 4608×3456):** estimation error was about 0 for rotation 0–90° and for anisotropic scaling 0.2–1.9. Watermark BER had median < 0.1 at all rotation angles (near 0 at 0° and 90°, higher at 45°) and median < 0.1 for anisotropic scale 0.5–1.5.
  - **Low-res images (256×256):** estimation is less reliable; composite attacks fail on 2–7 of 10 images depending on the pattern.
- **Su, Chang & Wu (IEEE TIFS 2013).** "uses a pilot signal to detect the embedding position of the watermark… The pilot signal is not used to correct errors". — [Kawano & Kawamura 2024](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741) [V-full secondary]; paper [DOI](https://doi.org/10.1109/tifs.2013.2282121) [abstract not opened; a repository description says SIFT-defined invariant regions plus an embedded pilot used to enlarge regions and so raise payload or confidence: UNVERIFIED]
- **Kang et al. 2003 DWT-DFT composite (pre-2005 baseline)** combined a DFT template with a DWT message ("robust to both affine transform and JPEG"). — [DOI](https://doi.org/10.1109/tcsvt.2003.815957) [title only]
- **Deguillaume, Voloshynovskiy & Pun (Signal Processing 83, 2003)** combined periodic and template ideas. — [DOI](https://doi.org/10.1016/s0165-1684(03)00172-5) [title only]
- **Print-cam frame and periodic patterns.**
  - Chen et al. (2020) note that pattern-based print-cam watermarks such as Nakamura et al. (2004) "are weak to cropping attacks".
  - Pramila et al. use "pseudorandom sequences and an autocorrelation function" in a frame-free print-cam method (SIVP 2012; JSS 2018 "Increasing the capturing angle…").
  - Sources: [Chen et al. 2020](https://www.mdpi.com/2076-3417/10/21/7494) [V-full]; [Gourrame et al. 2022](https://www.mdpi.com/2079-9292/11/2/266) [V-full]; [Pramila 2018 DOI](https://doi.org/10.1016/j.jss.2017.10.029) [title only]
- **Print-cam correlation detector (Gourrame et al., Electronics 2022).** Correlation detection with a threshold on erroneous chips of a 180-element mark, i.e. effectively a 1-bit, zero-bit-style detector. It sits on a DFT-magnitude ring of radius 70 at 512×512 and PSNR 40 dB. Geometry is corrected by detecting the ID-card frame with Hough lines and estimating a homography; the method relies on a visible frame. Their earlier MTAP 2019 paper is explicitly "zero-bit". — [Gourrame et al. 2022](https://www.mdpi.com/2079-9292/11/2/266) [V-full]

### Inferences
- **Template attack surface:** sparse DFT-peak templates are both removable and a single point of failure. Dense periodic or symmetric self-reference avoids a separate template and spreads synchronization energy over the payload carrier. This is why it survives cropping (any surviving tiles re-establish the lattice) and translation (cyclic shift search over one period).
- **Best fit for the user:** this family maps most directly onto the user's failure mode. Rotation, crop and translation are all global affine-plus-shift operations, which an ACF/lattice estimate plus a keyed shift search recovers.
- **Payload density gap:** the best verified figures are at 64 bits on 512² (Ma 2021, ~4,096 px/bit, uncoded) and up to 256 bits on 512² (NAWE, no per-payload BER stated). The user needs 512 coded bits on 1024², about 2,048 px/bit, which is twice the density of Ma's test. The user's lower PSNR target (~36.6 dB vs ~41 dB) gives roughly 4–5 dB more embedding power, which partly offsets this. I found no verified result at that operating point.
- **Template/pilot as a wrapper:**
  - **Pipeline:** a separate pilot (DFT peaks or a spatial grid à la Kawano 2026) could be added on top of the unmodified `dwtDctSvd` embed. At decode, one would estimate the affine transform from the pilot, invert it, and then search translation, i.e. block-grid phase, before calling the unmodified decoder.
  - **Costs:** about 1–3.4 dB PSNR for the pilot (per Kawano), and exposure to template-removal attacks if the pilot is sparse in DFT.
  - **Status:** this is an inference, not a tested design.

### Gaps
- I did not find post-2005 papers that specifically attack periodic/ACF watermarks (e.g. ACF-peak flattening). Ma et al. only repeat Herrigel's statement that periodic methods resist template removal.
- Kawano 2026 and NAWE report BER mainly in plots, so exact per-angle numbers are unavailable.
- I did not find original-paper numbers for Pereira & Pun (2000) or Kutter (1998/99); both are pre-2005 baselines in any case.

---

## 3. Feature-point and local-region methods (Harris–Laplace, SIFT, SURF, scale-space, local circular/affine regions): payload versus robustness to cropping and combined attacks

### Takeaway
Binding the mark to keypoint regions gives good resistance to cropping and RST, because surviving regions can still be decoded. Examples: Chen 2020 decodes 60 bits with BER 0 after 20–50% crop-off and 15–90° rotation on 1024×1024 images at about 42 dB. Per-region payload is small (tens of bits up to about 150), however. Detection depends on keypoint repeatability, which fails on smooth images, low-pass filtering and strong rescaling. Most published schemes are 1-bit or carry tens of bits, and multi-bit LDFT (Tian 2013) shows 8–13% BER at 64 bits under rotation and cropping.

### Cited Findings
- **Seo & Yoo (IEEE TSP 54(4), 2006).** Invariant regions from scale-space representation, with geometric normalization per region before embedding. Claims robustness to geometric transformations, cropping, filtering and JPEG. — [DOI](https://doi.org/10.1109/tsp.2006.870581) [V-abs; payload not in abstract]
- **Lee, Kim & Lee (Optical Engineering 45(3), 2006).** SIFT circular patches with polar mapping for rotation. "Our method belongs to the blind watermark." — [DOI](https://doi.org/10.1117/1.2181887) [V-abs]
- **Wang, Wu & Niu (IEEE TIFS 2(4), 2007).** Harris–Laplace local characteristic regions; the watermark is "repeatedly embedded by modulating the magnitudes of DFT coefficients" and recovered by a maximum-membership criterion. Claims robustness to RST, row/column removal, cropping and random bending. — [DOI](https://doi.org/10.1109/tifs.2007.908233) [V-abs; payload UNVERIFIED]
- **Gao, Deng, Li & Tao (IEEE TSMC-C, 2010).** Affine covariant regions extending Seo & Yoo. They note that existing schemes "few are resistant to cropping, nonisotropic scaling, random bending attacks (RBAs), and affine transformations". Uses graph-clustered stable regions, orientation alignment and indirect inverse normalization; tested on 100 Internet images. — [DOI](https://doi.org/10.1109/tsmcc.2009.2037512) [V-abs]
- **Tsai, Huang & Kuo (IEEE TIP, 2010 online; OpenAlex dates it 2010).** GA/knapsack selection of an optimal non-overlapping feature-region set, evaluated against StirMark. — [DOI](https://doi.org/10.1109/tip.2010.2073475) [V-abs]
- **Li, Yuan, Lu & Pan (Information Sciences, 2010).** Rotation-invariant embedding in scale-adapted characteristic regions. — [DOI](https://doi.org/10.1016/j.ins.2010.04.009) [title only]
- **Local moments in feature regions:**
  - Singhal et al., JVCIR 2009 (local Zernike). — [DOI](https://doi.org/10.1016/j.jvcir.2009.04.002) [title only]
  - Deng et al., Signal Processing 2009 (local Tchebichef). — [DOI](https://doi.org/10.1016/j.sigpro.2009.02.005) [title only]
  - Yuan, Pun & Chen, Signal Processing 2013 (local Zernike of binary patches). — [DOI](https://doi.org/10.1016/j.sigpro.2013.01.024) [title only]
- **Nasir, Khelifi, Jiang & Ipson (IET Image Processing, 2012).** End-stopped-wavelet feature points with normalized circular regions and keyed DCT-block embedding; blind. — [DOI](https://doi.org/10.1049/iet-ipr.2010.0421) [V-abs]
- **Tian, Zhao, Ni, Qin & Li (IEEE T-Cybernetics 43(6), 2013), LDFT.** [V-abs + V-full secondary] — [DOI](https://doi.org/10.1109/tcyb.2013.2245415); [Ma et al. 2021](https://arxiv.org/abs/2007.10240)
  - **Method:** a "local daisy feature transform" that is locally as well as globally invariant, partitioned by a BSP tree, with a bit embedded per leaf by logarithmic QIM.
  - **Abstract claims:** survives local and global desynchronization and "noninvertible cropping".
  - **Ma 2021 re-implementation at 64 bits:**
    - **Rotation:** 5° gave BEQ 8.59 (13.4%), 30° gave 7.56 (11.8%).
    - **Cropping:** 25% gave 3.0 (4.7%), 50% gave 5.44 (8.5%).
    - **Scaling:** 0.5 gave 24.5 (38%).
    - **RBA strength 1.0:** 5.83 (9.1%).
    - **JPEG QF50:** 24.1 (38%).
  - **Ma's verdict:** "its robustness to common image processing operations and global geometric distortions is weak."
- **Ma et al. on the family:** feature-based schemes are "[m]ost of them … one-bit watermark scheme[s]… feature based methods usually have higher computational cost." — [Ma et al. 2021](https://arxiv.org/abs/2007.10240) [V-full]
- **Kawano & Kawamura (2026):** SIFT-based methods are "one of the most robust methods against geometric attacks", but "the detection performance is still insufficient". — [arXiv 2601.18385](https://arxiv.org/abs/2601.18385) [V-full]
- **Chen, Ren, Zhu, Zhou, Seppänen & Keskinarkaus (Applied Sciences 10(21):7494, 2020), screen-cam.** [V-full] — [MDPI](https://www.mdpi.com/2076-3417/10/21/7494)
  - **Method:** local square feature regions from a modified Harris–Laplace detector plus SURF orientation. A 60-bit message is repeated in every region in DFT magnitudes; detection is positive if ≤ 8 bit errors.
  - **Setup:** host images are 1024×1024, with PSNR 42.3–44.1 dB across 8 images.
  - **Robust results (Table 2):** BER 0 on all 8 images for crop-off 20%, 30%, 40% and 50% and for rotation 15°, 30°, 45° and 90°.
  - **Partial results:** scaling 0.4–0.6 mostly works (BER ≤ 0.22), and scaling 0.3 fails (BER 0.17–0.47).
  - **Common processing:** JPEG 20% gives BER 0–0.28; 5×5 median gives up to 0.45.
  - **Stated limitations:** unstable keypoints on simple textures, failure when the image is strongly zoomed out, and computation time.
  - **On Fang 2019:** Fang et al. "needs to record the four vertices of the image in advance… cannot address orientation or scale desynchronization attacks".
- **Fang, Zhang, Zhou, Cui & Yu (IEEE TIFS 14, 2019; online 2018), screen-shooting.**
  - **Method:** intensity-based SIFT (I-SIFT) to locate regions, a "small-size template" repeatedly embedded in DCT so "at least one complete information region can survive", and cross-validation-based extraction. — [DOI](https://doi.org/10.1109/tifs.2018.2878541) [V-abs]
  - **Payload:** a secondary source says BCH(63,39) coding. [UNVERIFIED]
- **Fang et al. (IEEE TCSVT, 2019/2020), underpainting documents.** A flip-based autocorrelation arrangement so "a complete watermark region can be accurately located even if part of the document is recorded". — [DOI](https://doi.org/10.1109/tcsvt.2019.2953720) [V-abs]
- **Kawamura group, SIFT-based methods for the Japanese IHC ver.5 criteria (2017–2024).**
  - **Method:** SIFT-anchored regions carry 150 coded bits each.
  - **Luo et al. (2011) comparison:** Luo et al.'s SIFT+DFT method needs stored descriptors, so it is "not a completely blind watermarking", and it is 1-bit.
  - **Sources:** [Kawano & Kawamura 2024](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741) [V-full]. Kawamura & Uchida, IIH-MSP 2017, and Hayashi & Kawamura, APSIPA 2018, are cited there; a search snippet says the 2017 method "does not satisfy the criteria". [UNVERIFIED]

### Inferences
- **Fit for cropping:** feature-region schemes are the natural answer to *cropping*, since any region that survives decodes on its own.
- **Payload per region:** the payload per region (60–150 bits verified) is far below 512 bits. To carry 512 coded bits the user would need either:
  - (a) large regions, which is impractical on 1024² with several regions; or
  - (b) to split the codeword across regions, as Kawamura does, at the cost of needing several specific regions to survive.
- **Fit for the user's setup:** this also means replacing `dwtDctSvd`, which conflicts with the "library unmodified" rule.
- **Robustness profile:** feature-region methods inherit the keypoint detector's fragility to blur, JPEG and strong downscaling. LDFT shows that "locally invariant" features can be worse than periodic synchronization even under the geometric attacks they target.

### Gaps
- Payload and BER tables for Seo & Yoo 2006, Wang 2007, Gao 2010, Tsai 2011, Li 2010, Nasir 2012 and Su 2013 were not accessible (paywalled IEEE/Elsevier, and the ir.opt.ac.cn mirror refused connection).
- No verified multi-bit feature-region scheme carrying ≥256 bits in a ~1 Mpx image.

---

## 4. Geometric correction by registration or exhaustive search at the decoder (incl. Fourier-magnitude and log-polar registration)

### Takeaway
Blind decoder-side correction is done three ways: estimate parameters from a known embedded signal (template, pilot grid, periodic lattice, correction codes), search exhaustively over a bounded parameter space, or learn the parameters from invariant features (SVR/LS-SVM on moments). Exhaustive search is theoretically more reliable than template matching if the search space does not grow exponentially (Barni, 2005). In practice it is costly on large images, and per Kawano 2026 it often assumes the detector sees the image clipped to the watermarked region.

### Cited Findings
- **Barni (IEEE Signal Processing Letters 12(2), 2005).** "if the size of the search space does not increase exponentially, both methods [exhaustive search and template matching] provide asymptotically good results … the exhaustive search approach outperforms template matching from the point of view of reliable detection." — [DOI](https://doi.org/10.1109/lsp.2004.840872) [V-abs]
- **Zheng, Liu, Zhao & El Saddik (ACM Computing Surveys 39(2), 2007).** The two main RST categories are to "rectify the RST transformed image before conducting watermark detection" or to "embed and detect watermark in an RST invariant or semi-invariant domain". — [DOI](https://doi.org/10.1145/1242471.1242473) [V-abs]
- **Kawano & Kawamura (2026) on brute force:** "a brute force search is required to synchronize the images" for Fourier and Zernike approaches, and "such methods are computationally expensive". Also: "Many conventional watermarking methods that claim robustness against geometric attacks assume the use of clipped images for detection. Consequently, watermarking techniques that rely on brute-force synchronization cannot be regarded as truly robust against geometric attacks." — [arXiv 2601.18385](https://arxiv.org/abs/2601.18385) [V-full for the first two quotes; the last sentence via a search snippet of the same page, UNVERIFIED wording]
- **Kawano & Kawamura (2024):** a prior parameter-estimation method (Rodriguez et al.) would be "computationally expensive" on 4608×3456 IHC images, and "the message is degraded by the inverse transform". — [Kawano & Kawamura 2024](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741) [V-full]
- **Zhou, Zhu, Su, Wang & Sun, "Geometric correction code-based robust image watermarking" (IET Image Processing, 2021).** Embeds preset geometric correction codes (GCCs) with the watermark. At extraction, the image "can be geometrically corrected by minimising the difference between the extracted and the original GCCs", i.e. a decoder-side optimisation or search. It targets "arbitrary rotation, scaling and shifting with desirable hiding capacity". — [DOI](https://doi.org/10.1049/ipr2.12143) [V-abs; payload and BER UNVERIFIED because the Wiley full text was blocked]
- **Kang et al. ULPM (2010)** advertises "efficiency of blind resynchronization" in the Fourier/log-polar domain. — [DOI](https://doi.org/10.1109/tifs.2009.2039604) [V-abs]
- **Learned geometric-parameter estimation** (Xiang-Yang Wang / Hong-Ying Yang; Chunpeng Wang). An SVM/SVR or fuzzy LS-SVM is trained on moment features to predict rotation and scaling, then the image is corrected. — [Wang, Yang & Cui 2008](https://doi.org/10.1016/j.sigpro.2008.03.005); [Wang C. et al. 2017](https://doi.org/10.1016/j.sigpro.2016.12.010) [titles only; method description from titles and venue, details UNVERIFIED]
- **Resynchronization bits interlaced with payload bits.** Doërr, Rey & Dugelay (SETIT 2005) "interlac[e] resynchronization bits with the bits carrying the payload". These anchor points estimate local and global distortions via Elastic Graph Matching. — [EURECOM PDF](https://eurecom.fr/publication/1638/download/mm-doergw-050327.pdf) [V-full abstract]
- **Print-cam homography from a visible frame:** Hough lines plus four corners (Gourrame 2022). Fang 2019 needs the four image vertices to be known/recorded. — [Gourrame 2022](https://www.mdpi.com/2079-9292/11/2/266) [V-full]; [Chen 2020](https://www.mdpi.com/2076-3417/10/21/7494) [V-full]

### Inferences
- **Search over the block grid:** for the user, a cheap partial fix that keeps `dwtDctSvd` unmodified is an exhaustive search over translation phase. The 2D block-grid offset is bounded by the transform block size, so the search space is small. Combined with an affine estimate from a pilot or periodic signal, this is the "rectify then detect" route of Zheng et al. (2007).
- **False positives:** Barni's result implies the false-positive cost of searching grows with the number of hypotheses. With a 512-bit ECC payload, a CRC or ECC syndrome check can validate hypotheses (as NAWE does with CRC-16).
- **Crop and resize:** pure exhaustive search over rotation × scale × translation without a reference signal is expensive at 1024². Kawano's critique also applies: it breaks when the attacked image is not exactly the watermarked canvas (cropped and resized).
- **Implementation (inference only):** the registration and search pieces could be assembled from established-library primitives such as phase correlation, log-polar warps, the Radon transform and RANSAC, without modifying the watermark library. I did not verify specific library APIs in this research.

### Gaps
- No verified numbers for Zhou et al. 2021 GCC (payload, BER per angle).
- No verified runtime figures for exhaustive search at 1024².

---

## 5. Which methods carry hundreds of bits (256–1024) blindly while surviving rotation, cropping and translation? Is that out of reach for classical methods?

### Takeaway
In what I could verify, no classical blind scheme demonstrates ≥256 information bits with low BER under combined rotation + off-centre cropping + translation on ~1 Mpx images. The closest verified results are:
- **Kawamura group:** 200 information bits (LDPC to 300 coded) on 16-Mpx images. Median BER is 0 after cropping to 1920×1080 with ±30% scaling, but rotation is only handled in the 2026 pilot-grid work, at median BER < 0.1 with 300 uncoded bits.
- **Solanki et al. 2006:** "several hundred" bits with perfect recovery after print-scan, but this is a print-scan setting with small, estimable rotation, not arbitrary cropping or translation.
- **Periodic/symmetric self-reference:** excellent rotation, crop and translation robustness at 64 bits per 512² (Ma 2021), and up to 256 bits per 512² is claimed workable (NAWE 2026, no per-payload BER).

The 512-bit, 1024² operating point is therefore at the frontier for classical methods: not demonstrated, but not clearly out of reach.

### Cited Findings
Verified operating points (one row per scheme):

| Method (year) | Type | Payload | Image / PSNR | Geometric robustness (verified) | Source |
|---|---|---|---|---|---|
| Xin ZM/PZM thesis (2005); PR (2007) | multi-bit, moment QIM | 160 bits; 64+16 for StirMark | 256²; 42.5 / 46.4 dB | Rotation 3–45°: max BER ~10⁻³. Centred crop ≤50%: BER 0. Crop 75%, shear, RBA: fail. | [thesis](https://mspace.lib.umanitoba.ca/bitstreams/072619e9-e7c0-4104-878e-f9590ebd8163/download) |
| Zhang et al. ALMI (2011) | 1-bit | – | 256²; 40 dB | Rotation 45° and scale 0.8: detection 1. Crop 10%: detection 0. | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3378516/) |
| Kang ULPM (2010), Ma's re-implementation | multi-bit | 64, no ECC | 512²-class; 41.0 dB | Rotation 5°/30°: 7.6% / 9.3%. Crop 50%: 28%. Aspect ratio: ~50%. | [Ma 2021](https://arxiv.org/abs/2007.10240) |
| Voloshynovskiy ACF (2001), Ma's re-implementation | multi-bit, periodic | 64, no ECC | 40.7 dB | Rotation 5°: 1.2%. Crop 50%: 1.1%. Crop 75%: 15%. RBA 1.0: 14.6%. | [Ma 2021](https://arxiv.org/abs/2007.10240) |
| Tian LDFT (2013), Ma's re-implementation | multi-bit, local feature | 64, no ECC | 40.6 dB | Rotation 5°: 13.4%. Crop 50%: 8.5%. Scale 0.5: 38%. | [Ma 2021](https://arxiv.org/abs/2007.10240) |
| Ma et al. symmetry (2021) | multi-bit, self-reference | 64, no ECC | 108 images; 41.35 dB | Rotation 5–45°: ≤0.25%. Crop ≤50%: 0. Crop 75%: 8.7%. RBA: ≤1.05%. Scale 0.5–2: 0. | [Ma 2021](https://arxiv.org/abs/2007.10240) |
| Chen et al. screen-cam (2020) | multi-bit, feature region | 60 bits per region, repeated | **1024²**; 42–44 dB | Crop-off 20–50%: BER 0. Rotation 15/30/45/90°: BER 0. Scale 0.3: fail. | [MDPI](https://www.mdpi.com/2076-3417/10/21/7494) |
| Kawano & Kawamura (2024) | multi-bit, SIFT + DFT + grid pilot | 200 info bits; LDPC → 297, padded to 300, 2 × 150 | 4608×3456, cropped to 1920×1080 | Scale 0.7–1.3 + crop: median BER 0. BER > 0.1 outside 0.6–1.3. Smaller crops (HDTV, VGA): higher BER. | [repo PDF](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741) |
| Kawano & Kawamura (2026) | multi-bit, grid pilot + affine estimation | 300 bits, **no ECC** | 1080² crops of 16 MP; 37.25 dB | Rotation 0–90°: median BER < 0.1. Anisotropic scale 0.5–1.5: median < 0.1. | [arXiv](https://arxiv.org/abs/2601.18385) |
| Solanki et al. print-scan (2006) | multi-bit, DFT magnitude / phase QIM | "several hundred information bits" | – | "perfect recovery" after print-scan; also scaling, aspect ratio, row/column removal. Rotation estimated from printer halftoning. | [DOI](https://doi.org/10.1109/tifs.2006.885032) [V-abs] |
| NAWE (2026), hybrid; classical Wiener/BM3D variants exist | multi-bit, periodic carrier + Polar | 16–256 bits; reference 48 + CRC16 at rate 1/4 | 512²; 40 dB | Reference BER 0.07 over 34 attack arms. Translation and flip at floor. Rotation, shear, resize "low". | [arXiv](https://arxiv.org/abs/2609.25972) |

- **IHC ver.5 benchmark (Japan):** a message length of Nm = 200 bits must be decoded from attacked stego-images. The standard images are 4608×3456, and the attacked image is scaled 0.7–1.3 and cropped to FHD (1920×1080) at four positions (x ± 700, y ± 500). — [Kawano & Kawamura 2024](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741) [V-full]
- **Histogram-shape methods** (Xiang, Kim & Huang, IEEE TCSVT 2008; Zong et al., IEEE TCSVT 2015) target cropping and random bending through position-independent statistics.
  - **Xiang 2008:** "mathematically invariant to scaling … independent of the pixel position … statistically resistant to cropping … robust to interpolation errors".
  - **Payload:** small, since bits ride on gray-level bin relations; exact payload UNVERIFIED.
  - **Sources:** [Xiang 2008 DOI](https://doi.org/10.1109/tcsvt.2008.918843) [V-abs]; [Zong 2015 DOI](https://doi.org/10.1109/tcsvt.2014.2363743) [V-abs]

### Inferences
- **Density comparison** (pixels per bit, rough):
  - **User:** 512 coded bits / 1,048,576 px ≈ 2,048 px/bit at PSNR about 36.6 dB.
  - **Ma 2021:** about 4,096 px/bit at 41.35 dB (uncoded 64 bits).
  - **Chen 2020:** 60 bits per region of about 241–300 px side, i.e. about 1,000–1,500 px/bit per region, repeated over several regions.
  - **Kawano 2024:** 150 bits per region inside a 2-Mpx crop of a 16-Mpx image.
- **Feasibility:** the user's density is higher than the best verified periodic result, but the user has about 4–5 dB more embedding power. A periodic or self-referencing synchronization layer is therefore the most plausible classical route to fix rotation + crop + translation at 512 bits. It is unproven at this density.
- **Why ECC alone does not help:** ECC cannot fix the user's current 50% BER, because that is desynchronization, not noise. Kawano (2024) states this directly.
- **What a sync layer has to achieve:** it must bring raw BER down to the range the user's ECC can correct, typically ≤ 5–10% for common codes at moderate rate. Verified periodic-scheme raw BERs at 64 bits (≈0–1.2% for 5–45° rotation and ≤50% crop) are in that range. The ULPM and LDFT figures (8–38%) are not.
- **Cropping limits:** heavy cropping (75%, i.e. 128² remaining of 512²) leaves 8.7–15% BER even for periodic schemes at 64 bits. For 512 bits on 1024², a 75% crop leaves about 256² carrying 512 bits, which is likely beyond reach unless tiles are smaller than the remaining area and the full codeword fits in one tile.
- **Tile size:** if a tile must hold the whole 512-bit codeword and survive 50% cropping, it has to fit within the 512² that remains, i.e. ≤512 px period. That gives at most about 512 px²/bit, roughly 8× denser than Ma 2021.

### Gaps
- No verified BER for any classical scheme at ≥256 bits under rotation + off-centre crop + translation on ~1 Mpx.
- No verified payload for Kang 2010 (own experiments), Xiang 2008, Zong 2015, Fang 2019 or Zhou 2021.
- Solanki 2006: only the abstract was available. The exact bit count and the size of cropping/rotation it tolerates are unverified.

---

## 6. What do recent surveys and overview statements (2015–2026) say about the best classical geometric-robust schemes and open problems?

### Takeaway
Overview statements from 2005 to 2026 consistently say four things:
- Global RST is largely solved; Doërr 2005 calls it "almost … solved".
- Cropping, local/random bending, nonisotropic scaling and combined attacks remain open; Tian 2013 calls the area "still a grand challenge", and Wan 2022 says "cropping … still a difficult problem".
- Moment and normalization methods are weak to cropping and mostly 1-bit.
- Templates are removable, and feature methods are fragile and mostly 1-bit.

The strongest recent classical results are periodic or symmetric self-reference (Ma 2021), pilot grids (Kawamura 2024–2026) and repeated local-region embedding for camera capture (Fang 2019; Chen 2020).

### Cited Findings
- **Wan, Wang, Zhang, Li, Yu & Sun, "A comprehensive survey on robust image watermarking", Neurocomputing 488 (2022), 226–247.** Per Kawano & Kawamura (2026), its Section 7 states that "the problem of geometric attacks involving cropping is still a difficult problem". — [Kawano & Kawamura arXiv 2601.18385](https://arxiv.org/abs/2601.18385) [V-full secondary]; [Wan 2022 DOI](https://doi.org/10.1016/j.neucom.2022.02.083) [survey itself not opened]
- **Ma et al. (IEEE TCSVT 2021)** give a five-category taxonomy: image normalization, template, invariant domain (Fourier–Mellin/ULPM), feature-based, and periodic self-calibration. Their verdicts:
  - Normalization is "weak … under cropping … only one-bit capacity and high computational cost".
  - Templates are "vulnerable to template removal attack".
  - For invariant domains, "local geometric distortion is still a challenge".
  - Feature-based schemes are "[m]ost … one-bit" with "higher computational cost".
  - Only the last two categories "have the possibility [of] being robust to local geometric distortions".
  - Source: [Ma et al. 2021](https://arxiv.org/abs/2007.10240) [V-full]
- **Tian et al. (2013):** "Up to now, a watermarking scheme that is robust against desynchronization attacks (DAs) is still a grand challenge … few are resilient to challenging cropping and local DAs … robust features for watermark synchronization are only globally invariable rather than locally invariable." — [DOI](https://doi.org/10.1109/tcyb.2013.2245415) [V-abs]
- **Xiang, Kim & Huang (2008):** "few are resistant to challenging cropping and random bending attacks … those exploited robust features are more or less related to the pixel position." — [DOI](https://doi.org/10.1109/tcsvt.2008.918843) [V-abs]
- **Doërr, Rey & Dugelay (2005):** "If the weakness against global distortions can almost be considered as solved, local geometric distortions … remain" an open issue. — [EURECOM PDF](https://eurecom.fr/publication/1638/download/mm-doergw-050327.pdf) [V-full]
- **Zhou et al. (2021):** "existing watermarking schemes are still not robust enough to the common geometric transformation attacks such as arbitrary rotation, scaling and shifting with desirable hiding capacity." — [DOI](https://doi.org/10.1049/ipr2.12143) [V-abs]
- **Zhang et al. (2011):** cropping is "a common problem for the moment-based watermark algorithms." — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3378516/) [V-full]
- **Chen et al. (2020):** "frequency domain-based methods are global watermarks, they are also weak to cropping attacks". On feature methods: "For images with simple texture, the feature points are often unstable." — [MDPI](https://www.mdpi.com/2076-3417/10/21/7494) [V-full]
- **Kawano & Kawamura (2024):** "redundancy is not effective against geometric attacks. The type and strength of geometric attacks need to be estimated"; "the issue of overwriting the watermark is an open problem". — [repo PDF](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741) [V-full]
- **Gourrame et al. (2022):** "The study of robustness against geometric distortion is limited to rotation, scaling, and translation (RST) in a majority of the literature". Projective (perspective) distortion is under-studied. — [MDPI](https://www.mdpi.com/2079-9292/11/2/266) [V-full]
- **Zheng et al. (ACM CSUR 2007)** is the standard RST survey: rectify-then-detect versus invariant-domain. — [DOI](https://doi.org/10.1145/1242471.1242473) [V-abs]
- **Evsutin & Dzhanashia, "Watermarking schemes for digital images: Robustness overview", Signal Processing: Image Communication 100 (2022; online 2021)** exists but was not accessible. — [DOI](https://doi.org/10.1016/j.image.2021.116523) [not opened]

### Inferences
- **Open problems, in order of difficulty for classical methods:**
  1. Heavy or off-centre cropping combined with rotation at high payload.
  2. Local and random bending.
  3. Perspective or camera-capture distortion.
  4. Capacity: most geometric-robust schemes are 1-bit or carry tens of bits.
- **Where the frontier is:** classical progress since the early-2000s DWT/DCT schemes has mostly come from three directions:
  - (i) better invariant computation: accurate or fractional moments, ULPM without interpolation error;
  - (ii) local or self-referencing synchronization: LDFT, symmetry/ACF, SIFT regions with pilots;
  - (iii) explicit estimate-then-invert pipelines with ECC: Kawamura's IHC work, NAWE's Polar + CRC.

  Payload has grown only modestly: from ~64 bits per 512² to 200–300 bits on 16-Mpx images.
- **Bearing on the user:** the user's DWT-DCT-SVD baseline sits exactly in the class every overview calls "not geometric-robust". The literature consistently recommends adding a synchronization layer (periodic, pilot or template) rather than relying on ECC.

### Gaps
- I could not open Wan et al. 2022, Evsutin & Dzhanashia 2021/22, Tsougenis et al. 2012, or other 2015–2026 surveys in IEEE Access, MTAP or Information Sciences. Survey content above is limited to secondary quotes and to the taxonomies inside primary papers.
- No survey found that ranks classical geometric-robust schemes by payload at a fixed PSNR.
- Shijun Xiang's recent work, e.g. Hu & Xiang, "Cover-lossless robust image watermarking against geometric deformations", IEEE TIP 2021, was located only by title. — [DOI](https://doi.org/10.1109/tip.2020.3036727) [content UNVERIFIED]
- I did not research whether maintained open-source library implementations exist for any of these synchronization schemes. That matters for the user's "library implementations only" rule.
