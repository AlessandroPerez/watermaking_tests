# Embedding and decoding in classical blind multi-bit image watermarking since about 2005

Scope: non-ML, blind (no original image, no message at the decoder), multi-bit schemes, 2005–2026. How the sources were checked:
- Abstracts were read from the OpenAlex API record of each DOI (linked as doi.org).
- Full text was read for three papers: Zhu et al. 2014 (NCQM), Ma et al. 2010 (ASTDM) and Hirata et al. 2017 (IHC/LDPC).
- ScienceDirect, MDPI and HAL refused automated access (403 or a bot challenge). Numbers for those papers are marked **[UNVERIFIED]** where they come only from memory or search snippets.
- Context-specific facts about `imwatermark/dwtDctSvd.py` and the user's `wmecc/attacks.py` come from reading the local code. They are listed under Inferences.

---

## 1. Gain-invariant quantization (RDM, angle QIM, logarithmic QIM, perceptual STDM, normalized/adaptive QIM): how robust are they to amplitude scaling, contrast and gamma compared with plain QIM?

### Takeaway
Plain dither-modulation QIM breaks under any amplitude (valumetric) scaling. Since 2005 the field has made the quantizer gain-invariant in four ways:
- normalize by a gain-covariant local statistic: RDM (2005), Watson-slack QIM/STDM by Li and Cox (2005–2007);
- quantize an angle: AQIM (2005), DAQIM (2014/2015), dihedral-angle schemes (2013);
- quantize a normalized correlation: NCQM (2014);
- estimate the gain at the receiver: Kang–Huang–Zeng's adaptive receiver (2008), Shterev–Lagendijk scale estimation (2004–2006).

All of these are exactly invariant to a pure global gain. In practice, clipping and rounding still cause errors at large gains. Gamma is only partially handled. In the one head-to-head test found (Zhu et al. 2014, 1000 images), NCQM held BER ≤ 2.5% over a broad gain range and 4.9% at the worst gamma tested, and beat RDM, STDM and Zareian's ratio method.

