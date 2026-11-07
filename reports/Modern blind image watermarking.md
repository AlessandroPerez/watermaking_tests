# Blind watermarking advanced while its libraries froze

**Blind image watermarking has kept advancing since 2005; what stopped is the open-source code an engineer finds.** The two packaged Python libraries, invisible-watermark and blind_watermark, both ship a 2007–2008 DWT-DCT-SVD design. That design is fixed-step scalar QIM on one singular value per block, with no synchronization and no gain invariance, and neither library has had a PyPI release since 2023. The research that addresses the user's failures exists but never reached a reputable library. Gain-invariant quantization (Rational Dither Modulation, angle QIM, normalized-correlation QIM) was worked out between 2005 and 2014. Self-referencing and pilot-grid synchronization (Ma et al. 2021; Kawano and Kawamura 2024–2026; NAWE 2026) is the classical state of the art against rotation, cropping and translation, but **no verified classical scheme carries 256 or more bits through all three on a megapixel image**. After 2005, academic interest moved to security theory, industrial work went proprietary (Digimarc still ships classical Fourier-grid synchronization), and from 2018 neural networks took over. Meta's MIT-licensed **Pixel Seal (256 bits) and ChunkySeal (1024 bits) keep 0.93–0.99 bit accuracy under rotation, cropping and colour changes at PSNR 45–49 dB, where dwtDctSvd scores 50–63%**; they are not meaningfully better under JPEG down to quality 50, noise or blur, and both families fail under diffusion regeneration. In the user's experiment, **the colour failures (79% of all failures) come from an invertible chroma gain**, which shows up in the quantized value as an offset that depends on local colour. A decoder-side gain search built from PIL calls can remove most of them with a few dozen lines of glue code. **The geometric failures have no library-grade classical fix**, so under the library-only rule ChunkySeal is the only route that addresses them. Moving to the neural operating point (PSNR 44–51 dB) cuts dwtDctSvd's quantization step by a factor of 2–5, and its colour margin from 1.75–3.9 to 0.35–1.8 grey levels, so **matching PSNR widens the neural advantage rather than closing it**.

## Progress since 2005 went into theory, patents and neural nets, not libraries

