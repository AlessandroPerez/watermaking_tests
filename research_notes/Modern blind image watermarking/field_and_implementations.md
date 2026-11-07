# Modern blind image watermarking: how the field developed (2005–2026), what is deployed, how it is benchmarked, and which implementations are reusable

Status as of 2026-11-03. Source-quality key: "(opened)" means the page itself was read in this session. "(snippet)" means the fact was seen only in a search-result summary because the page was blocked (403/401/paywall/cert error) or not opened. Treat snippet-only facts as lower confidence. "[UNVERIFIED]" marks claims that could not be confirmed from any source in this session. GitHub and PyPI dates come from the public GitHub REST API and PyPI JSON API, queried on 2026-11-03.

## Q1. Why did classical watermarking research slow down or change direction after about 2005–2010?

### Takeaway
The field did not stall. It split. By about 2005 the communication-theory core was in place: informed (side-informed) coding, QIM/dither modulation and spread spectrum, all framed by Costa's dirty-paper result. Work from 2005 to 2010 then showed that robustness is not security. Cayre, Fontaine and Furon (2005) and the Bas/Furon line of work, the oracle/sensitivity attacks, and the BOWS and BOWS-2 contests showed that an adversary who can observe marked content or query a detector can estimate the key and remove the mark. Academic interest fell during the 2010s, while the remaining effort moved to industry products, steganography and forensics. The revival came with deep learning (HiDDeN, July 2018) and then generative-AI provenance (from 2023). That is why the "canonical" blind algorithms an engineer finds in libraries date from 1998–2008.

