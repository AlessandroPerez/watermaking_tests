# Error-correcting codes (ECC) in image watermarking, 2020–2026: recent work, evaluation practice, semi-blind/soft decoding, bibliometrics and open gaps

Research date: 2026-11-04. Scope: 2020–2026, mainly images; text (LLM), audio and model watermarking are included where they show useful practice. Landmark classical ECC+watermark work from before 2020 (Bastug & Sankur 2004 LDPC, Rey et al. 2003 turbo-BCH, Abrardo & Barni 2005 soft turbo, Hirata et al. 2017 PEG-LDPC, and others) is already covered in `research_notes/Modern blind image watermarking/embedding_decoding.md` §7 and is not repeated here.

How the sources were checked:
- **"(full text)"**: the arXiv HTML was downloaded and searched for keywords locally, so the quotes are verbatim.
- **"(abstract)"**: only the abstract or landing page was read.
- **"(snippet)"**: seen only in a search-engine summary. Lower confidence.
- **Citation counts** are OpenAlex `cited_by_count` values retrieved on 2026-11-04. OpenAlex splits arXiv preprints from their published versions and indexes with a lag, so counts for arXiv-only records are **lower bounds** and probably well below Google Scholar. Google Scholar and IEEE Xplore were not queried because they block automated access.

User context: Meta ChunkySeal at 1024 bits with no ECC gets all bits right on 13% of attacked frames, and a 256-bit slice right on 42.5%. 5G LDPC at rate 1/2 recovers 180 of 180 IDs.

---

## Q1. Which recent (2020–2026) papers focus on ECC or channel coding for watermarking, and what do they claim?

### Takeaway
ECC for watermarking is an active but thin and scattered niche, not a mainstream topic. In images, most neural watermark papers either ignore ECC or bolt on BCH as an afterthought: StegaStamp, InvisMark and TrustMark use BCH. Meta's Video Seal, WAM and ChunkySeal papers do not mention ECC at all. Since 2024 the work that actually focuses on coding has clustered in a few places:
- **In-generation diffusion watermarks:** PRC/LDPC (ICLR 2025), Gaussian Shading++ (soft LLRs, 2025) and Gaussian Shannon (LDPC plus majority vote, CVPR 2026).
- **A handful of 2025–2026 preprints:** NAWE (polar with CRC-aided list decoding, Sept 2026), a payload-matched BCH study on MBRS (Zenodo, Sept/Oct 2026), README (2048-bit signatures, 2025) and HMARK (BCH, 2025).
- **LLM text watermarking:** Reed–Solomon (Qu et al., USENIX Security 2025), LDPC (Chao et al. 2024), BCH (BREW 2026) and soft-decision BCH (CORE-BREW 2026).

I found no paper that applies the same set of modern codes (5G LDPC, polar, turbo, BCH, RS) on top of both classical and neural post-hoc image watermarks at matched quality.

### Cited Findings