### Cited Findings
- **RDM (Pérez-González, Mosquera, Barni, Abrardo, IEEE TSP 2005).**
  - Mechanism: dither modulation with a "gain-invariant adaptive quantization step-size at both embedder and decoder". The step is a function of past watermarked samples, so a global gain scales the step and the signal equally.
  - With more memory the scheme asymptotically approaches DM performance while staying gain-invariant.
  - It reaches "much higher rates for the same bit error probability" than improved spread spectrum. The paper also generalizes gain invariance to QIM in general. — [Pérez-González et al. 2005](https://doi.org/10.1109/tsp.2005.855407)
- **Logarithmic homogeneous RDM (ICASSP 2010).** Proposed a subclass of gain-invariant DM that is also insensitive to additive noise, and reports that it outperforms other gain-invariant schemes in simulation. — [ICASSP 2010](https://doi.org/10.1109/icassp.2010.5495452)
- **Li and Cox: Watson-based QIM (ICASSP 2005, MMSP 2005, IEEE TIFS 2007).**
  - Mechanism: replace the fixed QIM step with Watson-model perceptual "slack". The Watson model is modified so the slacks scale linearly with valumetric scaling, which makes QIM "theoretically invariant to valumetric scaling". The 2005 MMSP paper combines this with RDM.
  - Results on 1000 images: better fidelity and better robustness in high-noise regimes.
  - Caveat in the paper: "scaling can still result in errors due to cropping and roundoff that are an indirect effect of scaling". — [Li & Cox, TIFS 2007](https://doi.org/10.1109/tifs.2007.897266); [MMSP 2005 RDM+Watson](https://doi.org/10.1109/mmsp.2005.248616); [ICASSP 2005 version](https://doi.org/10.1109/icassp.2005.1415326)
- **Li and Cox: perceptual STDM (MMSP 2006).**
  - The earlier QIM/RDM perceptual schemes "remain extremely sensitive to re-quantization" (JPEG, rounding), which is why perceptual modelling was moved into STDM.
  - Tested on 1000 images at embedding rates of 1/32 and 1/320.
  - At rate 1/32, robustness equals STDM while Watson perceptual distance drops from 23 to about 4.
  - At rate 1/320, both robustness and fidelity improve. — [Li & Cox, MMSP 2006](https://doi.org/10.1109/mmsp.2006.285276)
  - Li's UCL thesis states that plain STDM "remains very sensitive to valumetric scaling" and that adding a perceptual model fixes this. — Q. Li, "Using Watson perceptual model to improve quantization index modulation based watermarking schemes", UCL doctoral thesis 2007 (abstract read via an OpenAlex search; no DOI or URL available)
- **ASTDM for colour (Ma, Yu, Wei, Tian, Lu, IEICE 2010), full text read.**
  - Embedding domain: the intensity channel of HSI. A modified Watson model makes luminance-masking thresholds scale with amplitude.
  - The global mean intensity C0,0 is itself embedded (with a 7+3-bit checksum, repeated 45 times) so the decoder can rebuild the same perceptual model. This is in effect embedded side information for gain consistency.
  - Payload and quality: a 60×60 = 3600-bit binary watermark, one bit per 8×8 DCT block on 20 zig-zag coefficients (2nd to 21st). At equal SSIM 0.982: Baboon 37.53 dB, Lena 41.60 dB. Mean quantization steps were 1186 for ASTDM vs 938 for STDM over 500 images.
  - Amplitude scaling was tested from 0.1 to 2.0. ASTDM beats STDM over the whole range and beats Li–Cox for factors > 1.0. Results are given as NC curves; the numbers were not extracted. — [Ma et al. 2010 PDF](https://www.jstage.jst.go.jp/article/transinf/E93.D/4/E93.D_4_843/_pdf)
- **Angle QIM (Ourique, Licks, Jordan, Pérez-González, ICASSP 2005).** Quantizes "the angle formed by the host-signal vector with the origin of a hyperspherical coordinate system", which makes it "provably insensitive to amplitude scaling". The companion paper derives exact BER under simultaneous amplitude scaling and AWGN for 2-D AQIM. — [AQIM](https://doi.org/10.1109/icassp.2005.1415525); [AQIM BER analysis](https://doi.org/10.1109/icassp.2005.1415526)
- **Difference AQIM (Cai, Zhu, Weng, Ling: ICCE-China 2014; Signal Processing: Image Communication 2015).** Quantizes the difference of two angles. Reported to outperform AQIM and gradient-direction watermarking (GDWM) in document-to-watermark ratio under gain attacks. — [DAQIM 2014](https://doi.org/10.1109/icce-china.2014.7029873); [DAQIM SPIC 2015](https://doi.org/10.1016/j.image.2015.03.010)
- **Dihedral-angle embedding with an ML detector (IET Image Processing 2013).**
  - Fits a plane to nine approximation coefficients per block and quantizes the dihedral angle to the x–y plane.
  - Claims "high robustness to gain attacks", plus robustness to JPEG, Gaussian and median filtering, noise and scaling. — [IET IP 2013](https://doi.org/10.1049/iet-ipr.2012.0693)
- **Logarithmic QIM (Kalantari and Ahadi, ICASSP 2009; IEEE TIP 2010).**
  - Mechanism: μ-law compand, then uniform quantization, then expand. Also a vector version on log-spaced hyperspheres.
  - The gain is perceptual: "stronger watermark… better performance" at equal visual quality. It is **not** gain-invariant by itself. — [LQIM TIP 2010](https://doi.org/10.1109/tip.2010.2042646); [ICASSP 2009](https://doi.org/10.1109/icassp.2009.4959863)
  - A later ICIP 2013 paper states that LQIM "is sensitive to valumetric scaling attack" and proposes logarithmic STDM with a perceptual model (LSTDM) to fix it. — [LSTDM ICIP 2013](https://doi.org/10.1109/icip.2013.6738931); follow-ups: [MTAP 2015](https://doi.org/10.1007/s11042-015-2853-5), [saliency-JND LSTDM, Electronics Letters 2015](https://doi.org/10.1049/el.2014.4329)
- **NCQM (Zhu, Ding, Dong, Hu, Zhang, IEEE TMM 2014), full text read.** Quantizes the normalized correlation between the host vector and a random vector. Setup: 3rd-level Haar DWT diagonal details, 1000 Corel images, 192-bit message, equal MSSIM across methods.
  - Valumetric scaling (gain 0.1–2): NCQM BER "does not exceed 2.5%" over the tested range. RDM and Zareian's method degrade at extreme gains because of "cropping and roundoff". STDM is "relatively sensitive".
  - Gamma correction: NCQM is the best of the four, with worst-case BER 4.9%. Zareian's magnitude-ratio method "performs substantially worse", because a ratio of vector magnitudes is "easily changed by the gamma correction".
  - Gray-level transforms: NCQM BER about 0 under log transform, 6.9% under contrast stretching and 14% under histogram equalization. RDM is close but slightly worse.
  - JPEG: NCQM BER < 12% for QF > 20, while STDM is slightly better (error < 3.9%). RDM is "very poor" at low QF.
  - Zareian's method had average BER > 10% even with no attack, while the other methods stayed under 0.2%.
  - Note: the gamma factors, gain values and image size could not be read from the PDF tables. — [Zhu et al. 2014 PDF](https://ieeexplore.ieee.org/ielx7/6046/6922170/06860239.pdf); [DOI](https://doi.org/10.1109/tmm.2014.2340695)
- **Adaptive receiver for QIM (Kang, Huang, Zeng, IEEE TMM 2008).**
  - Models the channel as "fading and nonzero mean additive noise".
  - A training sequence is embedded alongside the payload, and the decoder uses it to estimate the decision zones and the quantization step.
  - Reported gains: robustness to "image intensity DC change, histogram equalization, color reduction, image intensity linear scaling, … Gamma correction". — [Kang et al. 2008](https://doi.org/10.1109/tmm.2008.2001361)
- **Amplitude-scale estimation for QIM-DC (Shterev, Lagendijk, Heusdens).** SPIE 2004/2005 papers give Fourier-based and ML estimators of the attacker's scale. The full paper is IEEE TSP 54(11):4146–4155, 2006 (citation confirmed via a reference list; abstract not read). — [TU Delft record](https://research.tudelft.nl/en/publications/amplitude-scale-estimation-techniques-for-quantization-based-wate/); [Shterev thesis 2007](https://theses.eurasip.org/theses/117/quantization-based-watermarking-methods-for/download); [SPIE 2004](https://spiedigitallibrary.org/conference-proceedings-of-spie/5306/0000/Statistical-amplitude-scale-estimation-for-quantization-based-watermarking/10.1117/12.526432.full)
- **Content-aware QIM (IEEE TIFS 2023).** Reduces embedding distortion via canonical labelling. It is "(key-aided) semi-blind" and does not target gain invariance. — [CA-QIM 2023](https://doi.org/10.1109/tifs.2023.3342612)

### Inferences
- **Why the user's colour attacks behave like gain attacks.** In the user's harness, brightness, contrast and saturation are `PIL.ImageEnhance` with factor k = 1 ± p/100 (`wmecc/attacks.py`, lines 13 and 197–203). PIL implements these as blends:
  - Brightness = blend(black, img, k) = k·img.
  - Contrast = blend(uniform mean-grey, img, k).
  - Color (saturation) = blend(greyscale(img), img, k).

  OpenCV's U is 0.492·(B−Y) + 128, and every blend partner above is achromatic (U = 128). So all three operations map (U−128) to k·(U−128) exactly, apart from clipping and rounding: **a pure gain attack on the zero-mean chroma.**
- **What dwtDctSvd quantizes.** From `imwatermark/dwtDctSvd.py`, the decision is `s[0] % scale > scale/2`, with embedding at 0.25·scale or 0.75·scale. That leaves a margin of scale/4.
  - The 2-D orthonormal DCT is C·B·Cᵀ, so singular values are unchanged by it. The scheme is therefore plain QIM on the top singular value of each 4×4 Haar-LL block. That value is at least 4·mean(LL) ≈ 8·mean(U) over an 8×8-pixel area.
  - With the 128 offset, s[0] ≈ 8·(128 + m), where m is the local mean of U−128. A gain k shifts s[0] by about 8·(k−1)·m. With scale = 36, for example, a bit flips once |8·(k−1)·m| > 9: for k = 1.2 that is |m| > 5.6 grey levels of local chroma offset, which most coloured regions exceed.
  - Plain QIM on an amplitude feature has no protection here, and the literature above is exactly the remedy. Caveats: this is first-order (not every block is DC-dominated) and the 36 is the library default; the user's step is set per message length for wPSNR 40 dB, so it may differ.
- **The 128 offset matters for any gain-invariant fix.** A gain-invariant rule (RDM, NCQM or AQIM) applied to raw U, or to s[0] of raw U, would still not be invariant. It must operate on U−128, or on AC/zero-mean features.
- **Gamma is not a global gain.** It acts as an intensity-dependent local gain. Schemes whose normalization is local (RDM with short memory, NCQM on short vectors, angle-based schemes) handle it only approximately, consistent with NCQM's 4.9% worst-case BER.
- **Under the "watermark library unmodified" rule the embedding rule cannot change.** The literature-backed options that fit the constraint are receiver-side:
  - (a) Gain estimation and inversion before calling the unmodified decoder: rescale (U−128) by 1/k̂ (Shterev–Lagendijk; Kang et al.'s training sequence).
  - (b) An exhaustive search over a k grid (and over a gamma grid), keeping the candidate that makes the ECC decoder or CRC succeed.

  Embedding a different rule (RDM, NCQM, AQIM, perceptual STDM) would need a different established implementation. No maintained Python library implementing those rules was identified in this research (gap).

### Gaps
- Li and Cox 2007 TIFS: BER-versus-scale table values were not readable (paywalled).
- AQIM and DAQIM: no image-domain payload, PSNR or BER numbers could be read; only abstracts.
- Shterev and Lagendijk 2006 TSP: numerical results not read.
- Kang et al. 2008: no numbers available (abstract only).
- No paper found tests brightness, contrast or saturation as `ImageEnhance`-style chroma gains. NCQM's tests are on grey-level images.

---

## 2. Improved spread spectrum and host-interference rejection; side-informed coding (dirty-paper codes, trellis-coded watermarking): what capacity and robustness do they reach?

### Takeaway
- ISS (2003) removes host interference by projecting it out. Post-2005 follow-ups extend it to multi-bit and correlation-aware variants, but the gains are reported mostly as theoretical or simulated BER, not at image scale.
- The most important side-informed result for this problem is **dirty-paper trellis coding** (Miller, Doërr, Cox 2004). It carried 1380 bits in 240×368 images, robust to "changes in contrast" and JPEG, because its spherical codewords make it inherently invariant to valumetric scaling.
- Orthogonal/Gold dirty-paper codes with a correlation decoder (Abrardo and Barni 2005) are likewise gain-robust and were concatenated with turbo codes using soft inner decoding.
- The costs are embedding complexity (iterative informed embedding) and security weaknesses.

### Cited Findings
- **Dirty-paper trellis codes (Miller, Doërr, Cox, IEEE TIP 2004).**
  - Informed coding (a modified trellis where each message has many codewords) plus iterative informed embedding plus perceptual shaping.
  - Payload: "1380 bits of information in images with dimensions 240 × 368 pixels".
  - Tested on 2000 images: "robust to significant valumetric distortions, including additive noise, low-pass filtering, changes in contrast, and lossy compression". Each of the three components "improves performance substantially". — [Miller et al. 2004](https://doi.org/10.1109/tip.2003.821551)
- **Fast DPTC embedding (ICIP 2005).**
  - DPTC "have the advantage of being invariant to valuemetric scaling of the cover work", but the original informed embedding is computationally expensive.
  - A cone/normalized-correlation approximation gave "a 600-fold computational improvement" with better embedding quality on 2000 images. — [ICIP 2005](https://doi.org/10.1109/icip.2005.1529846)
- **DPTC security and speed (SPIE 2009).** DPTC "has two strong drawbacks: its security weakness and its CPU computation complexity". The paper proposes a wavelet-projection embedding space and a dichotomous-rotation embedding. — [SPIE 2009](https://doi.org/10.1117/12.839853)
- **UCL thesis (2007) on DPTC design.** DPTC are "a form of spherical code… robust to amplitude scaling". Trellis-coded modulation improves the spread of codewords on the sphere, and choosing codewords by a cost that mixes correlation and perceptual distance "can significantly improve performance". — "Investigations on dirty paper trellis codes for watermarking", UCL doctoral thesis 2007 (abstract read via an OpenAlex search; no DOI or URL available, so treat as a secondary pointer)
- **Orthogonal/quasi-orthogonal dirty-paper coding (Abrardo and Barni, IEEE TSP 2005).**
  - Equi-energetic orthogonal codewords plus a correlation decoder, giving robustness "against the gain attack".
  - Embedding is optimal: minimum distortion for a given pairwise error probability under AWGN.
  - Improved further with Gold sequences and an outer turbo code, with the inner decoder "modified to produce a soft estimate". — [Abrardo & Barni 2005](https://doi.org/10.1109/tsp.2004.839909)
- **Multibit ISS (WIFS 2011; InTech 2012 chapter).** Extends Malvar–Florêncio one-bit ISS to code-division multibit, optimizing sequence energies to reduce cross-correlation and host interference. — [MISS 2011](https://doi.org/10.1109/wifs.2011.6123146); [chapter 2012](https://doi.org/10.5772/36966)
- **CASS/CAISS (Valizadeh and Wang, IEEE TIFS 2011).** Correlation-and-bit-aware additive SS and ISS that "significantly reduce the host effect" and improve BER while keeping the simple correlation decoder. — [TIFS 2011](https://doi.org/10.1109/tifs.2010.2103061)
- **Multiplicative variant (WIFS 2013).** — [CMSS 2013](https://doi.org/10.1109/wifs.2013.6707816)
- **RDM versus ISS.** RDM "can achieve much higher rates for the same bit error probability" than ISS. — [Pérez-González et al. 2005](https://doi.org/10.1109/tsp.2005.855407)

### Inferences
- **Inherent gain invariance.** Spherical/trellis dirty-paper codes and orthogonal DPC with normalized-correlation decoding are gain-invariant by construction. Miller et al. explicitly report robustness to contrast change at roughly 0.0156 bits/pixel.
- **Scaling DPTC to the user's frame size (back-of-envelope only).** Scaling linearly to 1024×1024 gives roughly 16 kbit of raw capacity, an order of magnitude above 512 bits. So a DPTC-style scheme at 512 bits would have a large margin, but at a high computational cost.
- **ISS-type schemes** reject host interference, but a global gain still scales the correlation statistic. Their sign decisions are gain-invariant for binary antipodal signalling, while their soft values are not.

### Gaps
- Miller et al. 2004: per-attack BER and message error rate tables and PSNR were not readable.
- No post-2015 image-scale DPTC results with modern attack suites were found.
- ISS image-domain payload and PSNR numbers were not found.

---

## 3. Statistical-model blind decoders in DWT, DCT, contourlet, shearlet and NSCT domains: what gains over correlation or hard-threshold decoding are reported?

### Takeaway
A large body of work (about 2008–2020, mainly Concordia's Ahmad/Swamy group and Iranian groups such as Akhaee/Sahraeian/Marvasti) replaces correlation detectors with ML or locally-optimum detectors built on heavy-tailed coefficient models:
- generalized Gaussian, Cauchy, alpha-stable, normal inverse Gaussian (NIG), Bessel K-form, Gauss–Hermite;
- vector HMMs and Weibull-mixture HMTs; GARCH.

Most of these papers are **one-bit detection** (ROC) studies. The multi-bit **decoders** are Akhaee 2009/2010, Sadreazami 2016 (NIG), Amini 2016/2018 (vector HMM) and the 2020 Weibull HMT. All report lower BER than GG or Cauchy decoders, but abstracts give no portable numbers. Kwitt, Meerwald and Uhl showed that approximate or fixed parameters lose little detection performance. These decoders are mainly an AWGN and JPEG gain; none targets gain or colour attacks specifically.

### Cited Findings
- **Multi-bit ML decoders**
  - Akhaee, Sahraeian, Sankur, Marvasti (IEEE TMM 2009): scaling-based (multiplicative) embedding in low-frequency wavelet coefficients, HVS-optimized strength, ML decoder "aided by the channel side information"; performance derived analytically. — [TMM 2009](https://doi.org/10.1109/tmm.2009.2012922)
  - Akhaee, Sahraeian, Marvasti (IEEE TIP 2010): multiplicative embedding in the highest-energy contourlet directional subband with a GGD model and an ML optimal detector; a blind extension uses the patchwork idea. Robust to AWGN, JPEG and rotation compared with prior techniques. — [TIP 2010](https://doi.org/10.1109/tip.2009.2038774)
  - Sadreazami, Ahmad, Swamy (IEEE TMM 2016): NIG prior for contourlet coefficients, closed-form ML bit extraction in clean and noisy settings. "Lower bit error rate" than other decoders; robust to noise, rotation, cropping, filtering and compression. — [TMM 2016](https://doi.org/10.1109/tmm.2015.2508147)
  - Amini, Ahmad, Swamy (IEEE TCSVT 2018, online 2016): blind multibit multiplicative decoder using a vector-based HMM, which captures inter-scale and cross-orientation dependencies. Closed-form BER validated by Monte Carlo; outperforms Cauchy- and GG-based decoders with and without attacks. — [TCSVT](https://doi.org/10.1109/tcsvt.2016.2607299)
  - Weibull-mixture vector HMT on undecimated DTCWT magnitudes (IEEE Access 2020): ML multiplicative decoder; better imperceptibility and robustness than the state of the art. — [Access 2020](https://doi.org/10.1109/access.2020.2978119)
- **One-bit detectors**
  - Rahman, Ahmad, Swamy (IEEE TIP 2009): Gauss–Hermite-expansion PDF detector for additive DWT watermarking. Better than Gaussian and GG detectors in Pd/Pfa, and more robust under compression, AWGN, filtering and geometric attacks. — [TIP 2009](https://doi.org/10.1109/tip.2009.2021313)
  - Kwitt, Meerwald, Uhl (ACM MM&Sec 2008; IEEE TIP 2011): Rao–Cauchy detector "competitive with the Generalized Gaussian detector, yet… more efficient". With "approximate host signal parameter estimates or even fixed parameter settings" there is "a remarkable improvement in runtime… without sacrificing detection performance". — [TIP 2011](https://doi.org/10.1109/tip.2010.2064327); [Rao-Cauchy 2008](https://doi.org/10.1145/1411328.1411337)
  - Sadreazami, Ahmad, Swamy (IEEE TIP 2014): alpha-stable fits contourlet coefficients better than GG or Laplacian. A bivariate Cauchy (α = 1) detector is close to the best-fit alpha-stable detector and "much superior" to the GG detector. — [TIP 2014](https://doi.org/10.1109/tip.2014.2339633)
  - Bian and Liang (IEEE TIP 2013): locally optimum Bessel K-form detector, strongest advantage "when the watermark is weak". — [TIP 2013](https://doi.org/10.1109/tip.2013.2246177)
  - Locally optimum detector with vector HMM (Signal Processing 2017). — [SP 2017](https://doi.org/10.1016/j.sigpro.2017.01.019)
  - Ahmaderaghi et al. (IEEE TCI 2018): shearlet domain, Laplacian model, Neyman–Pearson threshold, 30 grayscale images; more sensitive to directional features than DWT or contourlets. — [TCI 2018](https://doi.org/10.1109/tci.2018.2794065)
  - 2-D GARCH contourlet detector (IET CV 2018). — [IET CV 2018](https://doi.org/10.1049/iet-cvi.2018.5254)
  - Weibull–Power-Cauchy model in NSST plus polar harmonic Fourier moments (Symmetry 2026): AUROC 0.9991 with no attack. — [Symmetry 2026](https://doi.org/10.3390/sym18071200)

### Inferences
- **Fit to the user's case.** These decoders target multiplicative or additive SS-type embedding and model-mismatch noise. They are not a drop-in replacement for a QIM decoder like dwtDctSvd's.
- **Possible gain-robustness benefit (unverified).** Multiplicative embedding with re-estimated distribution parameters at the decoder could absorb a global gain, since the scale parameter is re-estimated from the attacked image. No paper found demonstrates this under brightness, contrast or saturation changes.
- **The transferable idea is soft decoding.** Computing per-bit likelihoods instead of hard thresholds feeds a soft ECC decoder. That applies directly to the user's ECC experiments.

### Gaps
- No numeric BER improvements (dB gains, or BER at fixed WNR or JPEG QF) were readable from any of these paywalled IEEE papers.
- Payload sizes for the multi-bit decoders were not verified. The Akhaee/Sadreazami/Amini lines typically use a few hundred bits or fewer in 512×512 grayscale images **[UNVERIFIED]**.

---

## 4. Matrix-decomposition schemes (SVD, QR, Schur, Hessenberg, LU) and transforms (contourlet, NSCT, shearlet, curvelet, DTCWT, RDWT, quaternion DFT/DCT): which are genuine advances, which are incremental or flawed, including SVD false positives?

### Takeaway
- The main documented flaw is the **SVD false-positive problem (FPP)**. Schemes that embed the watermark's singular values and keep the watermark's U and V matrices as a "key" (side information) let the extractor output whatever reference watermark is supplied. Zhang and Li (2005) showed the false-positive probability is 1 for Liu and Tan's scheme. Similar breaks followed for later RDWT–SVD and hybrid DWT–SVD schemes (Ling, Phan, Heng 2013; ambiguity attacks 2017; Makbol, Khoo, Rassem 2018 review).
- Schemes that **quantize host singular values or matrix elements blindly** (like dwtDctSvd, Su's QR and Schur schemes, Zhang 2017 spatial-SVD) avoid the FPP. However, the largest singular value is an amplitude feature, so they inherit QIM's gain sensitivity.
- Most QR, Schur, Hessenberg and LU variants and multi-transform cascades are incremental: they choose a different block element to quantize.

### Cited Findings
- **The original FPP result (Zhang and Li, IEEE TMM 2005).** Liu and Tan's SVD scheme "is fundamentally flawed in that the extracted watermark is not the embedded watermark but determined by the reference watermark"; the SVD matrices from the reference watermark bias "the false positive detection rate such that it has a probability of one". — [Zhang & Li 2005](https://doi.org/10.1109/tmm.2005.843357)
- **Rykaczewski (IEEE TMM 2007).** Liu and Tan's algorithm "can be easily discredited and ipso facto cannot be used for protecting rightful ownership". — [Rykaczewski 2007](https://doi.org/10.1109/tmm.2006.886297)
- **Ling, Phan, Heng (AEÜ 67(10):894–897, 2013).** Makbol and Khoo's RDWT–SVD blind scheme "has a fundamental flaw" against false-positive attacks: an adversary can extract a watermark that was never embedded. It "should not be used for proof of ownership". — [MMU repository record](https://shdl.mmu.edu.my/5255/)
- **Ambiguity attacks (JESIT 2017).** Two ambiguity attacks on Makbol and Khoo's RDWT–SVD scheme show it fails for owner identification, proof of ownership and transaction tracking. — [JESIT 2017](https://doi.org/10.1016/j.jesit.2016.12.011)
- **FPP survey (Makbol, Khoo, Rassem, MTAP 2018).** — [MTAP 2018](https://doi.org/10.1007/s11042-018-5891-y)
- **Hybrid-SVD review (IEEE Access 2021).** "many existing hybrid SVD-based image watermarking schemes found be insecure" (sic). — [Access 2021](https://doi.org/10.1109/access.2021.3060861)
- **FPP-free designs.**
  - Guo and Prasetyo (JVCIR 2014), "False-positive-free SVD-based image watermarking" (abstract not available). — [JVCIR 2014](https://doi.org/10.1016/j.jvcir.2014.03.012)
  - Zhang, Wang, Zhou (Future Internet 2017): embedding a binary watermark "into the largest singular value of each image block in the spatial domain… avoids the false positive problem" at lower complexity. — [Future Internet 2017](https://doi.org/10.3390/fi9030045)
- **Singular-vector embedding (Algorithms 2009).** Modifies angles of the right singular vectors per block while preserving orthogonality. — [Algorithms 2009](https://doi.org/10.3390/a2010046)
- **Schur, QR and Hessenberg-type blind colour schemes (Su et al. and successors).**
  - Su et al. Schur (Optics Communications 2012, online 2011). — [Schur 2011/2012](https://doi.org/10.1016/j.optcom.2011.12.065)
  - Su, Niu, Wang, Jia, Yue, QR (Signal Processing 94:219–235, 2014). — [QR 2014](https://doi.org/10.1016/j.sigpro.2013.06.025)
  - Double colour QR (MTAP 2013), on 4×4 blocks of a 512×512 24-bit host. — [MTAP 2013](https://doi.org/10.1007/s11042-013-1653-z)
  - Structure-preserving quaternion QR (Signal Processing 2021). — [SP 2021](https://doi.org/10.1016/j.sigpro.2021.108088)
  - Fixes to Schur: a 2018 paper adds "restitution, data jittering, and level-shifting" to "remedy the deficiency" of Su's Schur scheme. A 2019 Access paper finds nil orthonormal vectors from zero eigenvalues, and reports that distortion compensation gives +2.47 dB PSNR at the same payload. — [TSP 2018](https://doi.org/10.1109/tsp.2018.8441282); [Access 2019](https://doi.org/10.1109/access.2019.2932077)
- **Transform-domain statistical schemes** (contourlet, NSCT, shearlet, UDTCWT): see Section 3. Quaternion DFT/DCT: see Section 5.

### Inferences
- **Genuine advances:**
  - the FPP analysis itself, which became the field's main security check for SVD schemes;
  - blind quantization of host features (no stored U and V);
  - gain-invariant feature design (Section 1);
  - informed coding and embedding (Section 2);
  - statistical decoders (Section 3).
- **Incremental work:** most QR, Schur, LU and Hessenberg variants and DWT+DCT+SVD(+X) cascades. The 2018–2019 Schur "remedy" papers show the base designs had numerical defects.
- **dwtDctSvd's SVD layer.** It quantizes only the host's own largest singular value, so it is free of the FPP. Because the DCT preserves singular values, the "Dct" stage adds nothing to s[0]; the scheme behaves like Zhang 2017's largest-singular-value QIM, applied on Haar-LL of U. Its weakness is amplitude sensitivity, not security.

### Gaps
- Payload, PSNR and attack numbers for Su et al. QR 2014, Schur 2012 and quaternion QR 2021 could not be read (ScienceDirect 403). See Section 6 for unverified figures.
- No 2005+ LU- or Hessenberg-specific papers were opened.

---

## 5. Colour watermarking (quaternion domain, colour-space choice): which channel or transform is most robust to brightness, contrast, saturation and gamma? Does luminance versus chroma matter?

### Takeaway
- Quaternion and vector-colour transforms (Tsui et al. 2008 QFT/SCDFT; Chen et al. 2014 full 4-D QDFT; QDFT plus tensor decomposition 2021; QuatJND 2022) embed across all three channels jointly. The main reported benefits are fidelity and robustness to channel-exchange and common attacks. None found reports systematic robustness to brightness, contrast, saturation or gamma.
- The literature with explicit amplitude-scaling tests on colour images embeds in **intensity or luminance** with gain-adaptive steps (ASTDM 2010, HSI intensity, gains 0.1–2.0).
- For the user's PIL attacks, the dominant issue is not luminance versus chroma per se. It is that the embedding feature is an absolute amplitude.

### Cited Findings
- **Tsui, Zhang, Androutsos (IEEE TIFS 2008).**
  - Two vector schemes: spatio-chromatic DFT on CIE a*b* chromaticity (yellow/blue watermarks in the chromatic frequency domain), and quaternion Fourier transform on L*a*b* with JND-based casting.
  - Robustness comes from the positive-frequency coefficient, which spreads the mark to all colour components. Reported to beat AC- and DCT-based colour schemes. — [Tsui et al. 2008](https://doi.org/10.1109/tifs.2007.916275)
- **Chen, Coatrieux, Chen, Sun, Coatrieux (Digital Signal Processing 2014).** Full 4-D quaternion DFT watermarking for colour images. Abstract and full text could not be read (HAL bot challenge, ScienceDirect 403). — [DSP 2014](https://doi.org/10.1016/j.dsp.2014.02.010); [HAL](https://inserm.hal.science/inserm-01016680)
- **QDFT plus Tucker tensor decomposition (Applied Sciences 2021).** Odd–even quantization of the core tensor built from the three imaginary QDFT components "spreads the watermark into the three channels" and "can effectively resist each color channel exchange attack". Pseudo-Zernike moments plus an MLS-SVR handle geometric correction. — [Appl. Sci. 2021](https://doi.org/10.3390/app11115006)
- **QuatJND (Entropy 2022).** A quaternion JND model with colourfulness and contrast masking sets the quantization step per quaternion-DCT block; better robustness at better visual quality. — [Entropy 2022](https://doi.org/10.3390/e24081051)
- **ASTDM on HSI intensity (2010).** Gain-consistent perceptual steps on intensity; amplitude scaling tested from 0.1 to 2.0. A colour-artifact suppression step bounds intensity changes using the saturation–intensity relation, because changing intensity at high saturation causes visible colour distortion. — [Ma et al. 2010](https://www.jstage.jst.go.jp/article/transinf/E93.D/4/E93.D_4_843/_pdf)
- **Quaternion QR blind colour (2021, 2024).** — [SP 2021](https://doi.org/10.1016/j.sigpro.2021.108088); [ICIPAI 2024](https://doi.org/10.1117/12.3035318)
- **Kang et al. 2008 adaptive receiver** lists "color reduction" and "Gamma correction" among the attacks it improves. — [Kang et al. 2008](https://doi.org/10.1109/tmm.2008.2001361)

### Inferences
The following analysis of the user's setup is based on the PIL blend formulas, OpenCV YUV, and local reading of `dwtDctSvd.py` and `attacks.py`.

- **Effect of each attack on Y and on U** (Y is luminance; m is the local mean of U−128):

  | Attack (PIL, factor k) | Effect on Y | Effect on U−128 |
  |---|---|---|
  | Saturation (`ImageEnhance.Color`) | Unchanged, apart from rounding | × k |
  | Brightness | × k | × k |
  | Contrast | k·Y + (1−k)·mean: gain plus a constant offset | × k |
  | Gamma | Non-linear | Non-linear |

  Notes on the table:
  - Saturation leaves Y unchanged because PIL's L conversion uses the same 299/587/114 weights as OpenCV's Y.
  - Contrast's constant offset affects only DC/mean features, not AC coefficients.
- **What this predicts:**
  - Moving the unmodified dwtDctSvd mark to the **Y channel** (the library's `scales=[s,0,0]` option) should largely eliminate **saturation** failures.
  - It would **not** fix brightness or contrast. s[0] of a 4×4 LL block is DC-dominated, roughly 8·mean(Y), so brightness gains and contrast offsets shift it directly.
  - Y also carries different perceptual and JPEG trade-offs: Y is not chroma-subsampled, but wPSNR budgets differ by channel. This needs testing; it is a prediction, not a verified result.
- **The literature-backed fix for all four colour attacks** is a gain-invariant rule applied to a **zero-mean feature**, so that the 128 chroma offset and contrast's DC offset drop out:
  - RDM, NCQM or AQIM on Y-AC coefficients or on (U−128);
  - or receiver-side gain estimation (Section 1).

  Of the gain-invariant rules, NCQM had the best measured gamma behaviour (worst-case BER 4.9%) together with ≤ 2.5% BER under gain.
- **Within the "library unmodified" rule, the most practical literature-aligned remedy is decoder-side:**
  1. Estimate or search the chroma gain k: a grid over about 0.6–1.5 plus gamma candidates.
  2. Rescale U−128 by 1/k (or undo the candidate gamma), re-encode to BGR, and call the unmodified decoder.
  3. Accept the candidate whose ECC decode or CRC passes.

  Cost: about one decode per candidate (a dozen or two for a k grid; more if a gamma grid is added). This is the exhaustive-search analogue of Shterev–Lagendijk scale estimation. Combined with embedding in Y (see the table above), it covers brightness, contrast, saturation and most of gamma. Brightness clipping in saturated regions is not invertible.
- **Quaternion schemes** process R, G and B jointly. Unless the quantized feature is normalized (e.g. an angle or ratio), they remain amplitude-sensitive, and no evidence was found that they help with brightness, contrast or gamma.

### Gaps
- No study was found that compares Y versus U/V (or L*a*b*, HSI) embedding robustness under brightness, contrast, saturation and gamma with a fixed PSNR budget.
- Chen et al. 2014 (QDFT) results were not readable.
- No colour paper reporting saturation-change BER was found.

---

## 6. Highest reported blind payloads (e.g. 256–4096 bits in 512×512 or larger at PSNR about 36–42 dB with JPEG robustness): which papers, and are the numbers credible?

### Takeaway
**Verified figures:**

| Scheme | Payload | Host | Quality | Robustness evidence |
|---|---|---|---|---|
| Miller, Doërr, Cox 2004 (DPTC) | 1380 bits | 240×368 | — | 2000 images; contrast, JPEG |
| Ma et al. 2010 (ASTDM) | 3600 bits | Corel colour | 37.5–41.6 dB at SSIM 0.982 | 500 images |
| Zhu et al. 2014 (NCQM) | 128 bits | — | 48 dB | ~700-bit capacity at BER < 2% (low noise) |
| Hirata et al. 2017 (IHC) | 200 bits | 4608×3456 | 41.1 dB | BER 0 after IHC v4 JPEG, crop, scale, rotate |
| 2024 polar-code scheme | 650–1600 bits | 1920×1080 | 39.66 dB | 0.01 error probability after social networks |

The 2024 scheme uses neural-network extraction, so it is not purely classical.

The often-quoted 4096-bit (64×64 logo) and 24,576-bit (32×32×24 colour logo) blind schemes on 512×512 hosts (Parah 2016, Hsu and Hu 2015, Su et al. QR/Schur) could not be verified from source here. Their evaluation conventions make the numbers weakly comparable to a 512-bit exact-message requirement.

### Cited Findings
- **Miller, Doërr, Cox (2004).** 1380 bits in 240×368 images; 2000-image test; robust to noise, low-pass filtering, contrast changes and lossy compression. — [TIP 2004](https://doi.org/10.1109/tip.2003.821551)
- **Ma et al. (2010).**
  - Payload: 3600 bits (60×60 binary), one bit per 8×8 block on 20 AC coefficients.
  - PSNR 37.53 dB (Baboon) and 41.60 dB (Lena) at SSIM 0.982; 500 Corel images.
  - Robustness shown as NC under scaling 0.1–2.0, JPEG QF 40–100, AWGN and salt-and-pepper. — [Ma et al. 2010](https://www.jstage.jst.go.jp/article/transinf/E93.D/4/E93.D_4_843/_pdf)
- **NCQM (2014).**
  - Payload and quality: 128 bits (vector length 32 on 3rd-level DWT diagonal details) at PSNR 48 dB and wPSNR > 49 dB. Robustness tests used 192 bits.
  - Capacity at BER < 2%: about 700 bits at low noise, with RDM higher at low noise; NCQM exceeds RDM beyond noise σ = 5 and keeps about 100 bits at high noise. — [Zhu et al. 2014](https://ieeexplore.ieee.org/ielx7/6046/6922170/06860239.pdf)
- **IHC ver. 4 standard and Hirata et al. (IEICE 2017).**
  - The standard: 200-bit messages, 4608×3456 images, first JPEG compression to a file size of 1/25 or less, plus cropping, scaling and rotation. Pass criteria: worst BER ≤ 2%, average BER < 1%, PSNR > 30 dB.
  - Hirata et al. achieved BER 0 at an average PSNR of 41.136 dB, using a (800,200) PEG-LDPC code with weighted majority voting in 8×8 DCT blocks.
  - Ogawa et al. (convolutional code, 256×256 DCT blocks) also exceeded 40 dB, but needed more than 20 minutes for synchronization. — [Hirata et al. PDF](https://www.jstage.jst.go.jp/article/transinf/E100.D/1/E100.D_2016MUP0003/_pdf); [DOI](https://doi.org/10.1587/transinf.2016mup0003)
- **Polar codes for social-network images (IEEE Access 2024).** Template-based embedding with neural-network extraction plus polar codes; 650–1600 bits in 1920×1080 at PSNR 39.66; error probability 0.01 after Facebook, VK, Telegram, WhatsApp and others. — [Access 2024](https://doi.org/10.1109/access.2024.3446489)
- **Turbo-coded double watermarking (Chemak et al., Journal of Testing and Evaluation 2008).** Claims 2000 bits in 256×256 medical images; 30-image test. — [JTE 2008](https://doi.org/10.1520/jte101051)
- **Inter-block DCT methods (dates and venues confirmed; payload and PSNR not readable).**
  - Hsu and Hu, JVCIR 32:130–143, 2015 — [DOI](https://doi.org/10.1016/j.jvcir.2015.07.017); [dblp](https://dblp.dagstuhl.de/pid/38/2350.html)
  - Parah et al., DSP 2016 — [DOI](https://doi.org/10.1016/j.dsp.2016.02.005)
  - Inter-block correlation, AEÜ 2013 and Information Sciences 2019 — [AEÜ 2013](https://doi.org/10.1016/j.aeue.2013.08.018); [Inf. Sci. 2019](https://doi.org/10.1016/j.ins.2019.11.005)
  - Hu and Hsu, collective DWT-DCT, MTAP 2017 — [MTAP](https://doi.org/10.1007/s11042-016-3332-3)
- **[UNVERIFIED, from memory and snippets, not opened]:**
  - Su et al. QR (2014) and Schur (2012) embed a 32×32 24-bit colour watermark (24,576 bits) into a 512×512 colour host using 4×4 blocks, at roughly 36–40 dB PSNR. One snippet confirms 512×512 hosts and 4×4 QR blocks for the MTAP 2013 double-colour paper, and a USPTO patent uses 32×32 24-bit colour watermarks when comparing against Su's QR method. — [search context: Springer MTAP 2013](https://link.springer.com/doi/10.1007/s11042-013-1653-z); [USPTO patent](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10037587)
  - Parah 2016 and Hsu and Hu 2015 are commonly cited as 64×64 = 4096-bit binary logos in 512×512 grayscale at about 40–42 dB. Not verified.

### Inferences
- **The very high payload claims (4096–24,576 bits in 512×512) need caution.** Typical features:
  - they measure success as NC of a logo image (an NC around 0.8–0.9 can coexist with BER of several to 10%+);
  - they use around 10 standard test images;
  - they quote PSNR rather than wPSNR;
  - they rarely test gain, gamma or saturation.

  Su-style schemes quantize absolute matrix elements, the same amplitude-feature class as dwtDctSvd, so they would have the same gain weakness.
- **Credible references for "robust at the user's scale"** are DPTC (about 0.0156 bit/pixel, contrast-robust) and the IHC-standard schemes (200 bits in 16 MP with BER 0 after strong JPEG and geometric attacks, at about 41 dB with LDPC).
- **Scaling to the user's frame.** 512 coded bits in 1024×1024 (about 0.0005 bit/pixel) is far below DPTC's density. The binding constraint is gain sensitivity, not capacity.

### Gaps
- Exact payload, PSNR and BER values for Su (QR/Schur), Parah, Hsu–Hu and Chen QDFT could not be verified (ScienceDirect and MDPI returned 403).
- No independent replication study of high-payload claims was found.

---

## 7. How have error-correcting codes (BCH, RS, LDPC, turbo, polar) and soft decoding been combined with classical watermarking, and what gains are reported?

### Takeaway
Reported coding gains are substantial whenever the code is matched to the watermark channel's error rate and soft information is used:
- LDPC roughly **doubled payload** versus BCH or repetition at equal BER (Bastug and Sankur 2004).
- A turbo-decoded BCH product code moved the first message error from JPEG Q≈50 to Q≈25 for a 121-bit payload at about 38 dB (Rey et al. 2003).
- A (800,200) PEG-LDPC corrected channel error rates up to 15% with no failures, versus 14% failure for a concatenated BCH+LDPC code (Hirata et al. 2017).
- Abrardo and Barni (2005) concatenated dirty-paper codes with turbo codes using **soft inner decoding**.

None of these gains fixes a systematic gain or colour attack. Coding helps when errors are random-like, not when most blocks flip together.

### Cited Findings
- **Bastug and Sankur (IEEE SPL 2004).** For transform-domain SS watermarking, "the information payload can be doubled via judicious use of LDPC codes" relative to BCH and repetition codes. — [SPL 2004](https://doi.org/10.1109/lsp.2003.819350)
- **Rey, Amis, Dugelay, Pyndiah, Picart (SPIE 2003).** BCH product code (Chase–Pyndiah turbo decoding) concatenated with repetition, distortion about 38 dB. For 121 bits the "first error appears at a JPEG quality factor of about 25%… instead of about 50% when using only repetition codes". — [SPIE 2003](https://doi.org/10.1117/12.477323); [HAL](https://hal.science/hal-02129093)
- **Abrardo and Barni (IEEE TSP 2005).** Gold-sequence dirty-paper codes plus an outer turbo code, with the inner decoder modified "to produce a soft estimate of the embedded message". — [TSP 2005](https://doi.org/10.1109/tsp.2004.839909)
- **Hirata, Nozaki, Kawamura (IEICE 2017).**
  - Code: (3,4)-regular (800,200) PEG-LDPC (rate 1/4) with sum-product decoding.
  - Result: "no decoding errors if the channel error rate is less than or equal to 15%" (100 trials). The previous concatenated (255,200,6) BCH plus random (1012,255) LDPC failed at 14% because of short Tanner cycles.
  - The shorter codeword let them raise PSNR to 41.1 dB at BER 0 under IHC v4. Weighted majority voting over repeated embeddings feeds the decoder. — [Hirata et al.](https://www.jstage.jst.go.jp/article/transinf/E100.D/1/E100.D_2016MUP0003/_pdf)
- **Martinez Noriega thesis (audio).** QIM plus LDPC, with LLRs computed from MP3-noise statistics and repetition+LDPC concatenation: 229.7 bit/s robust to MP3 at 64 kbps. It argues that "almost no previous study exploits" ECC properly. — [UEC repository](https://uec.repo.nii.ac.jp/records/1043)
- **Polar codes (IEEE Access 2024).** 650–1600 bits at error probability 0.01 through real social-network channels (template embedding, neural-network extraction). — [Access 2024](https://doi.org/10.1109/access.2024.3446489)
- **PHT + STDM + BCH (2025 conference).** PSNR up to 44.46 dB, BER = 0 for most attacks, BER ≤ 0.30 under high-level AWGN. — [ICoABCD 2025](https://doi.org/10.1109/icoabcd67551.2025.11470836)
- **DCT + BCH (arXiv 2021).** Qualitative claims only. — [arXiv 2108.01612](https://doi.org/10.48550/arxiv.2108.01612)
- **Turbo coding plus double watermarking (2008).** 2000 bits in 256×256 medical images. — [JTE 2008](https://doi.org/10.1520/jte101051)

### Inferences
- **ECC cannot rescue a systematic failure.** Under a chroma gain k, dwtDctSvd's bit errors are systematic and correlated (all blocks with similar local chroma offset m drift the same way), so the raw BER can jump well past any code's threshold (about 15% for rate-1/4 LDPC). That is consistent with the user's ECCs recovering only about half the colour-failure frames.
- **The right pairing** is a gain-robust inner layer (a gain-invariant rule, or decoder-side gain search) plus a soft-decision outer code. The soft input should be per-bit vote fractions or distance-to-centroid LLRs from the repeated blocks.
- **ECC as a hypothesis test in a gain search.** In the decoder-side gain search (Section 5), the ECC or CRC check doubles as the selection test, which is how IHC-style systems use code checks.

### Gaps
- No post-2010 classical image-watermarking paper was found that reports soft-decision versus hard-decision coding gain in dB on real attacks.
- No classical image paper with polar or LDPC codes tests colour or gain attacks.
- RS-code results for images were not located.