### Cited Findings
**Security theory (2005 onward)**
- Cayre, Fontaine and Furon, "Watermarking security: theory and practice", appeared in *IEEE Trans. Signal Processing* 53(10):3976–3987 (2005). Its companion SPIE 2005 papers were "Watermarking security part one: Theory" and "part two: Practice" — [dblp listing via search](https://dblp.org/pid/48/5609) (snippet).
- The core idea is that security means information leakage about the secret key from observed watermarked contents. It is measured with Shannon mutual information and the Fisher information matrix. The "security level" is the number of observations an attacker needs to estimate the key. The theory was applied to substitutive and spread-spectrum schemes, and Part Two studies practical estimators — [core.ac.uk record](https://core.ac.uk/works/28065217) (snippet; page returned 403); [SPIE Part Two](https://nanophotonics.spiedigitallibrary.org/conference-proceedings-of-spie/5681/0000/Watermarking-security-part-two-Practice/10.1117/12.586890.full) (snippet).
- This line of work was later consolidated in the SpringerBrief *Watermarking Security* (2016) by Bas, Furon, Cayre, Doërr and Mathon — [Springer listing](https://link.springer.com/978-981-10-0505-3) (snippet).
- Bas and Furon (EUSIPCO 2012) introduced an "effective key length" measure. They concluded that the key length of the system used for BOWS-2 "was indeed equal to 128 bits" — [EUSIPCO 2012 PDF](https://new.eurasip.org/Proceedings/Eusipco/Eusipco2012/Conference/papers/1569588779.pdf) (snippet).

**Oracle and sensitivity attacks**
- Linnartz and van Dijk, "Analysis of the sensitivity attack against electronic watermarks in images", Information Hiding 1998, LNCS 1525, pp. 258–272. A publicly available detector can be abused as an oracle: the attacker iteratively modifies the image until the detector stops firing. Follow-ups include Kalker, Linnartz and van Dijk's "Watermark estimation through detector analysis" (ICIP 1998) and Comesaña, Pérez-Freire and Pérez-González's "The return of the sensitivity attack" (2005). The later Blind Newton variant needs no knowledge of the decision function — [Springer DOI 10.1007/3-540-49380-8_18 via unpaywall](https://unpaywall.org/10.1007%2F3-540-49380-8_18) (snippet).
- Quiring, Arp and Rieck (arXiv 1703.05561, March 2017) give a unified notation for black-box attacks on machine learning and on watermarking. They show that "techniques for hardening machine learning can fend off oracle attacks against watermarks" — [arXiv abstract](https://arxiv.org/abs/1703.05561) (opened).

**BOWS and BOWS-2 contests**
- BOWS-2 ran "between the 17th of July 2007 and 17th of April 2008", within the Watermarking Virtual Laboratory (Wavila) of the EU Network of Excellence ECRYPT — [IEEE SPS data-challenge page](https://signalprocessingsociety.org/publications-resources/data-challenges/break-our-watermarking-system-2nd-ed) (opened; the page gives no results).
- The BOWS-2 target was "Broken Arrows", a zero-bit scheme by Furon and Bas. It was designed "from the lessons learnt during BOWS-1" as a "pure zero-bit watermarking scheme (no message decoding), which spreads the presence of the mark all over the host image". It implements a theoretical result of Merhav and Sabbag (2008) — [EURASIP JIS 2008](https://jis-eurasipjournals.springeropen.com/articles/10.1155/2008/597040) (snippet; redirects to a paywall).
- The first BOWS-2 episode did not break the scheme. In episodes 2 and 3, "pirates could observe plenty of pictures watermarked with the same secret key", and "security flaws have been revealed" — [search summary of a Furon paper](https://hal.archives-ouvertes.fr/hal-00335311) (snippet).
- A 2020 paper still calls Broken Arrows "the state-of-the-art zero-bit watermarking scheme in the image domain" and says it "won the BOWS competition" — [arXiv 2011.07355](https://arxiv.org/pdf/2011.07355) (snippet).
- BOWS-1 (2005–2006) was broken by key-guessing and sensitivity attacks: Comesaña and Pérez-González, EURASIP JIS 2007; also Westfeld, and Craver et al.'s "How we broke the BOWS watermark" — [EURASIP JIS 2007/25308](https://jis-eurasipjournals.springeropen.com/articles/10.1155/2007/25308) (snippet; redirects to a Springer login).

**Removal and estimation attacks**
- Voloshynovskiy, Pereira, Iquise and Pun, "Attack modelling: towards a second generation watermarking benchmark", *Signal Processing* 81(6):1177–1214 (2001). Their attacks use prior information about the image and the watermark (denoising and estimation style), not just generic signal processing — [Univ. Geneva / search](https://www.unige.ch/sip/download_file/view/137/311) (snippet).
- The modern equivalent is the regeneration attack of Zhao et al. (NeurIPS 2024). It noises the latent and regenerates the image, and it is provably effective against any watermark that perturbs the image within a bounded ℓ2 distance. On RivaGAN, regeneration removed 93–99% of the marks, against ≤3% for baseline attacks — [arXiv 2306.01953](https://arxiv.org/html/2306.01953v3) (snippet). The code is [XuandongZhao/WatermarkAttacker](https://github.com/XuandongZhao/WatermarkAttacker) (MIT, last push 2025-01-24; GitHub API).
- A related attack is CtrlRegen, "Image watermarks are removable using controllable regeneration from clean noise" (ICLR 2025) — [yepengliu/CtrlRegen](https://github.com/yepengliu/CtrlRegen) (repo description, GitHub API; no licence file).

**Theoretical capacity results that framed "settled" fundamentals**
- Costa, "Writing on dirty paper", *IEEE Trans. Inf. Theory* 29(3):439–441, May 1983. Dirty-paper coding "achieves the channel capacity without a power penalty", the receiver does not need the interference, and DPC "has also been used for informed digital watermarking" — [Wikipedia: Dirty paper coding](https://en.wikipedia.org/wiki/Dirty_paper_coding) (opened).
- Moulin and Koetter, "Data-hiding codes", *Proc. IEEE* 93(12):2083–2127, Dec. 2005, is the standard tutorial-level synthesis of the information-theoretic data-hiding results — [bibliographic snippet](https://archive-ouverte.unige.ch/unige:47689) (snippet only; content not read).
- STDM is described as a low-complexity form of QIM that beats spread spectrum against some attacks such as JPEG [MIT DSP group PDF](https://dsp-group.mit.edu/wp-content/uploads/2024/11/AchievablePerformance.pdf) (snippet). It is also described as "very sensitive to valumetric scaling" [UCL thesis](https://discovery-pp.ucl.ac.uk/id/eprint/1443976) (snippet).
- Chen and Wornell's QIM paper ("provably good methods") is hosted at [MIT DSP group](https://dsp-group.mit.edu/wp-content/uploads/2024/11/ProvablyRobust.pdf). The PDF was downloaded but could not be text-extracted (no PDF tooling), so its exact claims are [UNVERIFIED] in this session.
- Rational Dither Modulation (Pérez-González, Mosquera, Barni and Abrardo) appeared in *IEEE Trans. Signal Processing* 53(10):3960–3975 (2005), the same issue as Cayre et al. It makes dither modulation invariant to gain attacks through a gain-invariant adaptive quantisation step, and it achieves much higher rates than improved spread spectrum (ISS) at equal bit-error rate — [Univ. Vigo record](https://portalcientifico.uvigo.gal/documentos/5fa08253299952440aaea2ec?lang=en) (snippet).

**Capacity is not exhausted in practice (2025)**
- Petrov, Fernandez, Souček and Elsahar (Oxford / Meta FAIR), "We Can Hide More Bits: The Unused Watermarking Capacity in Theory and in Practice", arXiv 2510.12812; Meta's page dates it 18 Dec 2025. They write that robust deep-learning methods are "limited to the scale of only a few hundred bits". Their ChunkySeal (1024 bits) "is still very far from the theoretical limits". Video Seal "fails to encode even 1024 bits", while 2048 bits were encoded with a linear model, 32,768 by tiling and 456,509 with a handcrafted model — [Meta publication page](https://ai.meta.com/research/publications/we-can-hide-more-bits-the-unused-watermarking-capacity-in-theory-and-practice/); [arXiv](https://arxiv.org/abs/2510.12812v1) (snippet).

**Decline in the 2010s and revival in the 2020s**
- Pierre Fernandez's thesis (arXiv 2502.05215, §1.1) says: "The decline in watermarking research around the 2010s can be attributed to several factors". It continues: "As the field matured, focus shifted towards industry applications", funding moved toward "cloud computing and AI", and "Watermarking has started to become popular again since the start of the decade", driven by "the popularization of generative models" — [arXiv HTML](https://arxiv.org/html/2502.05215) (opened).
- The same thesis explains why deep learning took over: it "avoids algorithms hand-crafted for specific transformations", and networks are "trained end-to-end … resilient to transformations applied during training" — [arXiv HTML §2.3.1](https://arxiv.org/html/2502.05215) (opened).
- The deep-learning era starts with HiDDeN (Zhu, Kaplan, Johnson, Fei-Fei), arXiv 1807.09937, submitted 26 July 2018. It trains an encoder and decoder jointly, robust to blur, crop and JPEG — [arXiv](https://arxiv.org/abs/1807.09937) (opened; the ECCV 2018 venue is not stated on that page).
- In a 2008 IEEE talk, Ton Kalker (HP Labs) contrasted the mid-1990s hype with how few applications were deployed about ten years later — [IEEE SCV SPS abstract](https://ewh.ieee.org/r6/scv/sps/200809Abstract.htm) (snippet; the page failed a TLS check).
- A 2011 review by Blake and Latifi says watermarking faces "an uphill battle against relatively simple attacks" — [UNLV record](https://oasis.library.unlv.edu/ece_fac_articles/358) (snippet).

**Publication trends**
- A CiteSpace bibliometric review in *Symmetry* 17(6):871 (2025) covers 8,621 Web of Science Core Collection publications on watermarking from 2004 to 2024. It reports that hotspots expanded from copyright protection to integrity verification, multimedia and "intelligent technologies" — [MDPI](https://www.mdpi.com/2073-8994/17/6/871) (snippet; the page returned 403, so per-year counts were not retrieved).

### Inferences
- The 1998–2005 algorithms keep getting cited because they are the last generation of designs that are general-purpose, simple and patent-light. After that, academic classical work either went deep into theory and security (zero-bit detection, key-length measures, side-informed codes) or became incremental transform combinations. Neither produced a new "default algorithm" that a library would package.
- The security results matter for an engineer. Any public, fixed-key, blind detector, whether classical or neural, is exposed to oracle and estimation attacks. Neural methods inherit this problem; they do not solve it. The SynthID-Image paper (Q3) states "Achieving perfect security is impossible".
- The ChunkySeal paper suggests that capacity theory, not just robustness, is again an active question in 2025–2026. This is relevant to the user's 512-bit payload, because most robust neural methods carry 32–256 bits.

### Gaps
- No primary source with year-by-year publication counts for classical image watermarking was retrieved; the MDPI bibliometric paper was blocked.
- The full texts of Cayre et al. (2005), Chen–Wornell (2001) and Moulin–Koetter (2005) were not read; only abstracts or bibliographic records were seen.
- The official BOWS-2 results table and winners were not found. The bows2.ec-lille.fr site was not reachable.
- No source was found that states plainly why IH&MMSec's focus moved to steganalysis and forensics. This is inferred from the field's general trajectory and is [UNVERIFIED].

## Q2. Were the fundamentals essentially settled, and what was the incremental output of 2010–2020?

### Takeaway
Broadly yes. Spread spectrum, QIM/STDM/DC-QIM, RDM-type gain invariance, informed coding and the geometric-resilience toolbox were all in place by about 2008. The geometric toolbox comprises templates or calibration peaks in the Fourier domain, log-polar/Fourier–Mellin invariant domains, moment invariants and feature-point anchoring. Most of the 2010–2020 classical output in lower-tier venues recombined DWT/DCT/SVD (often with metaheuristic optimisation). A well-documented strand of critique showed that many SVD-based schemes have a structural false-positive flaw. The widely used "DWT-DCT-SVD" in invisible-watermark is itself just scalar QIM on one singular value per block.

### Cited Findings
- **Families of geometric (RST) resilience.** A survey by Zheng, Liu, Zhao and El Saddik describes "two categories": "rectify the RST transformed image before conducting watermark detection", or "embed and detect watermark in an RST invariant or semi-invariant domain". Zheng's 2008 Ottawa thesis lists five classes: "RST invariant domain, salient feature, template, image decomposition and stochastic analysis based algorithms" — [uOttawa thesis record](https://ruor.uottawa.ca/items/0d4e2e10-31ea-41d9-a160-b17e31602c77/full) (snippet). The survey's venue (ACM Computing Surveys, 2007) is [UNVERIFIED].
- Zheng, Zhao and El Saddik (2003) embed in "the log-polar mappings of the Fourier magnitude spectrum" and detect by phase correlation; a template can be added to undo geometric distortions — [RIT-hosted PDF](https://home.cis.rit.edu/~cnspci/references/zheng2003.pdf) (snippet).
- **Classical baselines cited by modern benchmarks** are DWT-DCT (Al-Haj, 2007) and DWT-DCT-SVD (Navas et al., 2008) — [W-Bench/VINE paper arXiv 2410.18775](https://arxiv.org/html/2410.18775) (opened); [WAM paper arXiv 2411.07231](https://arxiv.org/html/2411.07231) (opened).
- **What invisible-watermark's `dwtDctSvd` actually does (from source).** It converts BGR to YUV and takes a one-level Haar DWT. In 4×4 blocks of the LL band it applies a DCT and an SVD, then quantises the largest singular value: `s[0] = (s[0] // scale + 0.25 + 0.5*bit) * scale`. Decoding is `(s[0] % scale) > 0.5*scale`. The default `scales=[0,36,0]` combined with the loop `for channel in range(2)` means only the U chroma channel carries the mark — [imwatermark/dwtDctSvd.py](https://github.com/ShieldMnt/invisible-watermark/blob/main/imwatermark/dwtDctSvd.py) (opened via raw source).
  - `dwtDct` (maxDct.py) has default `scales=[0,36,36]` but the same `range(2)` loop, so it also marks only U — [imwatermark/maxDct.py](https://github.com/ShieldMnt/invisible-watermark/blob/main/imwatermark/maxDct.py) (opened).
- **guofei9987/blind_watermark** uses the same construction: Haar DWT, 4×4 blocks, DCT, keyed shuffle, SVD, then `s[0] = (s[0] // d1 + 1/4 + 1/2*wm) * d1` with d1=36, plus `s[1]` with d2=20. It runs on all three YUV channels — [bwm_core.py](https://github.com/guofei9987/blind_watermark/blob/master/blind_watermark/bwm_core.py) (opened).
- **SVD false-positive critique.**
  - Ling, Phan and Heng (*J. Electronic Imaging*, 2011) showed that the countermeasures proposed by Loukhaoukha and Chouinard "do not solve the false-positive detection" problem in the Abdallah and Aslantas SVD schemes — [SPIE JEI 20(1) 010501](https://ebooks.spiedigitallibrary.org/journals/journal-of-electronic-imaging/volume-20/issue-1/010501/On-the-security-of-ownership-watermarking-of-digital-images-based/10.1117/1.3534865.full) (snippet).
  - Another critique says an SVD + tiny-GA scheme "is fundamentally flawed and has a very high probability of false positive detection", corroborating Tian et al. — [JIH-MSP 2012](https://bit.kuas.edu.tw/2012/vol3/JIH-MSP-2012-02-002.pdf) (snippet).
- **Early comments on Liu and Tan's SVD scheme.** The scheme is "An SVD-based watermarking scheme for protecting rightful ownership", *IEEE TMM* 4(1):121–128, 2002.
  - A "Comments on" correspondence is attributed to Zhang and Li, *IEEE TMM* 7(1), 2005 — [arXiv 0808.0309 reference list](https://arxiv.org/pdf/0808.0309) (snippet). Other papers attribute a comment of the same title to Rykaczewski, *IEEE TMM* 9:421–423, 2007 — [MDPI Future Internet 9(3):45](https://mdpi.com/1999-5903/9/3/45) (snippet). These attributions conflict; check IEEE Xplore.
  - Y. Wu, "On the security of an SVD-based ownership watermarking", *IEEE TMM* 7(4):624–627, 2005 (same snippet sources).
- Makbol, Khoo and Rassem's 2019 *Multimedia Tools and Applications* review notes that even SVD schemes that meet robustness criteria "can still encounter false positive problems", and it classifies schemes by exposure — [doi 10.1007/s11042-018-5891-y](https://www.doi.org/10.1007/S11042-018-5891-Y) (snippet). A "false-positive-free" SVD scheme was proposed by Guo and Prasetyo (*J. Vis. Commun. Image Represent.* 25(5)) (same snippet).
- **Incremental work in the theoretical core continued**: trellis-coded RDM (IEE Proc. 2006) and a DFT-based RDM robust to linear filtering — [Univ. Vigo records](https://portalcientifico.uvigo.gal/documentos/5fa0824d299952440aaea24f?lang=en) (snippet).

### Inferences
- The source code shows that both popular "DWT-DCT-SVD" Python libraries embed with fixed-step scalar QIM (dither modulation without dither) on the largest singular value of a block. Theory has known since 2005 that this is not gain-invariant (cf. RDM). It also has no synchronisation, so the libraries' failure modes are expected from first principles, not a sign of poor tuning.
- The SVD stage does not change the robustness class: s[0] of a near-flat block is close to |DC|. The SVD mainly adds the false-positive pitfalls (in non-blind, image-watermark variants) that the critiques target.
- "Hybrid transform + metaheuristic" papers from 2010–2020 mostly re-tuned the same QIM/additive embedding. They did not change the fundamental trade-offs. This is a judgement from the critique literature and the benchmark results in Q4, not a measured statistic.

### Gaps
- No quantitative study (bibliometric or meta-analysis) of the "flood" of SVD/hybrid papers by venue tier was found.
- The Lin–Cox et al. (2001) RST-resilient method, Kutter's (1998) self-reference template, Pereira–Pun (2000) template matching, and Kim–Lee Zernike-moment watermarking are classic geometric-resilience references. They were not verified in this session [UNVERIFIED as citations].

## Q3. Industry and standards: who deploys what (classical or neural)?

### Takeaway
Deployed systems split along vendor age.
- **Classical, with geometric synchronisation:** Digimarc. Its patents describe a tiled, spread-spectrum-style mark with a Fourier-domain grid of peaks that is used to estimate affine transforms. It is deployed on retail and recycling packaging and as a C2PA soft binding.
- **Neural (encoder/decoder):** Google SynthID-Image (136-bit, proprietary), Meta VideoSeal/PixelSeal/ChunkySeal and WAM (open, MIT), Adobe TrustMark (open, MIT), Microsoft InvisMark (open, MIT), Steg.AI (deep-learning "light field messaging"), and Imatag (partly HiDDeN-derived, per the Hugging Face blog).
- **Standards:** C2PA 2.1 or later defines watermark "soft bindings" via an algorithm registry, which held 28 entries as of this check. ISO/IEC 21617-3 (JPEG Trust Part 3, media asset watermarking) is algorithm-agnostic and its publication status is in conflict between sources. No IEEE watermarking standard was found.

### Cited Findings
**C2PA soft binding**
- C2PA 2.1 added watermark-based recovery of Content Credentials, a "Watermarked Action", a "Soft Binding Assertion" naming the algorithm, an authoritative algorithm list, and a Soft Binding Resolution API. The API also supports fingerprints. Digimarc is "a co-chair of the C2PA watermarking task force", working with Adobe. Digimarc claims its marks "resist common modifications such as cropping, rotation, resizing"; these are vendor claims without data. Blog post by D. Guinard, 27 Aug 2024 — [Digimarc blog](https://digimarc.com/blog/c2pa-21-strengthening-content-credentials-digital-watermarks) (opened).
- C2PA soft-binding algorithm registry, downloaded 2026-11-03 — [spec.c2pa.org JSON](https://spec.c2pa.org/softbinding-alg-list/softbinding-algorithm-list.json) (opened). Image-capable watermark entries, with registration dates:

  | Date | Algorithm id | Description |
  |---|---|---|
  | 2024-05-17 | `com.digimarc.validate.1` | audio, video, text, image |
  | 2024-05-17 | `org.atsc.a336` | ATSC A/334, A/335, A/336 |
  | 2024-05-17 | `com.adobe.trustmark.Q` / `.C` | |
  | 2025-02-05 | `com.adobe.trustmark.P` | |
  | 2024-05-20 | `ai.steg.api` | |
  | 2024-08-14 | `ai.trufo.gen1.image`, `ai.trufo.gen1.image-lite` | |
  | 2024-08-14 | `app.overlai.watermark.1` | |
  | 2025-02-26 | `com.imatag.lamark.v1` | |
  | 2025-02-26 | `com.nagra.nexguard.watermark.1` | |
  | 2025-03-12 | `com.mentaport.watermark.1` | |
  | 2025-10-12 | `com.microsoft.invismark.1` | image, video |
  | 2025-11-26 | `ai.contentlens.image.*` | three variants |
  | 2026-01-26 | `es.lumatrace` | "Java-native Adaptive Spatial Watermarking using Blue-channel injection" |
  | 2026-02-25 | `com.markany.watermark.1` | |

  - Fingerprint entries include ISO 24138 ISCC (`io.iscc.v0`), Adobe ICN dense fingerprint, and DigiCAP.
  - Video-only entries include Kinetiq/Teletrax, castLabs, Verimatrix and SonicOrigin.
  - The registry's GitHub README calls it an "authoritative list" that the C2PA Technical Working Group may prune — [c2pa-org/softbinding-algorithm-list](https://github.com/c2pa-org/softbinding-algorithm-list) (snippet).

**Digimarc: classical, with geometric synchronisation**
- **US 8,301,453 B2**, "Watermark synchronization signals conveying payload data". Assignee Digimarc, inventor Ravi K. Sharma, priority 21 Dec 2000 — [Google Patents](https://patents.google.com/patent/US8301453B2/en) (opened).
  - The grid or calibration signal "comprises a collection of impulse or delta functions in the Fourier magnitude domain", placed in mid frequencies.
  - Rotation and scale come from correlating "the log-polar representation" with a log-polar remapping of the grid's Fourier magnitude. Affine refinement covers rotation, scale, differential scale and shear.
  - The impulses have pseudo-random but known phase, so translation can be computed.
  - "The payload can be discerned from the polarities of the grid signal components."
- **US 9,182,778 B2**, "Signal processors and methods for estimating transformations between signals with least squares". Digimarc; inventors Sharma, Lord and Lyons; priority 3 Sep 2010; granted 10 Nov 2015; adjusted expiry 31 Oct 2033 — [Google Patents](https://patents.google.com/patent/US9182778B2/en) (opened).
  - "The reference signal is a set of frequency peaks corresponding to the watermark signal."
  - A Direct Least Squares (DLS) method starts from seed rotation/scale candidates and iteratively refines a 2×2 linear transform by re-locating peaks in 3×3 neighbourhoods.
  - The patent compares DLS with Fourier–Mellin (log-polar): DLS needs fewer evaluations, is more accurate and allows arbitrary seed spacing. Translation is found by "phase estimation" and phase deviation without an inverse FFT.
- Other Digimarc patents describe log-polar mapping of the watermark's autocorrelation (US 7,152,021) and calibration features that give affine parameters (US 6,975,745) — [Justia US7152021](https://patents.justia.com/patent/7152021); [Google Patents US6975745](https://patents.google.com/patent/US6975745) (snippets).
- Several Digimarc packaging patents say:
  - "the synchronization signal is a collection of peaks in the Fourier domain … generated in the spatial domain in a block size coextensive with the 256 by 256 tile";
  - "a GTIN identifier can be encoded in a watermark integrated with, and printed with, the packaging artwork";
  - an "Embedded Systems SDK" is used in machine-vision line inspection.

  Sources: [USPTO 10506128](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10506128); [USPTO 11270404](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11270404) (snippets only; the PDFs were not opened).
- **Packaging deployment evidence (HolyGrail 2.0, with Pellenc ST and Digimarc):**
  - 2022 semi-industrial trials reported 99% detection, 95% ejection and 95% purity on about 125,000 packs from 260 SKUs.
  - A rigid-packaging trial from 19 Aug to 19 Dec 2024 at a German MRF reported 87.9–93.8% detection in single-pass sorting.

  Sources: [Packaging Europe](https://www.packagingeurope.com/holygrail-20-concludes-semi-industrial-trials-with-successful-validation/); [Packaging Insights](https://www.packaginginsights.com/news/holygrail-20-digital-watermarks-project-validates-detection-sorting-in-semi-industrial-trials.html) (snippets; trade press reporting initiative numbers).

**Google SynthID-Image: neural, proprietary**
- Source: arXiv 2510.09263, 10 Oct 2025, Gowal and 25 co-authors at Google DeepMind — [arXiv HTML](https://arxiv.org/html/2510.09263v1) (opened).
- Design and deployment:
  - "We used an encoder-decoder approach". It is post-hoc and model-independent.
  - It has been used to mark "over ten billion images and video frames across Google's services"; verification is available to trusted testers.
  - The external variant, SynthID-O, "can encode 136-bit payloads within 512×512 pixel images".
- Baselines are StegaStamp, TrustMark-P/Q, InvisMark, WAM, and VideoSeal 0.0 and 1.0. There is no classical baseline.
- Results in TPR@0.1% FPR:
  - Spatial (random): SynthID-O 99.98, WAM 84.34, VideoSeal-1.0 about 67.5, InvisMark about 61.
  - Colour (random): SynthID-O 100.00, StegaStamp 99.95, TrustMark-Q about 99.67, WAM 81.29.
- "Achieving perfect security is impossible". The authors expect deployment "alongside a metadata-based standard like C2PA".

**Meta: neural, open source**
- **Video Seal** was released December 2024 (arXiv 2412.09492). v1.0 (256-bit) followed in March 2025. PixelSeal (256-bit, arXiv 2512.16874) and ChunkySeal (1024-bit, arXiv 2510.12812) were released in December 2025, with checkpoints. The README says "The model is licensed under an MIT license" — [facebookresearch/videoseal](https://github.com/facebookresearch/videoseal) (opened).
- Press coverage at launch said the code, models and demo were released under permissive licences, alongside Watermark Anything, AudioSeal and the Omni Seal Bench leaderboard. No source confirms that Meta deploys Video Seal in its own products — [Maginative](https://www.maginative.com/article/meta-releases-video-seal-an-open-source-watermarking-tool-for-ai-video/); [Meta AI page](https://ai.meta.com/research/publications/video-seal-open-and-efficient-video-watermarking) (snippets).
- **Watermark Anything (WAM)** carries 32 bits: "WAM's capacity is limited to 32 bits". It was trained with resize, crop, rotate, flip and perspective augmentations — [arXiv 2411.07231](https://arxiv.org/html/2411.07231) (opened).

**Adobe TrustMark: neural, open source**
- It carries a 100-bit payload with BCH modes BCH_SUPER, BCH_5, BCH_4 and BCH_3.
- Variants Q and P are documented in the README; variant C is listed in the C2PA registry.
- The MIT licence covers "the code in this repo and the model files".
- Implementations exist in Python (`pip install trustmark`), JavaScript (decode only), Rust and C++ (ONNX).
- The paper is arXiv 2311.18297, ICCV 2025 — [adobe/trustmark](https://github.com/adobe/trustmark) (opened).

**Microsoft InvisMark: neural, open code**
- [microsoft/InvisMark](https://github.com/microsoft/InvisMark): MIT, created 2024-10-31, last push 2026-04-13 (GitHub API). It is registered in C2PA as `com.microsoft.invismark.1`.
- The SynthID paper benchmarks it as 100-bit. A 256-bit capacity claim is [UNVERIFIED].

**Imatag**
- Teddy Furon (Inria) is a co-founder. According to the Hugging Face blog, Imatag's BZH detector "is derived from HiDDeN", combined with an in-house zero-bit decoder, and its watermarker and detector are private — [HF blog: Stable Signature + IMATAG's BZH](https://huggingface.co/blog/imatag-vch/stable-signature-bzh) (snippet).
- Its C2PA entry is "Imatag invisible watermarking for images" (`com.imatag.lamark.v1`) (registry, opened). Whether LaMark itself is neural or classical is [UNVERIFIED].

**Steg.AI**
- Its "Light Field Messaging" came from Eric Wengrowski's PhD in Kristin Dana's Rutgers lab and "leveraged recent deep learning advances". Rutgers granted an exclusive licence in 2023 — [Rutgers news](https://www.rutgers.edu/news/rutgers-office-research-helps-launch-company-using-ai-prevent-deepfakes); [ROI-NJ](https://www.roi-nj.com/2023/03/31/tech/rutgers-office-for-research-executes-exclusive-license-with-artificial-intelligence-startup-steg-ai/) (snippets).

**ISO, IEEE and other standards**
- ISO/IEC 21617-1:2025, JPEG Trust Part 1 "Core foundation", was published on 2025-01-27 — [SCC record](https://scc-ccn.ca/standardsdb/standards/2056652) (snippet).
- ISO/IEC 21617-3, JPEG Trust Part 3 "Media asset watermarking", covers an "algorithm-agnostic embedding and extraction process", signalling, watermark structure, evaluation criteria and "pointers to repositories". Sources conflict on its status:
  - the ISO page shows DIS (enquiry) stage;
  - BSI lists BS ISO/IEC 21617-3 as published on 14 Jul 2026;
  - DIN lists a 2026-07 draft.

  Sources: [ISO 90209](https://www.iso.org/standard/90209.html) (403 when opened); [BSI](https://knowledge.bsigroup.com/products/bs-iso-iec-21617-3-information-technology-jpeg-trust-part-3-media-asset-watermarking); [DIN](https://www.dinmedia.de/en/draft-standard/iso-iec-dis-21617-3/404694192); [JPEG requirements doc](https://ds.jpeg.org/documents/jpegtrust/wg1n101309-109-REQ-Use_Cases_and_Requirements_for_Media_Asset_Watermarking.pdf) (snippets).
- ATSC A/334–A/336 (broadcast watermark) and ISO 24138 ISCC (fingerprint) appear in the C2PA registry (opened).

### Inferences
- Digimarc's published patents describe exactly the "classical template synchronisation" architecture: a Fourier peak grid estimated by log-polar search or DLS, then phase for translation, then a tiled payload. This is the main commercial evidence that classical blind watermarking with explicit synchronisation remains viable at scale, specifically in print and packaging, where the geometry is camera-induced and attacks are not adversarial.
- Every large AI or platform vendor that published a method from 2023 onward (Google, Meta, Adobe, Microsoft) chose neural encoder/decoders. Their payloads fall in a narrow 32–256-bit band: 136 bits for SynthID-O, 100 for TrustMark, 256 for VideoSeal v1.0 and PixelSeal, and 32 for WAM. The exception is ChunkySeal at 1024 bits.
- C2PA soft binding does not require a large payload. The watermark only needs to carry a lookup key to a manifest store. This is why 100–136 bits suffice for industry, and why no one optimised for 512-bit blind payloads.

### Gaps
- Digimarc's exact current production algorithm (Digimarc Validate / Illuminate) is not publicly specified. The patents describe families of methods, not necessarily the shipped version. The 256×256-tile packaging patent text was seen only as a snippet.
- No peer-reviewed independent evaluation of Digimarc, Imatag, Steg.AI, Trufo or MarkAny robustness was found.
- No IEEE standard on image watermarking was found. Searching the IEEE SA catalogue directly was not done.
- The exact status of ISO/IEC 21617-3 is unresolved because sources conflict.

## Q4. Benchmarks and evaluation tools, and what they say about classical baselines

### Takeaway
The first-generation benchmarks (StirMark 1997→4.0, Checkmark 2001, Optimark ~2001, Certimark 2000–2002) are historical. Only StirMark is still downloadable. Modern benchmarks are neural and diffusion-oriented:
- WAVES (ICML 2024);
- W-Bench (VINE, ICLR 2025);
- MarkDiffusion (JMLR 2026), covering in-generation methods only;
- Meta's omnisealbench (archived June 2026) and its HF leaderboard;
- WatermarkLab (PyPI, 2025).

Where these benchmarks include classical DWT-DCT or DWT-DCT-SVD at all, the result is consistent:
- usable against JPEG, noise and brightness changes;
- about 0% TPR or chance-level bit accuracy under geometric transforms;
- weak under valuemetric/colour attacks and under regeneration or editing;
- sometimes relatively robust to adversarial attacks.

### Cited Findings
**Historical tools**
- StirMark was first published in November 1997 as "a generic tool for simple robustness testing of image watermarking algorithms". It "introduced random bilinear geometric distortions to de-synchronise watermarking algorithms". StirMark 3.1 and StirMark Benchmark 4.0 are "freely available as binary and C/C++ source code" with git repositories on Codeberg. The licence comes from the package "copyright" file, and use for any purpose other than research or evaluation "is prohibited" — [petitcolas.net StirMark page](https://petitcolas.net/watermarking/stirmark) (opened). Version release dates are not given on the page.
- Checkmark (Pereira et al., Univ. Geneva, MATLAB) was "based on StirMark" with added attacks that "take into account statistical properties of images and watermarks". It is "now discontinued". Certimark was an EU project, 2000–2002 (another source says it was launched May 2001), meant to set up a benchmarking suite and "a standard certification process"; it is discontinued with no public source. Optimark (Solachidis et al., Aristotle Univ. of Thessaloniki, Windows) results are "neither open source nor Web accessible". Sources: [OR-Benchmark, arXiv 1506.00243](https://arxiv.org/pdf/1506.00243); [Purdue CERIAS report](https://www.cerias.purdue.edu/assets/pdf/bibtex_archive/2004-84.pdf); [Meerwald, Checkmark EI 2002](https://www.cosy.sbg.ac.at/~pmeerw/Watermarking/ei02/) (snippets).

**WAVES**
- An et al., ICML 2024 (PMLR v235) — [PMLR](https://proceedings.mlr.press/v235/an24a.html) (snippet); [arXiv 2401.08573v3](https://arxiv.org/html/2401.08573v3) (opened).
- The metric is TPR@0.1% FPR. Attacks fall into three groups: distortions (single and combined geometric, photometric, degradation), regeneration (VAE, diffusion, rinsing), and adversarial (grey-box and black-box embedding, surrogate detectors).
- The main study uses Stable Signature, Tree-Ring and StegaStamp because "these three methods are far more robust to simple off-the-shelf attacks than alternative watermarking algorithms".
- DwtDct's listed weaknesses are "distortion and purification". In Appendix G.5, DWT-DCT "is highly susceptible to regeneration attacks … and most distortion attacks …, but relatively robust against adversarial attacks". StegaStamp is the most robust overall.
- The code is [umd-huang-lab/WAVES](https://github.com/umd-huang-lab/WAVES): no licence file, last push 2024-09-15 (GitHub API).

**W-Bench (VINE)**
- Lu et al., arXiv 2410.18775v2, 15 Mar 2025. The repo states ICLR 2025 — [arXiv HTML](https://arxiv.org/html/2410.18775) (opened); [Shilin-LU/VINE](https://github.com/Shilin-LU/VINE) (GitHub API: licence NOASSERTION, last push 2026-03-27).
- There are 11 baselines: MBRS, CIN, PIMoG, RivaGAN, SepMark, TrustMark, DWTDCT, DWTDCTSVD, SSL, StegaStamp and EditGuard. All are at 30 bits and 512×512.
- Classical results (TPR@0.1% FPR, averaged):

  | Method | PSNR | Stochastic regen | Deterministic regen | Pix2Pix | MagicBrush | ControlNet-inpaint | SVD image-to-video |
  |---|---|---|---|---|---|---|---|
  | DWTDCT | 40.46 | 0.09 | 0.00 | 0.04 | 0.04 | 0.56 | 0.01 |
  | DWTDCTSVD | 40.40 | 3.12 | 1.43 | 3.82 | 30.84 | 50.04 | 0.76 |

  For comparison, VINE-R scores 99.66 (stochastic regeneration) and 93.04 (ControlNet).
- The authors say "Neither high bit accuracy nor AUROC alone guarantees a high true positive rate (TPR) at a low FPR".
- They also note "the implementations we employed for DWTDCT, DWTDCTSVD, and RivaGAN support CPUs exclusively". The library is not named.

**Watermark Anything paper (classical baseline under geometric and valuemetric groups)**
- On COCO, DWTDCT reaches PSNR 37.0. Its TPR / bit accuracy (%) are:

  | Condition | TPR | Bit accuracy |
  |---|---|---|
  | No attack | 77.1 | 91.4 |
  | Geometric | 0.0 | 50.5 |
  | Valuemetric | 13.6 | 58.1 |
  | Inpainting | 47.8 | 81.7 |
  | Splicing | 0.8 | 59.9 |

- WAM reaches 99.3 TPR and 91.8 bit accuracy under geometric attacks — [arXiv 2411.07231](https://arxiv.org/html/2411.07231) (opened).

**invisible-watermark's own README**
- For the frequency methods: JPEG, noise, brightness, overlay and mask "Pass"; "crop 7x5" "Fail"; "Resize 50%" "Fail"; "Rotate 30 degress" "Fail". The README says the methods "are not robust to resize or aspect ratio changed crop" — [ShieldMnt/invisible-watermark](https://github.com/ShieldMnt/invisible-watermark) (opened).

**SynthID-Image (2025)** omits classical baselines entirely and compares only neural post-hoc methods (see Q3) — [arXiv 2510.09263](https://arxiv.org/html/2510.09263v1) (opened).

**omnisealbench (Meta)**
- The repository was "archived by the owner on Jun 18, 2026". The common code is MIT and per-model licences vary.
- Image models: DCTDWT (the only classical one), HiDDeN, InvisMark, FNNS, MBRS, CIN, SSL WM, WAM, PixelSeal and TrustMark. Video: RivaGAN and VideoSeal. Audio: AudioSeal and WavMark.
- The leaderboard is at [HF space facebook/omnisealbench](https://huggingface.co/spaces/facebook/omnisealbench). PyPI `omnisealbench` 0.1 was uploaded 2025-06-15.
- Source: [facebookresearch/omnisealbench](https://github.com/facebookresearch/omnisealbench) (opened); PyPI API.

**MarkDiffusion**
- It is accepted to JMLR as vol. 27, no. 204 (2026); the update is dated 2026.07.11. It is Apache-2.0, `pip install markdiffusion`, v1.0.2 (GitHub release 2026-05-19).
- It contains 11 in-generation latent-diffusion methods: Tree-Ring, Ring-ID, ROBIN, WIND, SFW, Gaussian-Shading, GaussMarker, PRC, SEAL, VideoShield and VideoMark.
- Image attacks include Rotation, CrSc, noise, blur, JPEG, brightness, mask, overlay, adaptive noise, diffusion purification and neural-codec compression. It has no post-hoc or classical methods — [THU-BPM/MarkDiffusion](https://github.com/THU-BPM/MarkDiffusion) (opened).

**WatermarkLab**
- It is a "toolkit for benchmarking blind robust image watermarking". Version 0.1.22 was uploaded to PyPI on 2025-11-15; the PyPI author is Jiale Chen.
- Classical methods: DctDwt and DctDwtSvd. Neural post-hoc: RivaGAN, StegaStamp, TrustMark, InvisMark and VINE. In-generation: Tree-Ring, GaussianShading and StableSignature.
- Attacks: 44 configurations in 7 groups (compression, adversarial, noise, blur, geometric, colour, diffusion regeneration), plus 34 differentiable attackers.
- Metrics: BER, TPR@x%FPR, PSNR, SSIM, LPIPS and others. Licence: "MIT License with Additional Terms".
- Sources: [watermarklab.github.io](https://watermarklab.github.io) (opened); PyPI API.

### Inferences
- The benchmark results line up with the user's observations. Chance-level bit accuracy under geometric attacks (WAM: 50.5%) matches "no synchronisation". Low valuemetric TPR (WAM: 13.6%) matches the colour-change failures.
- Modern benchmarks use TPR at a fixed low FPR (0.1%) rather than BER at a fixed wPSNR. Results from the user's wPSNR-40-dB / BER framework are therefore not directly comparable with WAVES, W-Bench or omnisealbench numbers. To compare against literature, report TPR@0.1% FPR with a calibrated threshold as well.
- PSNR is similar across the benchmarks: about 37–40.5 dB for DWT-DCT(-SVD) in WAM and W-Bench. This is in the same regime as the user's wPSNR 40 dB, but wPSNR and PSNR differ, so the match is not exact.

### Gaps
- No StirMark 4.0 release date was found on the page.
- Per-attack WAVES numbers for DWT-DCT exist only as a figure (Fig. 31) with no table.
- W-Bench's classic-distortion results for DWTDCT and DWTDCTSVD are in figures without numbers.
- The omnisealbench leaderboard numbers for DCTDWT could not be retrieved, because the HF Space is a dynamic app.
- None of the benchmarks clearly names the library behind its DWT-DCT baseline. Given the CPU-only note and the common method names, invisible-watermark is likely [UNVERIFIED].

## Q5. Reputable open-source implementations: URL, maintainer, licence, last release, algorithm

### Takeaway
On the classical side, there are only two widely used, packaged Python libraries. Both are unmaintained as packages (last PyPI release 2023) and both are DWT-DCT-SVD QIM variants with no synchronisation. No reputable maintained library implements QIM/STDM/RDM, template synchronisation, or moment-invariant image watermarking. On the neural side, Meta's videoseal repo is the strongest maintained option: it is MIT, its image models range from 96 to 1024 bits, and it was updated in 2026. Adobe TrustMark is the best-packaged option: PyPI release in Sept 2026, MIT, 100 bits, in C2PA.

### Cited Findings
Metadata: GitHub REST API and PyPI JSON API on 2026-11-03, unless noted. "Last push" is the date of the latest repository activity; "Last release" is the latest PyPI upload or GitHub release.

**Classical (DWT, DCT, SVD)**

**invisible-watermark (import name `imwatermark`)**
- URL: https://github.com/ShieldMnt/invisible-watermark
- Maintainer: ShieldMnt; the PyPI author is Qingquan Wang
- Licence: MIT
- Last release: PyPI 0.2.0 (2023-07-06). GitHub releases stop at 0.1.5 (2021-02-01). Last push 2023-09-23. About 2.0k stars.
- Algorithm (from source): `dwtDct` takes Haar DWT and 4×4 DCT blocks and quantises the maximum non-trivial coefficient; `dwtDctSvd` applies QIM to s[0]; both mark only the U channel. `rivaGan` is RivaGAN (32 bits). The library requires images of at least 256×256.
- Notes: the README says it is "still experimental". It is used by the CompVis Stable Diffusion v1 `txt2img.py` (`wm = "StableDiffusionV1"`, method `dwtDct`) and by Hugging Face diffusers' SDXL watermarker (48-bit message, `dwtDct`) — [CompVis txt2img.py](https://github.com/CompVis/stable-diffusion/blob/main/scripts/txt2img.py); [diffusers SDXL watermark.py](https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion_xl/watermark.py) (sources opened).

**blind_watermark**
- URL: https://github.com/guofei9987/blind_watermark
- Maintainer: Guo Fei
- Licence: MIT
- Last release: PyPI 0.4.4 (2023-04-08); GitHub releases stop at 0.2.1 (2022). Last push 2026-03-25. About 14.8k stars.
- Algorithm: DWT-DCT-SVD QIM on s[0] and s[1] over all of YUV, with a keyed shuffle. The extractor needs `wm_shape` (the payload length).
- Notes: `recover.py` provides `estimate_crop_parameters` and `recover_crop`. Both use `cv2.matchTemplate` against the original image, so they are not blind — [recover.py](https://github.com/guofei9987/blind_watermark/blob/master/blind_watermark/recover.py) (opened).

**PyWavelets**
- URL: https://github.com/PyWavelets/pywt
- Maintainer: PyWavelets developers
- Licence: MIT [licence from general knowledge; PyPI JSON gave no licence string]
- Last release: 1.10.0 (2026-09-07)
- Algorithm: a transform library only. It provides no watermarking.

**imWatermark (PyPI) and PyWatermark (PyPI)**
- URLs: Mamdasn/imWatermark; ieshaan12/watermark
- Maintainers: individuals
- Licence: MIT
- Last release: 0.0.2 (2021) and 0.1.4 (2020) respectively
- Notes: hobby-level; not reputable choices. Do not confuse imWatermark with invisible-watermark's `imwatermark` import name.

**Lightricks "ltmarx" HF Space (`core/dmqim.ts`)**
- Language: TypeScript
- Algorithm: dither-modulation QIM with soft and hard decisions
- Notes: [UNVERIFIED]. Seen only as a search hit; the Space returned 401.

**Neural (post-hoc encoder/decoder)**

**videoseal**
- URL: https://github.com/facebookresearch/videoseal
- Maintainer: Meta FAIR
- Licence: MIT (code and model, per README)
- Last release: last push 2026-07-02. PyPI `videoseal` 1.0.1 was uploaded 2025-07-21 and predates the PixelSeal and ChunkySeal releases. There are no GitHub releases.
- Algorithm and models: VideoSeal v0.0 (96 bits), v1.0 (256 bits), PixelSeal (256 bits) and ChunkySeal (1024 bits). Image and video are supported (`model.embed` / `model.detect`).

**watermark-anything (WAM)**
- URL: https://github.com/facebookresearch/watermark-anything
- Maintainer: Meta FAIR
- Licence: MIT
- Last release: the repository is archived; last push 2025-06-20. There is no PyPI package.
- Algorithm: localised watermarking with 32 bits; supports multiple messages and masks.

**trustmark**
- URL: https://github.com/adobe/trustmark
- Maintainer: Adobe (John Collomosse)
- Licence: MIT (code and models, per README; the GitHub API reports NOASSERTION)
- Last release: PyPI 0.9.2 (2026-09-08); GitHub `rust-v0.3.0` (2026-09-29); last push 2026-11-03
- Algorithm: 100-bit payload with BCH options. Variants are Q and P (plus C in C2PA). Implementations exist in Python, JavaScript (decode), Rust and C++ (ONNX).

**InvisMark**
- URL: https://github.com/microsoft/InvisMark
- Maintainer: Microsoft
- Licence: MIT
- Last release: last push 2026-04-13; no releases
- Algorithm: neural, registered in C2PA. Its payload is reported as 100 bits in the SynthID paper; 256 bits is [UNVERIFIED].

**VINE**
- URL: https://github.com/Shilin-LU/VINE
- Maintainer: Shilin Lu / NTU (ICLR 2025)
- Licence: NOASSERTION
- Last release: last push 2026-03-27; no releases
- Algorithm: built on a generative prior, robust to editing; also hosts W-Bench.

**StegaStamp**
- URL: https://github.com/tancik/StegaStamp
- Maintainer: M. Tancik
- Licence: MIT
- Last release: last push 2023-12-08
- Algorithm: neural, 100 bits (per the SynthID paper's listing). Research code.

**HiDDeN (PyTorch reimplementation)**
- URL: https://github.com/ando-khachatryan/HiDDeN
- Maintainer: A. Khachatryan
- Licence: MIT
- Last release: last push 2024-08-08
- Notes: research code. It is not the original authors' release [UNVERIFIED which is official].

**MBRS**
- URL: https://github.com/jzyustc/MBRS
- Licence: none
- Last release: last push 2024-06-25
- Notes: ACM MM'21 research code.

**In-generation only** (not usable for watermarking existing images or frames):
- stable_signature: Meta; licence NOASSERTION; last push 2026-09-02.
- tree-ring-watermark (YuxinWenRick): MIT; last push 2024-03.
- MarkDiffusion: Apache-2.0; v1.0.2.

Supporting findings:
- In the C2PA registry, the only open-source watermark implementations with C2PA identifiers are TrustMark and InvisMark; the others are commercial — [C2PA registry JSON](https://spec.c2pa.org/softbinding-alg-list/softbinding-algorithm-list.json) (opened).
- Meta's ChunkySeal paper says robust methods are generally limited to "a few hundred bits". ChunkySeal embeds 1024 bits "while maintaining similar robustness and image quality" to Video Seal — [arXiv 2510.12812](https://arxiv.org/html/2510.12812v2) (snippet).

### Inferences
- A 512-bit blind payload is above the native capacity of TrustMark (100), WAM (32), SynthID-O (136, closed), VideoSeal v1.0 and PixelSeal (256). The only maintained, reputable library model that can carry 512 bits plus ECC parity in one image is ChunkySeal (1024 bits), from the videoseal repo.
- A rate-1/2 code over 512 information bits fits exactly in 1024. This would make the user's ECC comparison meaningful on a geometric-robust carrier.
- Its image-quality regime (PSNR/wPSNR) must be re-measured against the user's wPSNR 40 dB constraint. That fit has not been checked.
- ChunkySeal and PixelSeal must be installed from the GitHub repo, not from the PyPI `videoseal` 1.0.1 package. This follows from the release dates.
- Both classical libraries are fine as "classical baseline" references. Benchmarks use exactly these method names, but neither is maintained as a package (no PyPI release since 2023).

### Gaps
- The exact checkpoint licence text for PixelSeal and ChunkySeal (model cards) was not opened. The README says MIT for "the model" generally.
- The InvisMark payload and its README were not opened.
- Whether OpenCV's contrib modules include any watermarking module was not checked directly in this session. None is known [UNVERIFIED].
- MATLAB toolboxes (e.g. Checkmark) are discontinued. No maintained MATLAB watermarking toolbox from a reputable group was found.

## Q6. Is there a maintained library for classical geometric-resilient watermarking (log-polar template, moments)? And what are realistic options for the user's setup?

### Takeaway
No such library was found. Searches on GitHub, PyPI and the wider web turned up no maintained, reputable implementation of template/log-polar, Fourier–Mellin, or moment-invariant image watermarking. The only industrial implementation of that architecture is Digimarc's proprietary one, described in its patents. Reputable libraries do provide registration building blocks (log-polar FFT registration in scikit-image, imreg_dft and OpenCV ports). Using them for watermark resynchronisation would still need a hand-written template embedder and detector, which violates the user's "library implementations only" rule. Under that rule, the realistic geometric-robust options are neural libraries; for 512 bits, that means ChunkySeal.

The colour-change failure has a specific, code-level cause in invisible-watermark: fixed-step QIM on the U channel only, with no gain or offset invariance. The cause is inferred below.

### Cited Findings
- A search for log-polar or Fourier–Mellin watermarking implementations found only template-matching (registration) code, not watermarking code:
  - [bemoregt/gplogpolarpoc](https://github.com/bemoregt/gplogpolarpoc), an OpenFrameworks C++ app (snippet);
  - [Smorodov/LogPolarFFTTemplateMatcher](https://github.com/Smorodov/LogPolarFFTTemplateMatcher), "OpenCV Fourier-Mellin algorithm implementation", MIT, last push 2022-04-08 (GitHub API).

  Watermarking-specific Fourier–Mellin detection appears only in patents, e.g. US 6,408,082 "Watermark detection using a fourier mellin transform" — [USPTO](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6408082) (snippet).
- scikit-image's gallery example "Using Polar and Log-Polar Transformations for Registration" shows the building block:
  - It uses `transform.warp_polar` (with `scaling='log'`) and `registration.phase_cross_correlation`, run on band-passed, Hann-windowed FFT magnitudes so that translation is ignored.
  - It recovered about 23.75° (true 24°) and a scale of about 1.390 (true 1.4).
  - Stated limitations: there is no clearly optimal parameter choice; log-polar registration on raw images failed when translation was present; and large scale changes (about 1.8–2×) distort the spectra.

  Source: [scikit-image example](https://scikit-image.org/docs/stable/auto_examples/registration/plot_register_rotation.html) (opened). scikit-image's latest is 0.26.0, with 0.27.0rc1 on 2026-10-27, under BSD (PyPI API).
- imreg_dft (Matěj Týč) provides DFT-based (Fourier–Mellin) image registration. It is BSD-licensed, its last PyPI release is 2.0.0 (2016-06-18) and its last GitHub push was 2023-03-09 — [matejak/imreg_dft](https://github.com/matejak/imreg_dft) (GitHub/PyPI API). It is effectively unmaintained.
- No reputable Python library for QIM, STDM or dither modulation was found. Search results returned papers and one TypeScript file in a Lightricks Hugging Face Space — [search hit](https://huggingface.co/spaces/Lightricks/ltmarx/blob/main/core/dmqim.ts) (snippet; 401 when opened).
- blind_watermark's crop and scale recovery is non-blind: it runs `cv2.matchTemplate` of the attacked image against the original — [recover.py](https://github.com/guofei9987/blind_watermark/blob/master/blind_watermark/recover.py) (opened).
- invisible-watermark's README admits the methods "are not robust to resize or aspect ratio changed crop". Its table shows "Rotate 30 degress: Fail" for both the frequency methods and RivaGAN — [README](https://github.com/ShieldMnt/invisible-watermark) (opened).
- In invisible-watermark's `dwtDctSvd` (source, opened): the U channel only; quantisation step `scale` (default 36) applied to s[0] of the 4×4 DCT of the Haar-LL band; bit 0 is placed at offset 0.25·scale and bit 1 at 0.75·scale; the decision boundary is 0.5·scale — [dwtDctSvd.py](https://github.com/ShieldMnt/invisible-watermark/blob/main/imwatermark/dwtDctSvd.py).
- Since 2005, theory has known that plain dither modulation is "largely vulnerable to amplitude scalings", and Rational Dither Modulation fixes gain attacks with a gain-invariant adaptive step [Univ. Vigo RDM record](https://portalcientifico.uvigo.gal/documentos/5fa08253299952440aaea2ec?lang=en) (snippet). STDM is likewise "very sensitive to valumetric scaling" [UCL thesis](https://discovery-pp.ucl.ac.uk/id/eprint/1443976) (snippet).
- Neural libraries are trained with geometric augmentations and report high geometric robustness. WAM trains with resize, crop, rotate, flip and perspective, and reaches 99.3% TPR under geometric attacks [arXiv 2411.07231](https://arxiv.org/html/2411.07231) (opened). SynthID-Image reports colour-transform TPR of about 99.7–100% for TrustMark-Q, StegaStamp and SynthID-O [arXiv 2510.09263](https://arxiv.org/html/2510.09263v1) (opened).

### Inferences
**Why invisible-watermark fails on about half the frames under global colour changes.** This is derived from the source code and is not tested here.
- For a smooth block, s[0] is close to the magnitude of the DCT DC term. With pywt's orthonormal Haar, LL ≈ 2u. With OpenCV's orthonormal 4×4 DCT, DC = (1/4)·Σ ≈ 8u. So a uniform shift δ in the U channel, as produced by a global hue or white-balance change, shifts s[0] by about 8δ.
- A bit is decoded wrongly when that shift, taken modulo the step Q, lands in (Q/4, 3Q/4). That happens for δ between about Q/32 and 3Q/32, modulo Q/8. With the default Q = 36, a mean U shift of about 1.1–3.4 levels flips nearly all bits at once, and a shift of 4.5 levels brings them back.
- Over a random set of colour edits, therefore, roughly half the frames fall in the "flip" window and half do not. This matches "fails on about half the frames". Gain changes (saturation) scale (U−128) and have a similar, block-dependent effect.
- How to test it: measure the mean U shift per attacked frame and check whether failures cluster where frac(8δ/Q) ∈ (0.25, 0.75).
- Corollary: the colour failure is a property of the embedding rule (no offset or gain invariance, single chroma channel). It is not a property of the ECC. Stronger ECC cannot fix a fully correlated, near-all-bits flip.
- Some error correction is possible without modifying the library. A known pilot or sync sub-message could detect the global inversion, since the flip is coherent across bits. This would be project glue code, not a new algorithm, but it is still hand-written logic.

**Realistic implementation options under the "reputable library, unmodified" rule**
- (a) **Keep invisible-watermark `dwtDctSvd`** as the classical baseline and accept or document its known failure classes: geometric (no synchronisation) and colour (offset or gain on U).
  - Its geometric failures can only be removed with a non-blind step, for example blind_watermark's `estimate_crop_parameters`, which uses the original image. That breaks the user's blind-extraction rule.
  - A blind fix would need a template or self-reference sync. No reputable library provides one.
- (b) **Move the main experiments to a neural carrier with library support and geometric robustness.**
  - ChunkySeal (1024 bits, videoseal repo, MIT) is the only maintained option found that fits 512 information bits plus ECC parity.
  - PixelSeal or VideoSeal v1.0 (256 bits) would need two messages or a reduced payload. TrustMark (100 bits, PyPI, MIT, in C2PA) is the most production-grade option but too small.
  - The wPSNR 40 dB strength calibration would need to be redone, since these models have their own strength or scaling factors. Whether that is exposed was not verified.
- (c) **Hybrid diagnostic.** Use scikit-image's log-polar registration only as an analysis tool, for example to measure how much geometric distortion an attack introduced. Do not use it as part of the watermark.
- (d) **Benchmarking harness.** WatermarkLab (PyPI 0.1.22, includes DctDwt, DctDwtSvd, TrustMark, InvisMark, StegaStamp, VINE, with 44 attacks) or omnisealbench (archived, but includes DCTDWT, TrustMark, WAM and PixelSeal) could provide library-based attacks and metrics comparable with the literature. WatermarkLab's "MIT License with Additional Terms" should be read before use.

### Gaps
- No maintained, reputable library was found for moment-invariant (Zernike, pseudo-Zernike, Tchebichef) image watermarking. This absence is based on searches that returned only papers. A more exhaustive GitHub code search was not possible without the `gh` CLI or authenticated API.
- No maintained library for RDM, STDM or QIM image watermarking was found.
- It was not verified whether ChunkySeal's or PixelSeal's embedding strength can be tuned to hit an exact wPSNR target, nor their behaviour on 1024×1024 frames versus their training resolution.
- The U-channel offset-flip explanation is an analytical inference from the source code. It has not been verified empirically on the user's data in this session.