**Neural post-hoc image watermarks that use ECC as an add-on**
- **StegaStamp (Tancik et al., CVPR 2020; 531 OpenAlex citations).** Carries 100 raw bits. The system "robustly retrieves 56 bit hyperlinks after error correction", using BCH. Its real-world tables report the percentage of bits recovered, not the message success rate (full text). — [arXiv 1904.05343](https://arxiv.org/abs/1904.05343)
- **Distortion Agnostic Deep Watermarking (Luo et al., Google, CVPR 2020; 216 citations).** An early *learned* channel code. "Robustness … comes from two sources: adversarial training and channel coding." The channel coder is "two fully connected layers with 512 units each", trained against BSC noise because "it is impossible to know the true channel distortion model" (full text). — [arXiv 2001.04580](https://arxiv.org/abs/2001.04580)
- **InvisMark (Xu et al., Microsoft, WACV 2025; 30 citations).** Embeds 256 bits. The paper says it "introduce[s] watermark decoding success rate as another key metric, representing the probability of complete watermark recovery with error corrections… vital for content provenance applications, where accurate decoding of all bits is essential for database retrieval". With BCH and 128-bit UUIDs it reports "a perfect 100% success rate across various transformations" and over 90% elsewhere (full text). — [arXiv 2411.07795](https://arxiv.org/abs/2411.07795)
- **TrustMark (Bui et al., Adobe; arXiv 2023; 18 citations, venue not verified).** The paper evaluates with bit accuracy only (full text). The repository offers four BCH schemas over the 100-bit payload (BCH_SUPER, BCH_5, BCH_4, BCH_3) and reserves version bits: "two reserved (unused) bits, and two bits encoding an integer value 0-3 that specifies the data schema". — [arXiv 2311.18297](https://arxiv.org/abs/2311.18297); [adobe/trustmark README](https://github.com/adobe/trustmark)
- **Meta's recent models do not mention ECC at all.** Keyword searches of the full texts of Video Seal (arXiv 2412.09492), Watermark Anything (2411.07231) and the ChunkySeal capacity paper (2510.12812) found no mention of error-correcting codes, BCH, LDPC or polar codes. The ChunkySeal paper's only "channel coding" sentence describes classical work: "watermarking is modeled as a channel coding problem over an idealized Euclidean signal space… this assumption diverges sharply from the realities of digital images" (full text). — [arXiv 2510.12812](https://arxiv.org/abs/2510.12812); [arXiv 2412.09492](https://arxiv.org/abs/2412.09492); [arXiv 2411.07231](https://arxiv.org/abs/2411.07231)

**Papers whose contribution is the coding itself (images)**
- **PRC watermark (Gunn, Zhao, Song, ICLR 2025; OpenAlex 9, an undercount).**
  - Starts diffusion from initial latents chosen by a pseudorandom error-correcting code.
  - "As our PRC, we use the LDPC construction from Christ & Gunn (2024), modified to handle soft decisions… values of larger magnitude are more reliable."
  - Message decoding uses "belief propagation with ordered statistics decoding" from Roffe's `ldpc` package.
  - "The decoder is slower and less robust than the detector."
  - Encodes 512 bits robustly and up to 2500 bits without removal attacks (full text). — [arXiv 2410.07369](https://arxiv.org/abs/2410.07369)
  - The underlying primitive is Christ & Gunn, "Pseudorandom Error-Correcting Codes", CRYPTO 2024 (20 citations). — [ePrint 2024/235](https://eprint.iacr.org/2024/235)
  - An attack on it exists: "Cryptanalysis of LDPC-Based Pseudorandom Error-Correcting Codes" (snippet). — [arXiv 2512.17310](https://arxiv.org/abs/2512.17310)
- **Gaussian Shading (Yang et al., CVPR 2024; 98 citations).** Carries 256 bits through repetition plus a stream cipher, with no algebraic ECC. "Replicate the watermark … times" (full text). — [arXiv 2404.04956](https://arxiv.org/abs/2404.04956)
- **Gaussian Shading++ (2025).** Adds a PRC channel that "serves as the watermark header, encoding the seed". It also adds "a novel soft decision decoding strategy" for the repetition channel: per-bit LLRs aggregated from repeated instances, "near-optimal … MAP estimation under the assumption of independent Gaussian noise" (full text). — [arXiv 2504.15026](https://arxiv.org/abs/2504.15026)
- **Gaussian Shannon (Zhang, Huang, Zhang; CVPR 2026, Findings track per the CVF URL "CVPR2026F"; arXiv Mar 2026).**
  - Motivation: "existing methods rely on threshold-based detection, which only supports fuzzy matching and cannot recover structured watermark data bit-exactly."
  - Design: a (3,4)-regular LDPC code plus majority voting over replicas, at 256 bits.
  - Its primary metric is "TPR at 100% bit accuracy (TPR@BitAcc.100%)".
  - Results with noise, on SD 1.4/2.0/2.1: Gaussian Shannon 0.968/0.966/0.965; PRC watermark 0.855/0.827/0.827; Gaussian Shading 0.399/0.387/0.381; Stable Signature 0.173–0.182; DwtDctSvd 0.135/0.099/0.062; DwtDct 0.020/0.016/0.014 (full text, Table 1). — [arXiv 2603.26167](https://arxiv.org/abs/2603.26167)
- **Hu et al., Frontiers in Physics, published 20 Jan 2026.**
  - Compares BCH, LDPC and LDPC+BCH, each with a repetition layer, for diffusion latent watermarks at 256 bits.
  - LDPC uses min-sum with LLRs.
  - Mean bit accuracy: BCH 0.9641, LDPC+BCH 0.9559, LDPC 0.9540.
  - Reports bit accuracy only, with no exact-recovery rate. Reed–Solomon and convolutional codes were not tested (abstract and full page via WebFetch). — [Frontiers 10.3389/fphy.2025.1750515](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2025.1750515/full)
- **Evsutin, Ivanov, Dzhanashia (IEEE Access 2024; 4 citations).** Template embedding, neural-network extraction and polar codes. Carries "650 to 1600 bits for high-definition images (1920-by-1080)" at PSNR 39.66 with "small probability (0.01) of erroneous extraction" after Facebook, VK, Telegram, WhatsApp and others (abstract via OpenAlex). — [doi 10.1109/ACCESS.2024.3446489](https://doi.org/10.1109/access.2024.3446489)
- **NAWE (Chaban, Kinakh, Rouzaire, Voloshynovskiy, Univ. Geneva; arXiv 22 Sep 2026).** The closest recent work to the user's design:
  - Signal path: classical periodic carrier with a frozen neural denoiser for host suppression, polar code with CRC, "CRC-aided successive-cancellation list decoding", "known pseudorandom synchronization vector" cells, and "registered repetitions support soft decoding".
  - Metrics: it targets "zero-bit-error recovery" and reports word error rate (WER) and BER "at matched embedding PSNR" against TrustMark, SSL, PixelSeal and WAM, over a 156-arm benchmark across 34 attack families.
  - It keeps each competitor's own coding: "The comparison retains the systems' different payloads and coding… equal PSNR does not equalize information rate, coding gain, or perceptual visibility." It does not put one ECC on top of all systems.
  - Limitations: filtering and noise (full text). — [arXiv 2609.25972](https://arxiv.org/abs/2609.25972)
- **"When Does Error Correction Help? A Payload-Matched Study of Post-Hoc and End-to-End ECC in Neural Image Watermarking" (Yanze Li, Sun Yat-sen Univ.; Zenodo v1 26 Sep 2026, v2 7 Oct 2026; not peer-reviewed).**
  - Setup: MBRS backbone, 36-bit payload, BCH and Hamming(7,4), hard decision.
  - Main claims:
    - "hard-decision decoding does not fail — it miscorrects", corrupting κ = 0.482 ± 0.029 of block message bits;
    - the outcome is governed by the correction radius θ = t/n, with a closed-form break-even at 18.8% raw BER for Hamming(7,4);
    - "comparisons rarely control for the payload the code itself consumes".
  - v2 retracts part of v1's headline. The 4.2× advantage of post-hoc BCH over integrated BCH at JPEG Q50 (5.2% vs 21.9%) "is largely a property of the training mixture". Pool-matched retraining closes it to 5.4% vs 5.2%.
  - BatchNorm left in train mode inflates noise robustness by 2.4–6.7× (abstract, Zenodo API). — [Zenodo 22970405 (v1)](https://zenodo.org/records/22970405); v2 is record 23201193 (same concept DOI family).
- **README (Choi et al., arXiv Jul 2025).**
  - Goal: 2048-bit digital signatures in one image, using "cropping-based capacity scaling" and ERPA, a custom error-localization module built on "Distinct Circular Subsum Sequences". It does not use a standard ECC.
  - It "introduce[s] a new metric, the Zero Bit Error Image Rate (Z.B.I.R)… proportion of images from which all embedded bits are recovered without any error".
  - Z.B.I.R rises "from 1.2% to 86.3%" (full text). — [arXiv 2507.04495](https://arxiv.org/abs/2507.04495)
- **HMARK (arXiv Nov 2025).** Multi-bit watermark for diffusion models with BCH integration via python-bchlib. BCH(31,8) and BCH(31,16) lift bit accuracy above 90% under fine-tuning (full text and snippet). — [arXiv 2512.00094](https://arxiv.org/abs/2512.00094)
- **QRMark (Zhong et al., Rice/UIUC/UMD/Cisco; arXiv 2509.02447, cs.DC).** Reed–Solomon over tiles to recover the accuracy lost when detecting Stable Signature tile by tile. The goal is detection throughput, not capacity (full text). — [arXiv 2509.02447](https://arxiv.org/abs/2509.02447)
- **DREW (arXiv Jun 2024).** Combines ECC-coded cluster keys with TrustMark and embedding retrieval. It argues that "the volume of information that can be reliably embedded as a watermark is limited…, restricting the inclusion of sufficient redundant bits for effective error correction" (full text). — [arXiv 2406.02836](https://arxiv.org/abs/2406.02836)
- **CCMark (ICLR 2025).** Uses polar codes for high-payload watermarking of *generative models* (network watermarking, not images) (snippet). — [ICLR 2025 virtual page](https://iclr.cc/virtual/2025/35729)

**LLM text watermarking: a faster-moving ECC sub-literature**
- **Qu et al., "Provably Robust Multi-bit Watermarking for AI-generated Text" (USENIX Security 2025; 15 citations on the arXiv record).**
  - Code: Reed–Solomon, with a section titled "Background on Reed-Solomon codes".
  - Metric: "match rate… proportion of generated texts that can exactly extract embedded message without error".
  - Result: 97.6% for a 20-bit message in 200 tokens, against 49.2% for Yoo et al. (full text). — [arXiv 2401.16820](https://arxiv.org/abs/2401.16820)
- **Chao et al., "Watermarking Language Models with Error Correcting Codes" (arXiv 2024; 5 citations; venue not verified).** "We primarily use the popular low-density parity-check (LDPC) code", with a no-ECC "one-to-one code" baseline. Evaluation uses p-values (full text). — [arXiv 2406.10281](https://arxiv.org/abs/2406.10281)
- **Yoo et al., MPAC (NAACL 2024; 33 citations).** Has no ECC. It uses confidence-ordered list decoding and says "applying other techniques from coding theory such as error correction codes… to MPAC is straightforward" (full text). — [arXiv 2308.00221](https://arxiv.org/abs/2308.00221)
- **BREW (Kim et al., arXiv 2605.00348, 2026).** Block-wise BCH "designated codeword" embedding, with detection that "verifies that a recovered codeword equals the designated codeword that was actually embedded in that block". It reports a message-level exact match rate and notes MPAC's "49.2% match rate for 32-bit" (full text). — [arXiv 2605.00348](https://arxiv.org/abs/2605.00348)
- **CORE-BREW (Kim, Kim, Kim, DGIST; arXiv Jun 2026, v2 Sep 2026).**
  - Its premise: "Existing ECC-based LLM watermarks rely on hard-decision decoding, discarding token-level reliability information."
  - It calibrates a constant hit rate to obtain closed-form per-token LLRs, then applies soft-decision list decoding, with a hard-decision ablation. It cites Chase and ordered-statistics decoding for BCH.
  - The abstract gives no numbers (full text). — [arXiv 2606.24163](https://arxiv.org/abs/2606.24163)

**Audio**
- **WavMark (Chen et al., 2023).** 32 bits per 1-second segment. AudioMarkBench describes it as embedding "a preset synchronization bitstring s_sync together with the watermark" for localization (full text and snippet). — [arXiv 2308.12770](https://arxiv.org/abs/2308.12770); [AudioMarkBench arXiv 2406.06979](https://arxiv.org/abs/2406.06979)

### Inferences
- Before 2024, ECC in neural image watermarking meant BCH at 100–256 bits used as a convenience layer: StegaStamp, InvisMark, TrustMark. Since 2024, coding-centric work has concentrated in *in-generation* diffusion watermarks (PRC, Gaussian Shading++, Gaussian Shannon, Frontiers 2026), where the "channel" is DDIM inversion error. Post-hoc neural watermarks, which is the user's ChunkySeal case, have far less coding-focused work.
- The three 2026 items closest to the user's study each cover only part of the design space:
  - NAWE has polar codes, matched PSNR and WER, but only its own scheme carries the code.
  - The Li (Zenodo) study has a payload-matched ECC comparison, but only BCH and Hamming, hard decision, 36 bits and the MBRS backbone.
  - Gaussian Shannon uses LDPC with an exact metric, but only for in-generation diffusion watermarks.
- None of these combine:
  - modern capacity-approaching codes (5G LDPC, polar with CRC-SCL, turbo) against BCH and RS;
  - classical and neural post-hoc backbones;
  - hundreds to 1024 bits;
  - matched wPSNR;
  - blind versus semi-blind decoding.
- LLM text watermarking is ahead of images on coding rigour. It already has RS, LDPC and BCH, exact "match rate" metrics, designated-codeword verification and LLR soft decoding (CORE-BREW). Image work could borrow these framings directly.

### Gaps
- I could not find the "published integrated model" (36-bit, BCH integrated into MBRS training) that the Zenodo study re-evaluates. Its abstract does not name it.
- I did not verify TrustMark's per-schema data-bit and correction counts (they are in `python/CONFIG.md`, not read), its publication venue, or how `wm_present` is computed.
- NAWE's exact payloads, WER numbers per competitor and polar list size were not extracted. The paper is a fresh preprint and the code is "available on acceptance".
- CCMark details come from a snippet only.
- No Google Scholar citation counts were collected, so OpenAlex counts for arXiv-only works (PRC, WAVES, Video Seal, WAM) are likely large undercounts.

---

## Q2. How do benchmarks and survey/SoK papers evaluate message recovery? Does any benchmark require exact recovery of a multi-bit ID?

### Takeaway
The major image-watermark benchmarks (WAVES, ICML 2024; W-Bench, ICLR 2025; MarkDiffusion, JMLR 2026) all use **detection TPR at a fixed low FPR** as the headline metric, with bit accuracy as a secondary or reference number. W-Bench says outright that it excludes ECC. Meta's model papers report bit accuracy and log10 p-values. SynthID-Image defines "code accuracy" (the whole payload correct) but publishes only bit accuracy. Exact-recovery metrics appear only in individual method papers, and several of those present the metric as *new*:
- InvisMark's "decoding success rate" (2024);
- README's "Z.B.I.R" (2025);
- Gaussian Shannon's "TPR@BitAcc100%" (2026);
- NAWE's WER (2026);
- the LLM papers' "match rate".

**I found no benchmark that requires exact recovery of a multi-bit ID.**

### Cited Findings
- **WAVES (An et al., ICML 2024; OpenAlex 12, an undercount).**
  - Headline metric is TPR@0.1%FPR. It critiques bit accuracy for five reasons, including "Insensitivity to error distribution… certain types of errors (like clustered errors) might be more detrimental" and "Threshold dependency".
  - Its comparison of earlier evaluations shows that StegaStamp and Stable Signature were judged by "bit accuracy" and Tree-Ring by "TPR@1%FPR".
  - It names ECC as a defence direction: "Incorporating redundant bits. This technique, known as error correction coding, can help reconstruct the original message even when parts of the watermark are corrupted" (full text). — [arXiv 2401.08573](https://arxiv.org/abs/2401.08573)
- **W-Bench / VINE (Lu et al., ICLR 2025; 21 citations).**
  - "We primarily focus on TPR@0.1%FPR and TPR@1%FPR as our main metrics… we also provide bit accuracy and AUROC for reference."
  - "**all reported baseline bit accuracies do not include error correction methods, such as BCH… which can be applied to all watermarking models**."
  - SSL "often produc[es] bit accuracy exceeding 0.7 for unwatermarked images. Therefore, bit accuracy and AUROC alone are insufficient" (full text). — [arXiv 2410.18775](https://arxiv.org/abs/2410.18775)
- **MarkDiffusion (THU-BPM; arXiv Sep 2025; JMLR vol. 27, 2026).** The results table uses "Detectability (TPR@FPR=1%)", robustness as an F1-score, and FID and CLIP-T. Users "can plug in alternative detection metrics (e.g., p-value)". There is no exact-message metric (full text). — [arXiv 2509.10569](https://arxiv.org/abs/2509.10569); [JMLR v27](https://jmlr.org/papers/v27/25-2553.html)
- **Video Seal (Meta, arXiv Dec 2024).**
  - "The main metric to evaluate the robustness of the watermarking in a multi-bit setting is the bit accuracy… The biggest issue with bit accuracy is that it is agnostic to the number of bits being hidden."
  - It adds two measures: the log10 p-value of a binomial test against random bits, and an "expected capacity" that treats each bit as a BSC with the observed error rate (full text). — [arXiv 2412.09492](https://arxiv.org/abs/2412.09492)
- **ChunkySeal (Petrov, Fernandez, Souček, Elsahar; arXiv Oct 2025).** At 1024 bits and 45.32 dB PSNR it reports bit accuracy only:
  - 99.15% overall;
  - 98.27% under rotation of at most 10°;
  - 98.25% under crop;
  - 98.79% under JPEG Q50–80.

  No exact-message metric was found (full text via WebFetch). — [arXiv 2510.12812](https://arxiv.org/abs/2510.12812)
- **Watermark Anything (Meta, ICLR 2025).** Reports bit accuracy plus TPR/FPR. For baselines that lack a detector, "we hide 48 bits and reserve 16 bits for detection, and flag an image as watermarked if it has strictly less than two bits incorrectly decoded" (full text, Table 2). — [arXiv 2411.07231](https://arxiv.org/abs/2411.07231)
- **SynthID-Image (Google DeepMind, arXiv Oct 2025).**
  - "Bit accuracy does not explicitly measure what we might be interested in, which is how often we get the entire payload right, i.e., code accuracy… Code accuracy generally degrades with larger payload size and degrades more quickly with challenging transformations than bit accuracy."
  - "While many approaches allow multi-bit watermarks, it is often neglected how a multi-bit payload is best used."
  - On Yang et al. 2024: "a simple integer user identifier is encoded in the payload, without any redundancy or additional logic."
  - The published comparison table (SynthID-O at 136 bits against InvisMark, StegaStamp, TrustMark, Video Seal and WAM) reports **bit accuracy only** (full text). — [arXiv 2510.09263](https://arxiv.org/abs/2510.09263)
- **Survey (Cao, Li, Zhang, Ni, Lu, Queen's Univ.; arXiv 2510.02384 v2, Mar 2026).** Table 4 lists bit accuracy ("BA", about 10 methods) and TPR@εFPR (about 14 works) under "Detection and Attribution". No exact or word-level metric was seen (WebFetch, partial read). — [arXiv 2510.02384](https://arxiv.org/abs/2510.02384)
- **SoK: Watermarking for AI-Generated Content (Zhao et al., IEEE S&P 2025; 38 citations).** Discusses PRCs for text and images. Its keyword search found no BCH, LDPC or RS evaluation guidance (full text). — [arXiv 2411.18479](https://arxiv.org/abs/2411.18479)
- **Method papers that report exact recovery:**
  - InvisMark: "decoding success rate". — [2411.07795](https://arxiv.org/abs/2411.07795)
  - README: Z.B.I.R, "a new metric". — [2507.04495](https://arxiv.org/abs/2507.04495)
  - Gaussian Shannon: TPR@BitAcc100% "as the primary evaluation metric". — [2603.26167](https://arxiv.org/abs/2603.26167)
  - NAWE: WER, "at least one wrong bit or a decoding failure constitutes a word error". — [2609.25972](https://arxiv.org/abs/2609.25972)
  - Qu et al.: "match rate". — [2401.16820](https://arxiv.org/abs/2401.16820)
  - BREW: "Message-Level Exact Match Rate" (appendix D.9). — [2605.00348](https://arxiv.org/abs/2605.00348)
- **ADD (arXiv Apr 2026).** Treats per-bit accuracy as the standard multi-bit metric so it can compare with prior work, and notes that perfect decoding is all-or-nothing and gets harder with message length (snippet). — [arXiv 2604.11491](https://arxiv.org/abs/2604.11491)

### Inferences
- The field has two evaluation cultures:
  - detection, with TPR at a fixed FPR (benchmarks);
  - multi-bit attribution, with bit accuracy (model papers).

  Neither measures what a provenance ID needs: *exact ID recovery together with a controlled false-ID or false-accept rate*. A paper that reports exact-ID rate, undetected-error (wrong-ID) rate and detection TPR at a fixed FPR, for each code and backbone at matched wPSNR, would fill a recognised hole. SynthID-Image names the metric, and W-Bench explicitly excludes ECC.
- The user's ChunkySeal numbers fit SynthID-Image's statement that code accuracy degrades faster than bit accuracy. A back-of-envelope check (my arithmetic, not sourced):
  - with independent errors at ChunkySeal's published average bit accuracy (99.15%), all 1024 bits would be right with probability 0.9915^1024 ≈ 0.02%, and a 256-bit slice with probability ≈ 11%;
  - the observed 13% and 42.5% are far higher, so errors must be concentrated in a minority of "bad" frames (bursty per image), not spread uniformly;
  - this is exactly the clustered-error case WAVES warns bit accuracy hides;
  - it also means ECC gains will depend on the per-image error distribution, so a per-frame BER histogram is worth reporting.
- **Statistical note for publication (inference).** 180 of 180 successes gives a 95% upper bound of about 3/180 ≈ 1.7% on the ID failure rate (rule of three). Reviewers used to TPR@0.1%FPR will expect larger trial counts, or a reported confidence interval, for claims of near-zero failure.

### Gaps
- I did not read the full WAVES or W-Bench tables for per-method values. AudioMarkBench and any Meta "OmniSeal"-style benchmark were not checked in full.
- The Cao et al. survey's §5.3 (Detectability) was only partly read, so whether it mentions word accuracy is unconfirmed.

---

## Q3. Is there prior work on semi-blind decoding (known header or tag bits), known-bit-aided decoding, or soft-decision decoding that uses neural extractor logits as LLRs?

### Takeaway
Pieces of this exist, but I found no work that combines them for post-hoc neural image watermarks. Specifically:
- **Known-bit detection** is common: reserved detection bits in WAM's baseline protocol, a fixed key message with a binomial test (Stable Signature, Video Seal p-values), TrustMark's schema bits, WavMark's sync bitstring, NAWE's known sync cells, BREW's designated-codeword check.
- **Soft-decision decoding** exists for *in-generation* diffusion watermarks (PRC with soft BP and OSD; Gaussian Shading++ with LLR aggregation; LDPC min-sum in Frontiers 2026), for classical schemes (NAWE soft polar SCL; pre-2010 soft turbo/LDPC), and for LLM text (CORE-BREW, 2026).

I found **no paper that feeds a post-hoc neural extractor's logits (e.g., Video Seal or ChunkySeal) as LLRs into an LDPC or polar decoder**, and none that uses known header bits both to detect *and* as pinned bits inside the ID decoder.

### Cited Findings
- **Known reserved detection bits (WAM, ICLR 2025).** For baselines without a detector, "we hide 48 bits and reserve 16 bits for detection, and flag an image as watermarked if it has strictly less than two bits incorrectly decoded" (full text). — [arXiv 2411.07231](https://arxiv.org/abs/2411.07231)
- **Fixed known message with a binomial test.** SynthID-Image describes Yang et al. (2024) and Fernandez et al. (2023, Stable Signature) as selecting "a random but fixed payload… and make a detection decision by thresholding on the number of matching bits… if the reference payload is not available, this test is not applicable" (full text). — [arXiv 2510.09263](https://arxiv.org/abs/2510.09263). Video Seal reports the log10 p-value of the matching-bit count under a Bernoulli(0.5) null (full text). — [arXiv 2412.09492](https://arxiv.org/abs/2412.09492)
- **Structured or header bits.**
  - TrustMark: two schema bits and two reserved bits inside the 100-bit payload. — [adobe/trustmark](https://github.com/adobe/trustmark)
  - Gaussian Shading++: its PRC channel "serves as the watermark header, encoding the seed" (full text). — [arXiv 2504.15026](https://arxiv.org/abs/2504.15026)
  - WavMark: a preset synchronization bitstring embedded with the payload (snippet/full text). — [AudioMarkBench 2406.06979](https://arxiv.org/abs/2406.06979)
- **Known sync bits with soft polar decoding (NAWE, Sep 2026).** "The key/nonce pair also generates the known pseudorandom synchronization vector… These additional bits occupy dedicated cells… they are not user information or Polar parity bits." They are used to "refine the affine estimate, and validate alignment". Decoding is CRC-aided SCL on "soft coded symbols after removal of synchronization cells" (full text). — [arXiv 2609.25972](https://arxiv.org/abs/2609.25972)
- **Designated-codeword (known-codeword) verification in text (BREW 2026).** Detection checks that "a recovered codeword equals the designated codeword… thereby suppressing spurious matches that inflate FPR" (full text). — [arXiv 2605.00348](https://arxiv.org/abs/2605.00348)
- **Soft decoding in images.**
  - PRC watermark: LDPC "modified to handle soft decisions", decoded with BP and OSD. — [arXiv 2410.07369](https://arxiv.org/abs/2410.07369)
  - Gaussian Shading++: per-bit LLRs from repeated instances, "near-optimal soft decision decoding… MAP". — [arXiv 2504.15026](https://arxiv.org/abs/2504.15026)
  - Frontiers 2026: LDPC min-sum with LLRs, though BCH-repetition beat it on bit accuracy. — [Frontiers](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2025.1750515/full)
- **Soft decoding in text (CORE-BREW 2026).** "Most ECC-based LLM watermarking methods rely on hard decisions… Qu et al. (2025); Chao et al. (2024); Kim et al. (2026)". It contributes closed-form per-token LLRs and soft list decoding (full text). — [arXiv 2606.24163](https://arxiv.org/abs/2606.24163)
- **Hard decision fails silently.** Bounded-distance BCH or Hamming decoding beyond the correction radius "silently returns a different codeword", corrupting about 48% of the block's message bits (Zenodo 2026). — [Zenodo 22970405](https://zenodo.org/records/22970405)
- **Learned channel decoders.** DADW (CVPR 2020) trains an FC channel encoder and decoder on BSC noise (full text). — [arXiv 2001.04580](https://arxiv.org/abs/2001.04580). An LLR-based search turned up only communications papers that use a deep demapper to produce soft bits for a standard decoder, not watermark papers (search results).
- **Pre-2020 precedent** (already in the user's notes): Abrardo & Barni (2005) turbo with soft inner decoding; Martinez Noriega (audio) QIM plus LDPC with LLRs from an MP3 noise model. — see `research_notes/Modern blind image watermarking/embedding_decoding.md` §7.

### Inferences
- In coding terms, "semi-blind" decoding with known header bits is code shortening, or decoding with frozen or known bits: known positions get infinite-reliability LLRs. NAWE's polar frozen bits plus known sync cells and BREW's designated codeword are close cousins. The *coding* idea is therefore not new. The publishable part is empirical:
  - how much a known tag improves the exact-ID rate and the false-ID rate at fixed FPR for each backbone;
  - how to split bits between header and parity at a fixed watermark budget.

  (The claim that this matches shortening or 5G NR filler-bit handling comes from general coding-theory background and is not sourced in this session.)
- Using neural extractor logits as LLRs is the most clearly unclaimed piece for post-hoc neural image watermarks. A finding would be valuable if logits are miscalibrated, for example over-confident wrong bits under geometric attacks, so that soft decoding needs temperature or calibration. LLM work (CORE-BREW) had to *engineer* calibration ("constant hit rate") to get usable LLRs, which hints that calibration is the crux.
- The Zenodo "miscorrection" result argues for reporting **undetected-error (wrong ID) rates** separately from failures. LDPC and polar with CRC flag failures (syndrome or CRC); bounded-distance BCH mostly miscorrects. That is a concrete, defensible axis of comparison.

### Gaps
- I did not search IEEE Xplore or Google Scholar for "pilot bits", "reference bits" or "training sequence" in classical image watermarking from 2020 to 2026. Classical semi-blind schemes may use known pilots for channel estimation, but I found no specific modern instance beyond print-and-scan pilot patterns (search snippet only).
- I found no source on calibration of neural watermark extractor logits.

---

## Q4. Rough bibliometrics: how many papers match ECC + image watermarking per year, what is the trend, and which works are most cited?

### Takeaway
ECC-related image watermarking is a **small, flat-share niche**. OpenAlex counts 11–36 papers per year from 2020 to 2026 whose title or abstract mention image watermarking plus ECC terms, which is **about 1–2% of image-watermarking papers in every year since 2015**. Absolute counts rose in 2025–2026 (26 and 36), but only in step with the overall surge in watermarking papers (1,293 and 1,927). Deep-learning watermarking plus ECC is smaller still, about 2–17 per year, with a recent uptick (11 in 2025, 17 in 2026). The steepest relative growth is in **LLM text watermarking plus ECC** (1 → 3 → 6 → 18 for 2023–2026). Most-cited works are dominated by papers where ECC is a side component (StegaStamp 531, DADW 216) or by medical/dual watermarking.

### Cited Findings
All counts come from the OpenAlex API (`title_and_abstract.search`, `group_by=publication_year`), retrieved on 2026-11-04. 2026 is a partial year (to early November) and subject to indexing lag. — [OpenAlex API](https://api.openalex.org/works)

| Year | A: image wm + ECC terms | F: all image wm | A/F | G: deep/neural wm + ECC | D: deep/neural image wm | B: wm + LDPC | C: wm + polar code | D2: wm + BCH/RS | E: wm + turbo | T: LLM text wm + ECC | S: wm + soft decision/LLR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2015 | 18 | 1168 | 1.5% | – | 37 | 4 | – | 14 | 1 | – | 1 |
| 2017 | 22 | 1019 | 2.2% | 2 | 26 | 4 | – | 14 | 1 | – | 3 |
| 2019 | 19 | 994 | 1.9% | 1 | 72 | 1 | – | 6 | – | – | 2 |
| 2020 | 12 | 882 | 1.4% | 4 | 92 | 3 | 1 | 7 | 3 | – | 2 |
| 2021 | 18 | 966 | 1.9% | 2 | 99 | 2 | 1 | 6 | 4 | – | 1 |
| 2022 | 16 | 889 | 1.8% | 0 | 124 | 3 | 1 | 6 | 2 | – | 0 |
| 2023 | 11 | 1029 | 1.1% | 5 | 228 | 1 | 2 | 3 | 2 | 1 | 0 |
| 2024 | 13 | 1052 | 1.2% | 2 | 266 | 2 | 3 | 5 | 1 | 3 | 0 |
| 2025 | 26 | 1293 | 2.0% | 11 | 414 | 6 | 1 | 15 | 1 | 6 | 5 |
| 2026* | 36 | 1927 | 1.9% | 17 | 486 | 4 | 4 | 29 | 4 | 18 | 6 |

Exact query strings (OpenAlex boolean, title and abstract; columns B–E and S cover all modalities):
- A: `(watermark OR watermarking) AND image AND ("error correcting" OR "error-correcting" OR "error correction" OR "channel coding" OR "channel code")`
- F: `(watermark OR watermarking) AND image`
- G: `(watermark OR watermarking) AND ("deep learning" OR neural OR "deep network") AND ("error correcting" OR "error-correcting" OR "error correction" OR BCH OR LDPC OR "polar code")`
- D: `(watermark OR watermarking) AND image AND ("deep learning" OR neural OR "deep network" OR diffusion)`
- B: `… AND (LDPC OR "low-density parity-check" OR "low density parity check")`
- C: `… AND ("polar code" OR "polar codes")`
- D2: `… AND (BCH OR "Reed-Solomon" OR "Reed Solomon")`
- E: `… AND ("turbo code" OR "turbo codes")`
- T: `… AND ("language model" OR LLM OR "generated text") AND (ECC terms incl. BCH/LDPC/RS)`
- S: `… AND ("soft decision" OR "soft-decision" OR "log-likelihood ratio" OR "soft decoding")`

Totals and the Semantic Scholar cross-check:
- With ECC families added to A's terms, 168 image-watermarking papers match for 2020–2026.
- With the diffusion term added to G, 56 deep/neural-plus-ECC papers match for 2020–2026.
- Semantic Scholar bulk search (`watermark* + ("error correcting" | "error correction" | BCH | LDPC | "polar code" | "Reed-Solomon")`, all modalities) returned 23 (2019), 25 (2020), 25 (2021), 19 (2023) and 28 (2024). 2018, 2022, 2025 and 2026 were rate-limited (HTTP 429) and not obtained. This is consistent in magnitude with OpenAlex. — [Semantic Scholar API](https://api.semanticscholar.org/graph/v1/paper/search/bulk)

Most-cited 2020–2026 works matching the ECC queries (OpenAlex, 2026-11-04):
- **Distortion Agnostic Deep Watermarking (CVPR 2020): 216.** Learned channel code. — [doi](https://doi.org/10.1109/cvpr42600.2020.01356)
- **Robust High-Capacity Watermarking over OSN Shared Images (IEEE TCSVT 2020): 110–111.** A **false positive for ECC focus**: its abstract says it is robust "even without any error correcting codes (ECC)". — [doi](https://doi.org/10.1109/tcsvt.2020.2998476)
- Medical and dual-watermarking papers with incidental ECC: 30–78 each (e.g., IEEE TDSC 2022, 78). — [OpenAlex query results](https://api.openalex.org/works)
- **InvisMark (WACV 2025): 30.** — [doi](https://doi.org/10.1109/wacv61041.2025.00098)
- **StegaStamp (CVPR 2020): 531.** It uses BCH but does not mention it in its abstract, so the keyword query misses it. — [doi](https://doi.org/10.1109/cvpr42600.2020.00219)

Citation counts for other reference points (OpenAlex; the arXiv records are undercounts):

| Paper | OpenAlex citations |
|---|---|
| MBRS (ACM MM 2021) | 281 |
| Stable Signature (ICCV 2023) | 251 |
| Gaussian Shading (CVPR 2024) | 98 |
| SoK (S&P 2025) | 38 |
| MPAC (NAACL 2024) | 33 |
| W-Bench (arXiv) | 21 |
| PRC codes (CRYPTO 2024) | 20 |
| TrustMark (arXiv) | 18 |
| Qu et al. (arXiv) | 15 |
| WAVES (arXiv) | 12 |
| SynthID-Image | 10 |
| PRC watermark (arXiv) | 9 |
| Video Seal (arXiv) | 8 |
| WAM (arXiv) | 8 |
| Chao et al. | 5 |
| Polar-codes Access 2024 | 4 |
| ChunkySeal paper | 2 |
| DREW | 2 |
| MarkDiffusion (arXiv) | 1 |
| Gaussian Shannon (CVPR 2026) | 0 |

— [OpenAlex API](https://api.openalex.org/works)

### Inferences
- **Trend.** The *share* is flat at about 1–2% for a decade, so ECC-in-watermarking is not rising as a fraction. In absolute terms, 2025–2026 roughly doubled over 2020–2024, driven by the generative-AI watermarking boom and by the diffusion and LLM sub-areas. Polar (1–4 per year), LDPC (1–6) and turbo (1–4) remain tiny. The jump in BCH/RS (15 and 29 in 2025–2026) is mostly in medical, QR-code and authentication papers, judging by the top-cited list.
- Soft-decision/LLR watermarking papers were nearly absent from 2022 to 2024 (0 per year) and reappear in 2025–2026 (5–6 per year). That matches the qualitative picture: PRC, Gaussian Shading++, Frontiers and CORE-BREW.
- Keyword counts overstate the field. The second most-cited "ECC" hit explicitly does *without* ECC, and many hits only mention Hamming codes for fragile or tamper watermarks. The *true* number of papers whose contribution is coding for robust multi-bit image watermarks is probably a few per year.

### Gaps
- Google Scholar and IEEE Xplore counts were not collected because of automated-access blocks. Semantic Scholar was only partly collected (rate limits). I did not query arXiv listings by year separately.
- Keyword search cannot separate "ECC is the contribution" from "ECC is mentioned"; no manual relevance coding was done beyond the top-cited lists.

---

## Q5. What gaps do surveys and recent papers state explicitly (capacity limits, exact recovery, coding at matched quality)?

### Takeaway
Recent sources state, explicitly and repeatedly:
- ECC is underused because neural payloads are small;
- multi-bit payloads are rarely structured or used well;
- bit accuracy hides what provenance needs (whole-payload correctness);
- ECC comparisons rarely control for payload or quality;
- current models sit orders of magnitude below capacity bounds;
- hard-decision decoding dominates.

These are the openings a matched-quality, multi-code, blind/semi-blind study would address.

### Cited Findings
- **ECC is rarely used in AI-image watermarking.** "Despite its theoretical advantages, the use of RC [redundancy coding] in watermarking remains limited. Most watermarking schemes have inherently low capacity… so adding redundant bits for error correction further reduces the usable payload. Consequently, RC often becomes an impractical trade-off, and only a few recent methods have incorporated it" (Cao et al. survey §7.2, full text). — [arXiv 2510.02384](https://arxiv.org/abs/2510.02384)
- **Payload format is unstructured.** "Existing approaches rarely define a structured or semantically meaningful watermark format that assigns explicit roles to individual bits… Establishing standardized formatting rules, verifiable encoding protocols, and evaluation metrics will be essential" (survey §8.2, Structured and Informative Watermarking, full text). — [arXiv 2510.02384](https://arxiv.org/abs/2510.02384)
- **Payload use is neglected.** "It is often neglected how a multi-bit payload is best used." Code accuracy "degrades more quickly… than bit accuracy" (SynthID-Image §5, full text). — [arXiv 2510.09263](https://arxiv.org/abs/2510.09263)
- **Benchmarks exclude ECC.** W-Bench's bit accuracies "do not include error correction methods, such as BCH… which can be applied to all watermarking models" (full text). — [arXiv 2410.18775](https://arxiv.org/abs/2410.18775)
- **Bit accuracy hides clustered errors and depends on the threshold** (WAVES, full text). — [arXiv 2401.08573](https://arxiv.org/abs/2401.08573)
- **Capacity gap.**
  - "State-of-the-art methods successfully embed around 100–200 bits". "Recent methods operate far below the achievable bounds, often by orders of magnitude". ChunkySeal's 0.0052 bpp is far below a PSNR-only bound above 2 bpp.
  - Future work: better performance "ideally without scaling up models". ChunkySeal is about 1B and 774M parameters (embedder and extractor) (WebFetch summary of full text and search snippet). — [arXiv 2510.12812](https://arxiv.org/abs/2510.12812); [Meta publication page](https://ai.meta.com/research/publications/we-can-hide-more-bits-the-unused-watermarking-capacity-in-theory-and-practice/)
- **ECC comparisons lack controls.** ECC is "routinely bolted onto neural image watermarking decoders… Neither practice comes with a rule for when it helps, and comparisons rarely control for the payload the code itself consumes" (Zenodo 2026 v2 abstract). — [Zenodo](https://zenodo.org/records/22970405)
- **Matched PSNR is not matched rate.** "Equal PSNR does not equalize information rate, coding gain, or perceptual visibility" (NAWE, full text). — [arXiv 2609.25972](https://arxiv.org/abs/2609.25972)
- **Exactness.** Existing diffusion watermarks "cannot recover structured watermark data bit-exactly" (Gaussian Shannon, full text). — [arXiv 2603.26167](https://arxiv.org/abs/2603.26167). Zero-bit errors become "increasingly difficult under real-world distortions" for 2048-bit signatures (README, full text). — [arXiv 2507.04495](https://arxiv.org/abs/2507.04495)
- **Hard-decision dominance.** "Existing ECC-based LLM watermarks rely on hard-decision decoding, discarding token-level reliability information" (CORE-BREW, full text). — [arXiv 2606.24163](https://arxiv.org/abs/2606.24163)
- **Narrow ECC comparisons.** The Frontiers 2026 ECC paper tested only three configurations (BCH, LDPC, LDPC+BCH), with no RS or convolutional codes, no test statistics and bit accuracy only (WebFetch of full page). — [Frontiers](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2025.1750515/full)
- **Capacity limits ECC.** "The volume of information that can be reliably embedded… is limited…, restricting the inclusion of sufficient redundant bits for effective error correction" (DREW, full text). — [arXiv 2406.02836](https://arxiv.org/abs/2406.02836)

### Inferences
- The stated gaps line up with the user's planned contribution:
  - "coding at matched quality" matches the Zenodo and NAWE caveats;
  - "exact recovery" matches SynthID's code accuracy, README and Gaussian Shannon;
  - "modern codes" matches the survey's "few methods incorporate", Frontiers' narrow set and W-Bench's "can be applied to all";
  - "blind vs semi-blind" matches survey §8.2's call for structured bits and the BREW/WAM known-bit detection practice.
- The arrival of 1024-bit post-hoc models (ChunkySeal) removes the survey's main reason for skipping ECC, that payloads are too small. Spending half of 1024 bits on parity still leaves 512 information bits, more than any other open post-hoc model carries raw. This is timely in a way it was not before late 2025.

### Gaps
- The bodies of survey §§8.1, 8.3 and 8.4 and the SoK §7 were only skimmed by keyword. Other stated gaps, for example on standardisation, may exist.
- I did not check whether the ChunkySeal paper's unread second half (characters 100k–243k) mentions ECC. The keyword search of the full downloaded text found none, so this is likely, not certain.

---

## Q6. Overall: is a systematic evaluation of modern ECCs on classical and neural image watermarks, at matched quality, with blind and semi-blind decoding, saturated or open?

### Takeaway
**Open, but the edges are filling in fast (several close preprints in Sept–Oct 2026).** No located paper does what the user proposes:
- the same 5G LDPC, polar, turbo, BCH and RS codes;
- applied identically on top of both classical (e.g., dwtDctSvd) and neural post-hoc backbones (e.g., ChunkySeal at 1024 bits);
- at matched wPSNR;
- reporting exact-ID rate and wrong-ID rate;
- with blind and known-header (semi-blind) decoding, and ideally soft decoding from extractor logits.

The closest works each cover a slice:
- NAWE: polar-SCL, matched PSNR and WER, but its own scheme only.
- Li (Zenodo): payload-matched BCH and Hamming, hard decision, MBRS at 36 bits.
- Gaussian Shannon and PRC: LDPC with exact metrics, in-generation only.
- InvisMark: BCH, success rate, its own model only.

### Cited Findings
- No benchmark applies ECC or exact-ID metrics: W-Bench explicitly excludes ECC; WAVES and MarkDiffusion use TPR@FPR. — [W-Bench](https://arxiv.org/abs/2410.18775); [WAVES](https://arxiv.org/abs/2401.08573); [MarkDiffusion](https://arxiv.org/abs/2509.10569)
- NAWE (22 Sep 2026) compares at matched PSNR with WER but "retains the systems' different payloads and coding". — [arXiv 2609.25972](https://arxiv.org/abs/2609.25972)
- The Li Zenodo study (Sep/Oct 2026) is payload-matched but covers BCH and Hamming, hard decision, on a 36-bit MBRS backbone. — [Zenodo](https://zenodo.org/records/22970405)
- Gaussian Shannon (CVPR 2026) uses LDPC with TPR@BitAcc100%, for in-generation diffusion only. — [arXiv 2603.26167](https://arxiv.org/abs/2603.26167)
- SynthID-Image defines code accuracy but publishes bit accuracy only; ChunkySeal reports bit accuracy only. — [SynthID-Image](https://arxiv.org/abs/2510.09263); [ChunkySeal](https://arxiv.org/abs/2510.12812)

### Inferences
- **Novelty is in the *systematic, matched, exact-ID* evaluation and in the 1024-bit neural setting, not in any single code.** Coding-theory reviewers will consider LDPC, polar and soft decoding on watermark channels to be known since the 2000s (Bastug & Sankur 2004 and others; see the earlier notes). Watermark/ML reviewers may say ECC "can be applied to all watermarking models" (W-Bench). The paper must therefore show *non-obvious* findings, for example:
  - code ranking flips between classical (i.i.d.-ish errors) and neural (bursty, per-image) channels;
  - soft decoding with neural logits helps or hurts depending on calibration;
  - known-header semi-blind decoding changes the false-ID/TPR trade-off;
  - an "effective capacity at matched wPSNR" frontier per backbone;
  - hard-decision miscorrection (wrong IDs) versus CRC/syndrome-flagged failures.
- **Strongest framing.** For example: "Bit accuracy is the wrong metric for provenance IDs. Exact-ID recovery of neural and classical watermarks with modern channel codes at matched quality." The user's own numbers make the case: 13% of frames exact at 1024 raw bits against 180/180 with LDPC rate 1/2. This lines up with SynthID's and WAVES's critiques.
- **Timing risk.** Three closely related preprints appeared between Sept and Oct 2026 (NAWE, Li v1 and v2), plus CVPR 2026's Gaussian Shannon. The window is open but narrowing. Citing and differentiating from these four is essential.
- **Likely venues (inference).** IEEE WIFS, ACM IH&MMSec, ICASSP, IEEE TIFS or SPL for the coding-centric version; a datasets-and-benchmarks track for a benchmark version that adds exact-ID metrics and ECC to existing benchmarks.
- **Rigour expectations (inference).**
  - Report confidence intervals: 0/180 failures gives a 95% upper bound of about 1.7%.
  - Report wrong-ID (undetected-error) rates separately from failures.
  - Report detection TPR at fixed FPR alongside, and give header-bit overhead.
  - Use more trials than 180 if claiming near-zero failure.

### Gaps
- I could not check Google Scholar for unindexed theses or workshop papers on "LDPC/polar + HiDDeN/StegaStamp/Video Seal". A small number of such works may exist outside arXiv, OpenAlex and the search engine used.
- I could not determine whether any industry system (SynthID, Digimarc, TrustMark deployments) uses LDPC or polar internally. SynthID-Image does not disclose its payload coding.