**The algorithms look old because the libraries are old.** invisible-watermark was last released to PyPI as 0.2.0 on 6 July 2023 and still calls itself "still experimental". It is also the watermarker that Stable Diffusion v1 and the diffusers SDXL pipeline call, in its `dwtDct` mode ([invisible-watermark](https://github.com/ShieldMnt/invisible-watermark); [CompVis txt2img.py](https://github.com/CompVis/stable-diffusion/blob/main/scripts/txt2img.py); [diffusers SDXL](https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion_xl/watermark.py)). blind_watermark, with about 14.8k GitHub stars, was last released as 0.4.4 in April 2023 ([blind_watermark](https://github.com/guofei9987/blind_watermark)). Modern benchmarks label these designs DWT-DCT (Al-Haj 2007) and DWT-DCT-SVD (Navas et al. 2008) ([W-Bench](https://arxiv.org/abs/2410.18775); [WAM](https://arxiv.org/abs/2411.07231)).

The source code shows how little sits behind the name. `dwtDctSvd` converts the image to YUV and takes a one-level Haar DWT. In every 4×4 block of the LL band of the U channel only (default `scales=[0,36,0]`), it sets `s[0] = (s[0] // scale + 0.25 + 0.5*bit) * scale` and decodes with `(s[0] % scale) > 0.5*scale` ([dwtDctSvd.py](https://github.com/ShieldMnt/invisible-watermark/blob/main/imwatermark/dwtDctSvd.py)). Because an orthonormal DCT preserves singular values, the "DCT" stage changes nothing about s[0]. **The scheme is plain QIM on the largest singular value of the Haar-LL band of U**, which is the same construction blind_watermark applies to all three channels ([bwm_core.py](https://github.com/guofei9987/blind_watermark/blob/master/blind_watermark/bwm_core.py)). Theory has known since 2005 that fixed-step dither modulation is "largely vulnerable to amplitude scalings" ([Univ. Vigo RDM record](https://portalcientifico.uvigo.gal/documentos/5fa08253299952440aaea2ec?lang=en)). invisible-watermark's own README marks rotation, resizing and aspect-changing crops as "Fail" ([README](https://github.com/ShieldMnt/invisible-watermark)). **The user's failures follow from first principles, not from tuning.**

**The fundamentals were settled by about 2005–2008, and then the field's central question changed.** Costa's dirty-paper result, QIM, Rational Dither Modulation (*IEEE TSP* 53(10), October 2005) and dirty-paper trellis codes had laid the communication-theory core ([Dirty paper coding](https://en.wikipedia.org/wiki/Dirty_paper_coding); [RDM](https://doi.org/10.1109/tsp.2005.855407); [DPTC](https://doi.org/10.1109/tip.2003.821551)). In the same journal issue as RDM, Cayre, Fontaine and Furon recast the field's central question as one of security. They defined it as leakage of the secret key from observed watermarked content, measured by how many observations an attacker needs ([dblp](https://dblp.org/pid/48/5609), snippet).

The Break Our Watermarking System contests made this concrete. BOWS-1 fell to key-guessing and sensitivity attacks ([EURASIP JIS 2007](https://jis-eurasipjournals.springeropen.com/articles/10.1155/2007/25308), snippet). In BOWS-2, which ran from July 2007 to April 2008, "security flaws have been revealed" once "pirates could observe plenty of pictures watermarked with the same secret key" ([IEEE SPS](https://signalprocessingsociety.org/publications-resources/data-challenges/break-our-watermarking-system-2nd-ed); [HAL](https://hal.archives-ouvertes.fr/hal-00335311), snippet). Oracle attacks, which use a public detector to strip the mark, go back to 1998 ([Linnartz and van Dijk](https://unpaywall.org/10.1007%2F3-540-49380-8_18), snippet). Pierre Fernandez's 2025 thesis describes what followed as "the decline in watermarking research around the 2010s", as "focus shifted towards industry applications" and funding moved to "cloud computing and AI" ([Fernandez thesis](https://arxiv.org/html/2502.05215)).

**Volume continued; novelty thinned.** A 2025 bibliometric review counts **8,621 Web of Science watermarking publications from 2004 to 2024** ([Symmetry 2025](https://www.mdpi.com/2073-8994/17/6/871), snippet), so the field never stopped publishing. Much of the classical output in the 2010s, however, recombined DWT, DCT and SVD (often with metaheuristic tuning), or simply picked a different block element to quantize (QR, Schur, Hessenberg).

A strand of critique showed that many SVD schemes are structurally broken. In 2005, Zhang and Li showed that Liu and Tan's SVD scheme has **a false-positive probability of one**, because the extractor returns whatever reference watermark it is given ([Zhang & Li 2005](https://doi.org/10.1109/tmm.2005.843357)). Similar breaks followed for RDWT-SVD schemes ([Ling, Phan & Heng 2013](https://shdl.mmu.edu.my/5255/)). A 2021 review found "many existing hybrid SVD-based image watermarking schemes" insecure ([IEEE Access 2021](https://doi.org/10.1109/access.2021.3060861)).

Headline payloads of 4,096–24,576 bits in 512×512 hosts circulate from this literature **[UNVERIFIED]**. These figures typically come from scoring a logo by normalized correlation on about ten test images, rarely with any gain, gamma or saturation test. dwtDctSvd quantizes only the host's own singular value, so it avoids the false-positive flaw. **Its weakness is amplitude sensitivity, not security.**

**The real advances were never packaged, and the market did not ask for them.** The genuine classical advances (gain-invariant quantizers, informed coding, and periodic and pilot synchronization, all covered below) exist as papers or, in Digimarc's case, as patents. Searches found no maintained, reputable library implementing QIM, STDM, RDM, template synchronization or moment-invariant watermarking. The only code available is image-registration building blocks ([scikit-image example](https://scikit-image.org/docs/stable/auto_examples/registration/plot_register_rotation.html); [imreg_dft](https://github.com/matejak/imreg_dft)).

Deep learning arrived with HiDDeN in July 2018 ([HiDDeN](https://arxiv.org/abs/1807.09937)). It won because networks are "trained end-to-end … resilient to transformations applied during training", instead of needing an invariance hand-crafted for each attack ([Fernandez thesis](https://arxiv.org/html/2502.05215)). Generative-AI provenance revived industrial interest from 2023. But C2PA "soft binding" only needs the watermark to carry a lookup key into a manifest store ([Digimarc blog](https://digimarc.com/blog/c2pa-21-strengthening-content-credentials-digital-watermarks); [C2PA registry](https://spec.c2pa.org/softbinding-alg-list/softbinding-algorithm-list.json)). That explains why deployed payloads cluster at 100–136 bits, and why nobody optimized for 512-bit blind messages.

Finally, the neural papers that include classical baselines always run invisible-watermark at its defaults, with no synchronization and no ECC ([InvisMark](https://arxiv.org/abs/2411.07795); [WAM](https://arxiv.org/abs/2411.07231); [W-Bench](https://arxiv.org/abs/2410.18775)). So the literature keeps comparing new neural methods against the oldest classical design, and that design stays visible as "the" classical baseline.

## Classical state of the art: each failure has a known remedy, none packaged

The user's failures fall into three separate problems, each with its own literature since 2005: spatial synchronization (rotation, cropping, translation), amplitude invariance (the colour attacks), and coding.

### Self-referencing synchronization leads geometry, but stops near 300 bits

**A 1° rotation already breaks dwtDctSvd**, because the decoder reads 8×8-pixel blocks at fixed positions. Rotating a 1024×1024 frame by 1° about its centre moves every pixel beyond a radius of about 230 px by more than half a block (4 px). That is over 80% of the frame (my arithmetic). Desynchronization is not noise. Kawano and Kawamura state the consequence plainly: "redundancy is not effective against geometric attacks. The type and strength of geometric attacks need to be estimated" ([Kawano & Kawamura 2024](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741)). Ma et al. sort the remedies into five families: normalization, templates, invariant domains, feature points and periodic self-calibration. Only the last two "have the possibility [of] being robust to local geometric distortions" ([Ma et al. 2021](https://arxiv.org/abs/2007.10240)).

**Invariant domains and feature points each solve only half the problem.**

Moments handle rotation but not cropping. Xin's Zernike-moment scheme carries **160 bits on 256×256 at 42.5 dB, with maximum BER around 10⁻³ over 3–45° rotations** ([Xin thesis](https://mspace.lib.umanitoba.ca/bitstreams/072619e9-e7c0-4104-878e-f9590ebd8163/download)). But moments are computed about a centre. Zhang et al.'s affine-moment scheme detects perfectly after a 45° rotation, yet drops to **0 detection after a 10% crop**, and the authors call cropping "a common problem for the moment-based watermark algorithms" ([Zhang et al. 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3378516/)). Fourier–Mellin fares no better. Kang's ULPM, re-implemented by Ma at 64 bits, gives **7.6% BER at 5° rotation, 28% after a 50% crop and about 50% under aspect-ratio change** ([Ma et al. 2021](https://arxiv.org/abs/2007.10240)).

Feature-point regions survive cropping, because each region decodes on its own. Chen et al. decode **60 bits with BER 0 after 20–50% crop-off and 15–90° rotation on 1024×1024 images at 42–44 dB**. They fail, however, at 0.3× scaling and on simple textures ([Chen et al. 2020](https://www.mdpi.com/2076-3417/10/21/7494)). Payloads per region stay in the tens of bits. The "locally invariant" LDFT scheme shows 13.4% BER at 5° rotation and 38% after JPEG 50 ([Ma et al. 2021](https://arxiv.org/abs/2007.10240)). Explicit Fourier-peak templates can be estimated and interpolated away ([Herrigel et al. 2001](https://archive-ouverte.unige.ch/unige:47768)).

**Periodic self-reference is the strongest classical family.** When the watermark is tiled, any surviving tiles re-establish the lattice, which defeats both cropping and template removal. Translation then follows from a cyclic shift search over one period. Ma et al. compared Voloshynovskiy's autocorrelation scheme with their own symmetry-based one under identical conditions: 64 bits, no ECC, about 41 dB and 108 images ([Ma et al. 2021](https://arxiv.org/abs/2007.10240)). The BERs below were converted from bit-error counts out of 64 by the note author.

| Attack | ACF, Voloshynovskiy 2001 | Symmetry, Ma 2021 |
|---|---|---|
| Rotation 5° | 1.2% | 0.07% |
| Rotation 45° | 0.8% | 0.25% |
| Crop 50% | 1.1% | 0% |
| Crop 75% | 15% | 8.7% |
| Crop 25% + rotation 30° | 1.75% | 0.25% |
| StirMark random bending 1.0 | 14.6% | 0.9% |
| JPEG 50 | 0.3% | 0.25% |
| 5×5 average filter | 23% | 21% |

More recent classical work adds explicit estimation and coding.

- **Kawano and Kawamura (2024)** combine a grid pilot with SIFT-anchored DFT regions to carry **200 information bits (LDPC-coded to 300)**. They reach median BER 0 under the Japanese IHC criteria: 16-megapixel images scaled by 0.7–1.3 and cropped to 1920×1080. **The pilot costs about 3.4 dB of PSNR** ([Kawano & Kawamura 2024](https://petit.lib.yamaguchi-u.ac.jp/30297/files/168741)).
- **Their 2026 follow-up** embeds a three-valued grid pilot by QIM in the U channel and recovers the full affine matrix with a Radon transform. It carries **300 uncoded bits at 37.25 dB, with median BER below 0.1 at every rotation from 0° to 90°**, on 1080×1080 crops. These values were read from box plots, so they are approximate ([Kawano & Kawamura 2026](https://arxiv.org/abs/2601.18385)).
- **NAWE (September 2026)** tiles a periodic, perceptually masked carrier, synchronizes it by fitting the ACF lattice with RANSAC, and protects the payload with a rate-1/4 polar code plus CRC-16. It carries 16–256 bits on 512×512 images at 40 dB, with a **reference BER of 0.07 across 34 attack types**. Per-attack figures exist only in plots. NAWE is hybrid: its host estimator is a neural denoiser, although a BM3D variant lands within about 0.01 BER ([NAWE](https://arxiv.org/abs/2609.25972)).

**No verified classical scheme carries 256 or more bits through rotation, off-centre cropping and translation on a roughly 1-megapixel image.** The user's codewords raise the bar further. At 684–1548 coded bits on 1024×1024 pixels, they need **about 680–1,530 pixels per coded bit, 2.7–6 times denser than Ma's 4,096**. At the current 36.6 dB PSNR, the user had 4–5 dB more embedding power than Ma's 41 dB. At the new 44–51 dB target, they would have 3–10 dB less.

Exhaustive search at the decoder is the alternative to a reference signal. Barni showed that it beats template matching for detection reliability, provided the search space does not grow exponentially ([Barni 2005](https://doi.org/10.1109/lsp.2004.840872)). Kawano and Kawamura call brute-force synchronization "computationally expensive" ([Kawano & Kawamura 2026](https://arxiv.org/abs/2601.18385)). For a 1024×1024 frame, keeping the corner displacement under half a block needs angle steps of about 0.3°, multiplied by the block-phase and block-offset translations (my arithmetic).

None of these synchronization schemes exists in a reputable library. scikit-image's `warp_polar` and `phase_cross_correlation` supply registration primitives ([scikit-image](https://scikit-image.org/docs/stable/auto_examples/registration/plot_register_rotation.html)), but the pilot or template embedder and detector would have to be hand-written.

### Gain-invariant quantization solved colour attacks on paper in 2005

Plain QIM breaks under any amplitude scaling. Since 2005 the literature has made the quantizer gain-invariant in four ways.

**Normalize by a gain-covariant statistic.** RDM computes the step from past watermarked samples, so a global gain scales step and signal together, and it reaches "much higher rates for the same bit error probability" than improved spread spectrum ([RDM](https://doi.org/10.1109/tsp.2005.855407)). Li and Cox's Watson-slack QIM is "theoretically invariant to valumetric scaling". They add that "scaling can still result in errors due to cropping and roundoff" ([Li & Cox 2007](https://doi.org/10.1109/tifs.2007.897266)).

**Quantize an angle.** Angle QIM is "provably insensitive to amplitude scaling" ([AQIM](https://doi.org/10.1109/icassp.2005.1415525)), and difference-angle QIM followed in 2015 ([DAQIM](https://doi.org/10.1016/j.image.2015.03.010)).

**Quantize a normalized correlation.** NCQM was tested on 1,000 images against RDM, STDM and a ratio method at equal MSSIM ([Zhu et al. 2014](https://ieeexplore.ieee.org/ielx7/6046/6922170/06860239.pdf)). It held **BER ≤ 2.5% over gains from 0.1 to 2**. Under gamma correction its worst BER was **4.9%**. It reached about 0 under a log transform, 6.9% under contrast stretching and 14% under histogram equalization, and stayed under 12% for JPEG quality above 20.

**Estimate the gain at the receiver.** Kang, Huang and Zeng embed a training sequence from which the decoder estimates the decision zones and the step. They report gains under DC shifts, histogram equalization, colour reduction, linear scaling and gamma correction ([Kang et al. 2008](https://doi.org/10.1109/tmm.2008.2001361)). Shterev and Lagendijk derived maximum-likelihood and Fourier-based scale estimators ([TU Delft](https://research.tudelft.nl/en/publications/amplitude-scale-estimation-techniques-for-quantization-based-wate/)).

Informed coding is gain-invariant by construction. Dirty-paper trellis codes are spherical codes, and they carried **1,380 bits in 240×368 images**, robust to "changes in contrast" and lossy compression, on 2,000 images ([Miller, Doërr & Cox 2004](https://doi.org/10.1109/tip.2003.821551)). The price was slow iterative embedding (later sped up 600-fold) and acknowledged security weaknesses ([ICIP 2005](https://doi.org/10.1109/icip.2005.1529846); [SPIE 2009](https://doi.org/10.1117/12.839853)). On colour images, adaptive STDM on HSI intensity carried 3,600 bits and was tested under gains from 0.1 to 2.0 ([Ma et al. 2010](https://www.jstage.jst.go.jp/article/transinf/E93.D/4/E93.D_4_843/_pdf)).

Four caveats matter for this user:

- **Gamma is only partly handled.** It acts as a local gain that depends on intensity.
- **Invariance must be built on zero-mean features.** U carries a 128 offset, so a gain-invariant rule applied to raw U, or to s[0] of raw U, still breaks.
- **Luminance versus chroma is untested.** No study compares embedding in luminance and in chroma under brightness, contrast, saturation and gamma at a fixed PSNR. Quaternion colour schemes target channel-exchange attacks, not these.
- **No maintained library implements any of these embedding rules.** Adopting one would mean hand-written code, which the user's rule excludes. The receiver-side branch is the one the rule leaves open.

### The two research notes on colour failures describe one mechanism: a chroma gain becomes an offset

One research note treats the user's colour attacks as gains and the other as offsets. Both are right, at different points in the pipeline.

**The gain view.** In `wmecc/attacks.py`, the PIL Brightness, Contrast and Color enhancers use k = 1 ± p/100. Each blends the image with an achromatic partner: black for Brightness, uniform mean grey for Contrast, and the image's own greyscale for Color. An achromatic pixel has U = 128 in OpenCV's YUV, so all three operations map (U−128) to k·(U−128) exactly, apart from rounding and clipping.

**The offset view.** dwtDctSvd does not quantize U−128. It quantizes s[0] of a 4×4 block of the orthonormal Haar-LL band. For a DC-dominated block that is close to the DCT DC term, 8·mean(U) over the block's 8×8 pixels, so **s[0] ≈ 8·(128 + m)**, where m is the local mean of U−128. Under the gain, s[0] moves by about **8·(k−1)·m**. A global gain on the zero-mean chroma therefore becomes a block-by-block offset on the quantized value, proportional to local colour. The offset note's arithmetic, in which a uniform U shift δ moves s[0] by 8δ, applies unchanged with δ = (k−1)·m.

**When a bit flips.** Embedding places s[0] at 0.25Q or 0.75Q inside its bin, and the decoder's boundary is at 0.5Q. A shift Δ therefore flips the bit when Δ mod Q lies between Q/4 and 3Q/4. It aliases back to correct between 3Q/4 and 5Q/4, and the pattern repeats with period Q. In chroma terms, a bit flips when (k−1)·m mod Q/8 lies between Q/32 and 3Q/32. Gamma, applied with scikit-image's `adjust_gamma` as a power law on RGB, is not a pure chroma gain. To first order it acts by the same mechanism, with k varying with local luminance.

The table uses the library default step, the user's real steps of 56–126, and the steps the user would need at the neural operating point. The matched-PSNR rows assume embedding distortion scales with Q², as it does for QIM.

| Step Q | Operating point | s[0] shift where flipping starts (Q/4) | Local chroma shift (k−1)·m that flips (grey levels) | \|m\| that flips at k = 0.8 or 1.2 | \|m\| that flips at k = 1.4 (saturation +40) |
|---|---|---|---|---|---|
| 36 | Library default | 9 | 1.1–3.4 | 5.6–16.9 | 2.8–8.4 |
| 56 | User, wPSNR 40 dB | 14 | 1.75–5.25 | 8.8–26.2 | 4.4–13.1 |
| 126 | User, wPSNR 40 dB | 31.5 | 3.9–11.8 | 19.7–59.1 | 9.8–29.5 |
| ≈25 | PSNR ≈44 dB (Q=56 code) or ≈51 dB (Q=126 code) | 6.3 | 0.78–2.3 | 3.9–11.7 | 2.0–5.9 |
| ≈11 | PSNR ≈51 dB (Q=56 code) | 2.8 | 0.35–1.05 | 1.75–5.2 | 0.9–2.6 |

Three consequences follow. All are inferences from the code and this arithmetic.

**The errors are systematic and spatially correlated, not random.** Grey regions (m ≈ 0) never flip, while every block whose colour puts (k−1)·m inside the window flips together. At the user's current steps, a ±10% attack flips only strongly coloured blocks (|m| ≥ 17.5–39). A ±30% attack or a ±40% saturation change also flips moderately coloured blocks: |m| from about 4–17 at Q = 56, and about 10–39 at Q = 126.

**ECC cannot fix them.** The keyed layout in `wmecc/watermark/imwm.py` spreads each bit's votes over the whole frame. Every bit therefore sees roughly the frame-wide fraction f of flipped blocks:

- While f is well below one half, majority voting absorbs it.
- As f approaches one half, all vote fractions collapse towards 0.5 together, and the d′ separation goes to 0.
- Above one half, the votes invert coherently, and the blind Gaussian-mixture labelling hands the decoder the complement of the codeword.

The outcome is a frame-level threshold set by colour content and attack strength, and it is the same for every code. That fits every code recovering only about half of the colour-attacked frames.

**The "about half" has a different cause from the one the offset note assumed.** That note pictured a single global shift whose phase lands in the flip window about half the time. With the PIL attacks and the user's large steps, the first window dominates, so f grows with how colourful the image is. This can be tested directly: compute f for each frame from the cover's map of m and the attack's k, and check whether failures cluster at high f.

### Coding helps random errors and cannot touch systematic ones

Coding gains in classical watermarking are real whenever errors look random:

- LDPC codes "doubled" spread-spectrum payload relative to BCH or repetition codes ([Bastug & Sankur 2004](https://doi.org/10.1109/lsp.2003.819350)).
- A turbo-decoded BCH product code, carrying 121 bits at about 38 dB, moved the first message error from JPEG quality ≈50 to ≈25 ([Rey et al. 2003](https://doi.org/10.1117/12.477323)).
- A (800,200) PEG-LDPC code decoded without failure up to a 15% channel error rate, where a concatenated BCH+LDPC code failed at 14%. That allowed **BER 0 at 41.1 dB under the IHC v4 benchmark**: 200-bit messages in 4608×3456 images after strong JPEG, cropping, scaling and rotation ([Hirata et al. 2017](https://www.jstage.jst.go.jp/article/transinf/E100.D/1/E100.D_2016MUP0003/_pdf)).
- Abrardo and Barni concatenated gain-robust dirty-paper codes with a turbo code fed by soft estimates from the inner decoder ([Abrardo & Barni 2005](https://doi.org/10.1109/tsp.2004.839909)).
- A 2024 scheme with polar codes and neural extraction reached **650–1,600 bits in 1920×1080 images at 39.66 dB**, with error probability 0.01 after Facebook, VK, Telegram and WhatsApp ([IEEE Access 2024](https://doi.org/10.1109/access.2024.3446489)).

The 2008–2020 statistical-decoder literature (generalized Gaussian, Cauchy, NIG and HMM models) is mostly about one-bit detection. Its idea that transfers is soft decoding ([Kwitt et al. 2011](https://doi.org/10.1109/tip.2010.2064327); [Amini et al.](https://doi.org/10.1109/tcsvt.2016.2607299)), and the user's harness already does this by turning vote fractions into Gaussian-mixture LLRs.

**The user's gain from 61% to 84–85% exact recovery is what coding should deliver on random-like errors.** The remaining failures are systematic: desynchronization, and colour flips that are correlated across the frame. These push raw BER past any code's threshold at once, and no classical paper reports LDPC or polar codes under gain or colour attacks. The literature supports pairing a gain-robust inner layer with a soft outer code. In that pairing, the ECC or CRC check doubles as the hypothesis test of a parameter search, which is how IHC-style systems use it.

**Capacity is not the binding constraint.** Scaling dirty-paper trellis density to 1024×1024 gives roughly 16 kbit of raw capacity (a back-of-envelope estimate). Meta's capacity analysis bounds robust capacity at about 3,013 bits against a 50% crop-and-rescale, at PSNR 42 dB on 256×256 images. It concludes that "recent methods operate far below the achievable bounds, often by orders of magnitude" ([ChunkySeal](https://arxiv.org/abs/2510.12812)).

## Neural methods win geometry and colour by 35–50 points, and little else

Neural post-hoc watermarking went through four steps:

- **HiDDeN (2018):** 30 bits in 128×128 images at about 33.6 dB ([HiDDeN](https://arxiv.org/abs/1807.09937)).
- **MBRS:** 625 bits in 400×400 at 39.3 dB, with BER 0.0012% after JPEG 50. Its training "crop" was only a black mask, so it collapses under real geometry ([MBRS](https://arxiv.org/abs/2108.08211); [Video Seal](https://arxiv.org/abs/2412.09492)).
- **Pixel Seal:** 256 bits at 48.9 dB on 1280×1280 images, with geometric bit accuracy of 0.95/0.93, where no other method passes 0.84 ([Pixel Seal](https://arxiv.org/abs/2512.16874)).
- **ChunkySeal:** 1,024 bits at 45.3 ± 2.2 dB, with 99.15% overall bit accuracy ([ChunkySeal](https://arxiv.org/abs/2510.12812)).

InvisMark's paper (100 bits at 51.4 dB) gives the cleanest head-to-head comparison against dwtDctSvd, because it ran both on the same attacks ([InvisMark](https://arxiv.org/abs/2411.07795)).

| Attack | dwtDctSvd (InvisMark test, 38–40 dB) | InvisMark (100 bits, 51.4 dB) | Pixel Seal (256 bits, 48.9 dB) | ChunkySeal (1024 bits, 45.3 dB) |
|---|---|---|---|---|
| Rotation | 52.6% (0–10°) | 97.4% | 0.99 (5° and 10°) | 98.3% (≤10°) |
| Crop | 52.4% (resized crop 0.75–1.0) | 97.3% | 0.95 (crop 0.63), 0.90 (0.55) | 98.3% (crop 77–95%) |
| Perspective 0.1 | 50.1% | 100% | 1.00 | — |
| Contrast | 62.8% (0.75/1.25) | 99.9% | 0.92 (2.0) | 99.5% |
| Saturation | 59.2% (0.75/1.25) | 100% | — | — |
| Brightness | 93.6% (0.75/1.25) | 99.7% | 0.91 (2.0) | 99.0% (0.5–1.5) |
| JPEG | 80.8% (q ≥ 50) | 99.5% | 0.97 (Q50) | 98.8% (Q50–80) |
| Gaussian noise σ 0.04 | 98.8% | 100% | — | — |
| Gaussian blur | 99.7% | 100% | 1.00 | — |

Sources: [InvisMark Table 3](https://arxiv.org/abs/2411.07795); [Pixel Seal](https://arxiv.org/abs/2512.16874); [ChunkySeal Table 3](https://arxiv.org/abs/2510.12812).

**Geometry and colour are where the neural advantage is overwhelming: a 35–50-point gap in bit accuracy.** WAM's test of invisible-watermark's DWT-DCT shows the same pattern: 50.2% after a 20% crop, 50.7% under ±10° rotation, and 47–49% under 2× brightness, contrast or saturation ([WAM](https://arxiv.org/abs/2411.07231)). WAM's text does not name the mode; it is most likely `dwtDct` **[UNVERIFIED]**. Pixel Seal still decodes 0.86 under a combination of JPEG 40, a 0.71 crop and 0.5 brightness ([Pixel Seal](https://arxiv.org/abs/2512.16874)). dwtDctSvd's mild brightness loss in InvisMark's harness (93.6%) fits the gain analysis above if that harness's brightness is additive, since an additive shift leaves U untouched. This is an inference; the harness implementation was not checked.

**Elsewhere the neural advantage is small or absent.**

- **Noise, blur, posterization and random erasing:** dwtDctSvd already scores 98.8%, 99.7%, 99.5% and 99.8%. Under noise it beats TrustMark (69.9%) and StegaStamp (88.9%) ([InvisMark](https://arxiv.org/abs/2411.07795)).
- **JPEG:** neural models score higher in the published tests, but the user's own system already survives quality 50.
- **Regeneration:** both families fail.
  - After diffusion regeneration, dwtDctSvd's true-positive rate at 0.1% false positives falls to 1.4–3.1% ([W-Bench](https://arxiv.org/abs/2410.18775)).
  - Regeneration removes over 99% of DwtDctSvd, RivaGAN and SSL marks ([Zhao et al.](https://arxiv.org/abs/2306.01953)).
  - Under DiffPure, WAM decodes 49.1% of bits against DWT-DCT's 49.5% ([WAM Table 9](https://arxiv.org/abs/2411.07231)).
  - Only heavily distorting models (StegaStamp, VINE and MBRS, at PSNR 27–40 dB) survive regeneration.

**The neural results carry caveats the user should weigh.**

- **Independent re-tests come out lower.**
  - Google's benchmark gives InvisMark a 50.06% true-positive rate on its worst spatial attacks, against InvisMark's own ≥97% bit accuracy ([SynthID-Image](https://arxiv.org/abs/2510.09263)).
  - A 2026 study that retrained ChunkySeal at 64 bits on 128×128 images got only 82.3% under crop-and-resize and 87.9% under rotation ([CASIAL](https://arxiv.org/abs/2607.26729)).
  - An independent September 2026 benchmark finds that "geometric misalignment causes the sharpest reduction in payload recovery", even for the strongest methods ([arXiv 2609.16832](https://arxiv.org/abs/2609.16832)).
- **High PSNR does not mean invisible.** Video Seal's authors say most methods "are visible under close inspection, especially in flat areas, like the skies" ([Video Seal](https://arxiv.org/abs/2412.09492)).
- **The compute cost is large.** ChunkySeal has a 1,022.7M-parameter embedder and a 773.7M-parameter extractor ([ChunkySeal](https://arxiv.org/abs/2510.12812)).
- **dwtDctSvd has its own security weakness.** Its pattern does not depend on the image. Averaging many marked images drops its accuracy to 0.57 and exposes a "barcode"-like pattern, while content-adaptive neural marks stay above 0.95 ([Yang et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/67b2e2e895380fa6acd537c2894e490e-Abstract.html)). The user embeds one fixed message in every image, which is exactly the exposed case (inference).
- **The published comparisons are unfair to classical methods.** No neural paper compared against a synchronized classical scheme. They show that unsynchronized DWT-DCT-SVD loses, not that synchronized classical watermarking loses.

### Matching PSNR widens the gap instead of closing it

**The published comparisons gave the classical method 4–13 dB more distortion budget, and it still lost.** dwtDctSvd ran at 38.3–40.2 dB in InvisMark's test, 38–41 dB in TrustMark's and 40.4 dB in W-Bench ([InvisMark](https://arxiv.org/abs/2411.07795); [TrustMark](https://arxiv.org/abs/2311.18297); [W-Bench](https://arxiv.org/abs/2410.18775)). The neural methods ran at 44–51 dB: InvisMark 51.4, Pixel Seal 48.9, Video Seal 1.0 44.4–48.7 and ChunkySeal 45.3. Matching PSNR therefore takes away the extra distortion budget the classical method had, while the neural numbers already sit at the target operating point.

With the user's measured gap between PSNR and wPSNR, PSNR 44–51 corresponds to wPSNR 47–54, which is 7–14 dB above the current wPSNR of 40. **The quantization step therefore shrinks by a factor of 0.45–0.20.** The user's steps of 56–126 become **about 25–56 at PSNR 44 and about 11–25 at PSNR 51**, a range with the library default of 36 near its middle. Four consequences follow from the table above:

- **The colour flip threshold falls to 0.35–1.8 grey levels** of local chroma shift.
- **The flip window aliases rapidly.** At Q ≈ 11–25 under a ±20% attack, it repeats every 7–16 grey levels of chroma offset, so about half of all coloured blocks flip, regardless of how colourful the image is.
- **The margin against random noise also shrinks.** Vote repetition still averages random noise such as JPEG and additive noise, but that margin falls in proportion to Q. JPEG-50 survival should be re-measured rather than assumed.
- **The classical synchronization gap widens.** The distance to Ma et al.'s verified density grows by 3–10 dB.

One caveat runs the other way: **matched PSNR is not matched visibility.** The Pixel Seal paper attributes Video Seal 0.0's 53.7 dB to "very localized artifacts, which yield, on average, a high metric value but are very visible" ([Pixel Seal](https://arxiv.org/abs/2512.16874)). The user should inspect flat regions, not only PSNR and wPSNR.

## Digimarc is the classical holdout; every vendor since 2023 ships neural

| System | Approach | Payload | Availability |
|---|---|---|---|
| Digimarc (packaging, C2PA `com.digimarc.validate.1`) | Classical: tiled mark plus a Fourier-domain peak grid for affine estimation; phase gives translation | Not public; GTIN-class identifiers | Proprietary, patented |
| Google SynthID-Image | Neural encoder/decoder, post-hoc | 136 bits (SynthID-O, 512×512) | Closed; "through partnerships" |
| Meta Video Seal 1.0 / Pixel Seal / ChunkySeal / WAM | Neural | 256 / 256 / 1024 / 32 bits | MIT |
| Adobe TrustMark | Neural | 100 bits with BCH options | MIT; in the C2PA registry |
| Microsoft InvisMark | Neural | 100 bits released (256 in the paper) | MIT; in the C2PA registry |
| Imatag, Steg.AI | Neural (Imatag's BZH is derived from HiDDeN; the basis of its LaMark is **[UNVERIFIED]**) | Not public | Proprietary |

Sources: [US 8,301,453](https://patents.google.com/patent/US8301453B2/en); [SynthID-Image](https://arxiv.org/abs/2510.09263); [videoseal](https://github.com/facebookresearch/videoseal); [TrustMark](https://github.com/adobe/trustmark); [InvisMark](https://github.com/microsoft/InvisMark); [HF blog on Imatag](https://huggingface.co/blog/imatag-vch/stable-signature-bzh); [Rutgers on Steg.AI](https://www.rutgers.edu/news/rutgers-office-research-helps-launch-company-using-ai-prevent-deepfakes).

**Digimarc's patents describe exactly the classical synchronization architecture that this report favours in principle.** US 8,301,453 (priority 2000) describes a grid that "comprises a collection of impulse or delta functions in the Fourier magnitude domain". Rotation and scale come from log-polar correlation, and translation from the impulses' known pseudo-random phases ([US 8,301,453](https://patents.google.com/patent/US8301453B2/en)). US 9,182,778 (adjusted expiry 31 October 2033) replaces the Fourier–Mellin search with an iterative least-squares refinement of the 2×2 transform. It claims this is more accurate and needs fewer evaluations ([US 9,182,778](https://patents.google.com/patent/US9182778B2/en)).

The deployment evidence comes from trade-press reports of the HolyGrail 2.0 recycling project. They report **99% detection** on about 125,000 packs in 2022 semi-industrial trials, and **87.9–93.8% detection** in a 2024 single-pass trial at a German materials recovery facility ([Packaging Europe](https://www.packagingeurope.com/holygrail-20-concludes-semi-industrial-trials-with-successful-validation/); [Packaging Insights](https://www.packaginginsights.com/news/holygrail-20-digital-watermarks-project-validates-detection-sorting-in-semi-industrial-trials.html); both snippets). Digimarc's claim that its marks "resist common modifications such as cropping, rotation, resizing" comes without published data ([Digimarc blog](https://digimarc.com/blog/c2pa-21-strengthening-content-credentials-digital-watermarks)).

**The lesson is that classical, explicitly synchronized watermarking works at industrial scale when the geometry comes from cameras rather than from adversaries.** But no open implementation of it exists.

Every large platform that published a watermarking method from 2023 onwards (Google, Meta, Adobe, Microsoft) chose neural encoder/decoders. SynthID has marked "over ten billion images and video frames" ([SynthID-Image](https://arxiv.org/abs/2510.09263)). The C2PA soft-binding registry lists 28 algorithms, and among its image watermarks only TrustMark and InvisMark are open source ([C2PA registry](https://spec.c2pa.org/softbinding-alg-list/softbinding-algorithm-list.json)). The relevant standard, ISO/IEC 21617-3 (JPEG Trust Part 3, media asset watermarking), is algorithm-agnostic. Sources conflict on whether it was published in July 2026 or is still a draft ([BSI](https://knowledge.bsigroup.com/products/bs-iso-iec-21617-3-information-technology-jpeg-trust-part-3-media-asset-watermarking); [ISO](https://www.iso.org/standard/90209.html)).

## Two frozen classical libraries and one neural repo can carry 512 bits

| Library | Maintainer, licence | Latest release | Algorithm and payload | Status for this user |
|---|---|---|---|---|
| [invisible-watermark](https://github.com/ShieldMnt/invisible-watermark) | ShieldMnt, MIT | PyPI 0.2.0, July 2023 | `dwtDct`, `dwtDctSvd` (U only, no synchronization); RivaGAN (32 bits) | Current carrier; classical baseline |
| [blind_watermark](https://github.com/guofei9987/blind_watermark) | Guo Fei, MIT | PyPI 0.4.4, April 2023 | DWT-DCT-SVD QIM on s[0] and s[1], all of YUV | Same failure class; its crop recovery matches against the original, so it is not blind ([recover.py](https://github.com/guofei9987/blind_watermark/blob/master/blind_watermark/recover.py)) |
| [videoseal](https://github.com/facebookresearch/videoseal) | Meta FAIR, MIT (code and models, per the README) | Last push July 2026; PyPI 1.0.1 (July 2025) predates Pixel Seal and ChunkySeal | Video Seal 1.0 (256), Pixel Seal (256), ChunkySeal (1024) | Only open carrier with 512+ bits; install from GitHub |
| [trustmark](https://github.com/adobe/trustmark) | Adobe, MIT (code and model files) | PyPI 0.9.2, September 2026 | 100 bits with BCH; Python, Rust, JS (decode only), C++ (ONNX) | Best packaged; payload too small |
| [InvisMark](https://github.com/microsoft/InvisMark) | Microsoft, MIT | Last push April 2026; no releases | 100-bit weights, no ECC | Payload too small |
| [watermark-anything](https://github.com/facebookresearch/watermark-anything) | Meta, MIT (SA-1B model) | Archived 2025 | 32 bits, localized | Payload too small |
| [scikit-image](https://scikit-image.org/docs/stable/auto_examples/registration/plot_register_rotation.html) | BSD | 0.26.0 | `warp_polar`, `phase_cross_correlation` | Registration primitives only, not a watermark |
| [WatermarkLab](https://watermarklab.github.io) | J. Chen, "MIT License with Additional Terms" | 0.1.22, November 2025 | Benchmark covering DctDwt, DctDwtSvd, TrustMark, InvisMark, StegaStamp and VINE; 44 attacks | Optional harness |
| [omnisealbench](https://github.com/facebookresearch/omnisealbench) | Meta, MIT core | Archived June 2026 | Benchmark including DCTDWT and PixelSeal | Optional harness |

No reputable library implements RDM, STDM, NCQM or angle QIM. None implements template, periodic or pilot synchronization, and none implements moment-invariant watermarking. The only Fourier–Mellin code found is for image registration, and imreg_dft has had no release since 2016 ([imreg_dft](https://github.com/matejak/imreg_dft)). It could not be confirmed where SyncSeal, Meta's neural synchronization add-on, is released or under what licence. The READMEs state that the videoseal and TrustMark checkpoints are MIT-licensed, but the checkpoint files themselves were not inspected. VINE, Meta's `ssl_watermarking` and most of `stable_signature` are non-commercial, and MBRS and CIN carry no licence.

## Five routes for your experiment, ranked against the library rule

| Rank | Route | Fixes | Library rule | Hand-written code | Main risk |
|---|---|---|---|---|---|
| 1 | Chroma-gain and gamma search in front of the unmodified dwtDctSvd decoder | Brightness, contrast and saturation (exact up to clipping and rounding); most of gamma | Pixel operations are library calls (PIL `ImageEnhance.Color`, scikit-image `adjust_gamma`); decoder unmodified | Yes: the candidate loop and the acceptance rule | 15–50 decodes per frame; false acceptance grows with the number of candidates; no geometric benefit |
| 2 | ChunkySeal (videoseal, MIT) as the carrier at PSNR 44–51 | Rotation, cropping, translation as crop, colour, JPEG | Compliant | None, unless strength must be set by blending | 1.8B parameters on GPU; only Meta's numbers at 1,024 bits; codewords over 1,024 bits do not fit |
| 3 | Pixel Seal or Video Seal 1.0 (256 bits) | Same classes; best published geometric scores | Compliant | Payload split across two embeddings | 512 information bits do not fit; double embedding untested |
| 4 | SyncSeal in front of the unmodified dwtDctSvd, plus route 1 | Geometry and colour while keeping the classical carrier | Only if SyncSeal is released as a library (unconfirmed) | Pipeline glue | 3.8–6.6 px residual misalignment against 8-px blocks; SyncSeal alone uses the whole 44 dB budget |
| 5 | Classical synchronization layer (periodic tiles, pilot grid, Fourier peaks) around dwtDctSvd | Geometry | Not compliant | The template or pilot embedder and detector, which is the core of the method | Unverified at this density; the pilot costs up to 3.4 dB; template-removal attacks |

### Route 1: decoder-side gain and gamma search (classical; first because it is cheap)

**Route 1 attacks the largest failure class with the least code.** The three PIL operations all scale U−128 by k, and the greyscale blend partner sits at U = 128. So `ImageEnhance.Color(attacked).enhance(1/k)` restores U exactly, apart from clipping and rounding, whichever of the three operations was applied, and dwtDctSvd reads only U. For gamma, `skimage.exposure.adjust_gamma(attacked, 1/g)` inverts the power law, apart from 8-bit quantization of dark tones.

The decoder loops over a grid of k and a grid of g, runs the unmodified dwtDctSvd decoder on each candidate, and keeps one candidate. Either it picks the candidate with the largest d′ separation (the harness's own statistic) and decodes it once, or it accepts the first ECC success that a CRC confirms. This is the exhaustive-search version of Shterev–Lagendijk scale estimation and of Kang et al.'s adaptive receiver ([TU Delft](https://research.tudelft.nl/en/publications/amplitude-scale-estimation-techniques-for-quantization-based-wate/); [Kang et al. 2008](https://doi.org/10.1109/tmm.2008.2001361)). Barni's analysis warns that false positives grow with the number of hypotheses ([Barni 2005](https://doi.org/10.1109/lsp.2004.840872)), which is why the selection statistic or the CRC matters.

How fine the grid must be depends on the step:

- **At Q = 56:** with |m| up to about 30, the residual gain error must stay under about 0.06. A k step of about 0.1 suffices, roughly 10 candidates over 0.6–1.5.
- **At the matched operating point:** the smallest steps are Q ≈ 11–25, reached at PSNR 51 for every code and at PSNR 44 for the longest code. They tighten the tolerance to 0.012–0.026, which takes about 17–38 candidates.

A gamma grid comes on top of either.

The payoff has a simple upper bound. The best codes fail on 15–16% of frames, and 79% of those failures are colour attacks. Recovering all of them would lift exact recovery to roughly 97%, though clipping in brightened highlights and gamma's non-linearity will leave some failures.

**This route requires hand-written code**: the candidate loop and the acceptance rule. Every pixel operation and the watermark decoder remain library calls, and the library itself is untouched. Whether that counts as a hand-written algorithm is the user's call. It is the same class of glue as the harness's existing keyed layout and Gaussian-mixture LLR code. Route 1 does nothing for geometry.

### Route 2: ChunkySeal (neural; the only fix for geometry that keeps the library rule)

ChunkySeal is the only open, maintained model from a reputable organization that holds 512 information bits plus parity in one embedding. Its native PSNR of 45.3 ± 2.2 dB already lies inside the 44–51 dB window.

- **Which codes fit:** codes with n ≤ 1,024, that is rate ≥ 1/2 for 512 information bits. The user's 684-bit codes fit; the 1,548-bit ones do not.
- **What the codes would face:** ChunkySeal's published bit accuracy is 98–99% under rotation up to 10°, crops of 77–95%, brightness of 0.5–1.5× and JPEG 50–80 ([ChunkySeal](https://arxiv.org/abs/2510.12812)). That implies a raw BER of about 1–2%, which would make the ECC comparison meaningful on a geometrically robust channel.
- **Installation:** from the GitHub repository, because PyPI's videoseal 1.0.1 predates ChunkySeal.

Three points remain unverified:

- whether ChunkySeal exposes a strength parameter, as Video Seal does, or must be calibrated by blending the marked and original images;
- how it behaves on 1024×1024 frames;
- whether it exposes soft per-bit outputs for the existing LLR pipeline.

**The only evidence at 1,024 bits is Meta's own**, and the independent 64-bit retraining scored lower ([CASIAL](https://arxiv.org/abs/2607.26729)). The user's harness, with the currently excluded rotation, crop and translation attacks added back, would be the first independent test at this payload.

### Routes 3–5: fallbacks and rule-breaking options

**Route 3 is the fallback if ChunkySeal is too heavy or misbehaves at 1024×1024.** Pixel Seal has the best published geometric scores with only 77M parameters ([Pixel Seal](https://arxiv.org/abs/2512.16874)). But its 256 bits cannot hold the 512-bit message unless the message is split across two embeddings, which is untested.

**Route 4 is the architecture closest to the user's preference for non-ML methods, if SyncSeal becomes available.** SyncSeal regresses and inverts the geometric transform before any primary decoder runs. Under 30° rotation, a 0.5 crop and 0.3 perspective, it lifted TrustMark from 0.50/0.53/0.51 to 0.99/0.92/0.97 bit accuracy ([SyncSeal](https://arxiv.org/abs/2509.15208)). Three problems stand in the way:

- **Residual misalignment:** its corner error of **3.8 px after a 0.7 crop and 6.6 px after 0.1 perspective** is at or beyond half of dwtDctSvd's 8-pixel block.
- **Distortion budget:** **SyncSeal alone runs at 43.9 dB**, which leaves no budget for dwtDctSvd at a 44 dB target.
- **Independent evidence:** a separate benchmark found that its benefit "varies widely" and that it adds a fidelity cost to every method ([arXiv 2609.16832](https://arxiv.org/abs/2609.16832)).

**Route 5 violates the rule, because the synchronization signal is itself the method.** It is also unverified at 2.7–6 times Ma et al.'s density. A Kawano-style pilot embedded by QIM in U would compete with dwtDctSvd for the same channel. And sparse Fourier templates can be removed.

### Options not to pursue

**Moving the mark to Y.** This needs only the library's `scales=[s,0,0]` parameter, so it complies with the rule. It should fix saturation, which leaves Y unchanged. But brightness would shift s[0] ≈ 8·Y by 8(k−1)·Y, and contrast by 8(k−1)·(Y−Ȳ). Luminance levels of about 50–200 dwarf typical chroma offsets, so both attacks should get much worse. This is an inference, and it is cheap to test.

**Gain-invariant embedding rules (RDM, NCQM, AQIM).** These would fix colour at the source, but no library implements them.

**blind_watermark's crop recovery.** It needs the original image, so it breaks blind extraction.

### Measurement plan

The sensible order is:

1. Validate the colour mechanism by predicting each frame's flipped-block fraction f from the cover image and k.
2. Re-calibrate Q to wPSNR 47–54 and re-run the 77 attacks, with and without route 1.
3. Run ChunkySeal on the same 100 images at the same PSNR, including the excluded geometric attacks.
4. Report the true-positive rate at 0.1% false positives alongside exact-message recovery, so the results line up with WAVES, W-Bench and Meta's tables.

## Conclusion

The premise that blind watermarking stalled mistakes what has been packaged for what is known. Both of the user's failure classes were diagnosed, and solved on paper, by about 2005: RDM and its successors for amplitude, templates and self-reference for geometry. The gap is engineering availability, and a "reputable library only" rule turns that gap into the deciding constraint. For colour, the fix can be assembled from PIL and scikit-image calls around the unmodified decoder. For geometry, the only library-grade answer today is neural.

The deeper point is that the colour failure is not noise at all. It is an unknown but deterministic and invertible transform, a synchronization problem in amplitude, just as rotation and cropping are synchronization problems in space. Both call for the same treatment: estimate the transform, invert it, decode, and use the code to verify the hypothesis rather than to absorb the damage. That is also why the current ECC comparison cannot separate the codes on half the colour-attacked frames. Until the systematic failures are removed, a code ranking measures random-error performance only on frames that were never in danger.

Moving to PSNR 44–51 dB will make dwtDctSvd a weaker baseline, not a fairer one. The published classical-versus-neural gap was measured with the classical side holding the larger distortion budget.
