# Error-correcting codes in classical (signal-processing) image watermarking, 1996–2026

Scope: non-neural image watermarking and the general watermarking theory that applies to images. The requester's setting is a 256–512-bit message, a DWT-DCT-SVD embedder (invisible-watermark `dwtDctSvd`) and neural embedders, with 5G LDPC, polar, LTE turbo, BCH, RS and repetition codes compared at matched wPSNR. Their observation was that LDPC r1/2 beat r1/3 at fixed quality.

Source quality: I read the full text of Darbon/Sankur/Maître 2001, Bastug/Sankur (LDPC), Rey et al. 2003 (block turbo codes), Chen & Wornell 2001 (QIM), Miller/Doërr/Cox 2004 (dirty-paper trellis codes), Schlauweg et al. 2008 and Coumou & Sharma 2006, after extracting the PDFs to text. For everything else I saw only abstracts, index records or search snippets, and those findings are marked "(abstract-level)" or "(snippet-level)".

## 1. Empirical studies: which codes were used, what gains were measured, and when repetition beats algebraic codes

### Takeaway
Early studies (2000–2004) agree on three things:
- Raw watermark channels are very noisy, with BER of 0.1–0.5 being common.
- Algebraic codes such as BCH collapse once the channel BER rises above roughly 0.1–0.2. Repetition is then the "last resort", and the best results come from an inner repetition code (or a soft spreading/combining stage) under a stronger outer code.
- Soft-decoded iterative codes (LDPC, block turbo codes) gave the largest measured gains: about 2x payload, roughly 3 dB over BCH, and JPEG survival extended from QF≈50 to QF≈25–30.

### Cited Findings

**Darbon, Sankur & Maître (SPIE EI 2001, vol. 4314, pp. 663–672). Full text read.**
- Watermark channel error rates "between 0.1 and 0.5 are not uncommon". Capacity is about 0.01 bit/pixel. Signal-to-interference figures quoted from Marvel are −30 to −10 dB. Messages are "typically below a hundred bits", too short for turbo codes to work well. — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Analysis on a binary symmetric channel (64-bit message) compared BCH (127,64), (255,63), (511,67) and (1023,66). These BCH codes "fail for channels worse than pb = 0.1" and then produce more errors than no coding at all. — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Repetition overtakes BCH above a raw BER of "around 0.15–0.20". The comparison was a (32,1) repetition code against 8× BCH(255,9) and 2× BCH(1023,36) for a 64-bit signature. Below that threshold, BCH is "orders of magnitude better". — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Repetition codes correct up to pb = 0.5 because dmin = n. For any other code (dmin < n), the largest correctable pb is "roughly 0.25" (citing Desset et al.). — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Concatenation at equal redundancy (16-bit message, redundancy factor 31) compared three schemes: (31,1) repetition over 506 sites, BCH(511,19) over 511 sites, and BCH(31,6) + (5,1) repetition over 555 sites. The concatenation wins for 0.16 < pb < 0.22, and repetition wins above that. The paper's conclusion gives the window where concatenation helps as pb ≈ 0.15–0.30. — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Experiments used 20 Petitcolas images with a Zhao–Koch-style DCT substitution scheme and a 64-bit message. With R = 13 repetitions, the signature decodes down to JPEG Q = 40; without repetition it fails at Q = 70. — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- With BCH(511,58) (about 13x redundancy), the outcome is "dichotomic": either the message is decoded exactly or it fails completely. — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Second scheme (16-bit payload, JPEG attack):
  - BCH(31,16) + 3× repetition performs well down to Q = 60.
  - Pure BCH(127,16) fails for Q < 40, where the raw BER reaches 0.20.
  - Concatenation must be dimensioned "judiciously". For example, BCH(15,7)/(15,7)/(7,4) with 3 repetitions did worse than every other option.
  — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Earlier results summarised in the same paper:
  - Hernández et al. (2-D multipulse spatial scheme, Gaussian noise plus Wiener filtering, Lena): for a BER of 1e-4, uncoded needs about 420 pixels/bit, while BCH(63,36) needs about 240 pixels/bit.
  - Marvel (steganography) used Reed–Solomon codes, turbo codes and Retter codes with an interleaver, reaching a BER of about 1e-2 at 0.16 bit/pixel.
  - Mukherjee et al. report that the coding advantage "turns into a loss" when the host is rendered at higher quality.
  — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)

**Other early studies**
- Baudry, Delaigle, Sankur, Macq & Maître, "Analyses of error correction strategies for typical communication channels in watermarking", *Signal Processing* 81(6):1239–1250, 2001 (abstract/review-level):
  - studies very high error rates and the trade-off between BCH and repetition codes;
  - hard-decision extraction is modelled as a binary symmetric channel and soft-decision extraction as an additive Gaussian channel;
  - soft decoders are a Viterbi decoder for convolutional codes and "a new soft-BCH decoding algorithm";
  - the coding scheme concatenates BCH and repetition.
  — [dblp](https://dblp.dagstuhl.de/rec/journals/sigpro/BaudryDSMM01.html); [zbMATH/MaRDI review record](https://portal.mardi4nfdi.de/wiki/Item:Q5941324)
- Desset, Macq & Vandendorpe, *Signal Processing: Image Communication* 17(5):409–421, 2002 (abstract-level):
  - target channels have BER 0.1–0.5;
  - "The repetition code lowers the huge channel BER, as no other code can do this part of the job", and a BCH code then reduces the BER further;
  - BCH has moderate complexity, while "more efficient coding schemes based on soft decoding are far more complex".
  — [UCLouvain record](https://dial.uclouvain.be/pr/boreal/object/boreal:41836)

**Bastug & Sankur, "Improving the Payload of Watermarking Channels via LDPC Coding" (manuscript for IEEE Signal Processing Letters, received Nov. 2002). Full text read.**
- Setup: spread-spectrum embedding in global DFT magnitudes or block-DCT coefficients, using 65,536 cover coefficients. Strength is fixed at α = 0.2 for about 38 dB PSNR. Each code bit is extracted with a soft maximum-likelihood detector (Weibull model for DFT, generalised Gaussian for DCT). — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf)
- LDPC and BCH were both set to rate 1/2, with the chip rate χ adjusted so that coding plus repetition fills all coefficients. The best BCH codes were (511,250,31) for DFT and (63,30,6) for DCT. — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf)
- To reach a BER of 1e-3 in the DFT channel, LDPC needs χ = 96, BCH needs 176 and pure repetition needs 256. That is about 2x the BCH payload and 2.7x the repetition payload. — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf)
- "There exists a crossover point, at which a code ceases to be useful and repetition code takes over". It occurs at χ ≥ 70 for LDPC and χ ≥ 140 for BCH, "hence a 3 dB advantage accrues for the LPDC". — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf)
- Under JPEG with 256-bit messages, BER < 1e-3 holds down to Q = 70 with LDPC. BCH starts failing at Q = 85, and repetition needs Q = 100. — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf)

**Rey, Amis, Dugelay, Pyndiah & Picart, "Enhanced robustness in image watermarking using block turbo codes", SPIE EI 2003 (vol. 5020). Full text read.**
- Setup: 75 images of 512×512, distortion fixed at about 38 dB, blind extraction. The code is a BCH product code (Chase–Pyndiah iterative soft decoding) concatenated with a repetition code. — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- With a 121-bit payload, the product code BCH(16,11)² + soft repetition decodes without error down to JPEG 30%, while repetition alone shows errors at 50%. The abstract states the first error appears at about 25% against about 50%. BCH(128,120) or BCH(256,123) + repetition beats repetition alone but loses to the product code. — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- From their review of prior work: "Repetition codes are not efficient in terms of error correction since they exhibit a coding gain of zero dB", and "For very low JPEG quality (under 20%), repetition codes seem the best solution". — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- They confirm earlier results by Kesal, Mıhçak, Koetter & Moulin (Turbo Codes symposium 2000) that "BTC coding scheme outperforms all other coding solutions for watermarking applications". — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)

**Turbo and convolutional codes (abstract- or title-level only)**
- Pereira, Voloshynovskiy & Pun (ICIP 2000, pp. 671–673) use turbo codes with DCT-magnitude embedding and fold JPEG quantisation tables into the embedding. — [Univ. Geneva record](https://archive-ouverte.unige.ch/unige:47873)
- Balado, Pérez-González & Scalise (ICIP 2001, pp. 1003–1006) apply turbo codes to sample-level DCT watermarking at low SNR, with DCT statistical models that allow theoretical bounds. — [Univ. Vigo record](https://portalcientifico.uvigo.gal/documentos/5fa081e7299952440aae97ad?lang=en)
- Hernández, Delaigle & Macq (SPIE 2000) "Improving data hiding by using convolutional codes and soft-decision decoding". Title-level only. — [cited in Rey et al.](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)

**Later applied studies (abstract- or snippet-level)**
- Yi & Lee (2003, Korea): LDPC on DWT coefficients; "the trade-off between chip rate and LDPC code rate" determines watermark quality. — [KoreaScience](https://koreascience.or.kr/article/JAKO200311921988363.pub?lang=ko)
- IEICE 2015 report: compared BCH, RS, Sourlas and LDPC codes; BCH + LDPC was the best concatenation. — [IEICE](https://www.ieice.org/ken/paper/201501293Bvd/eng/)
- Saeki, Nozaki & Kawamura (IEICE 2017): non-binary LDPC codes; longer codes correct more errors but are more exposed to clipping and lower stego quality. — [IEICE](https://www.ieice.org/ken/paper/20170306rbSA/eng/)
- Abdul, Carré & Gaborit (EURASIP J. Info. Security 2013): colour wavelet watermarking compared repetition, Hamming, BCH and RS codes. Concatenated non-binary block codes do well against JPEG, noise and brightness changes, and Sudan list decoding of RS does well against hue and saturation changes. Authors were taken from a reference list. — [EURASIP JIS](https://jis-eurasipjournals.springeropen.com/articles/10.1186/1687-417X-2013-1)
- AFRICON 2019: compared RS and BCH for colour JPEG watermarking. — [Univ. Johannesburg record](https://pure.uj.ac.za/en/publications/performance-analysis-for-reed-solomon-codes-and-bose-chaudhuri-ho/)
- arXiv 2021: DCT + BCH watermarking; its literature list covers Hamming, BCH, RS, convolutional, LDPC and turbo codes. — [arXiv 2108.01612](https://arxiv.org/pdf/2108.01612)

**Polar codes (abstract-level)**
- Evsutin, Ivanov & Dzhanashia, IEEE Access 12:118154–118168, 2024: template watermark with neural-network extraction, protected by polar codes. They embed 650–1600 bits in 1920×1080 images at PSNR 39.66 dB, with an extraction-error probability of about 0.01 after transfer through real social networks. — [DOAJ](https://doaj.org/article/5b00baaef8044d8d9e8a2fdd1b4e02ee); [HSE](https://publications.hse.ru/en/articles/957670835)
- Lee & Shin, J. KICS 45(6), 2020: 128 information bits at polar rate 1/2. The study is about frozen bits acting as a key: a mismatched frozen set gives an information BER of 12.5–53.125%. It is a security study, not a robustness comparison. — [KICS](https://journal.kics.or.kr/digital-library/37189)

### Inferences
- Combining the measured thresholds: hard-decision algebraic codes help when the raw per-coded-bit BER is below about 0.1. Concatenating repetition with BCH helps at about 0.15–0.30. Pure repetition (or heavy spreading) is best above about 0.2–0.3 and at very low JPEG quality (below about 20–40, depending on the scheme).
- Burst-like or "fading" attacks (cropping, local filtering) favour interleaving, erasure-aware codes and RS. Solanki et al. and Schlauweg et al. (section 5) also say RS is preferable only when insertion/deletion errors arrive in bursts.
- Soft iterative codes (LDPC, block turbo codes) gave the largest gains in every study I found that measured them: about 3 dB or 2x payload over BCH (Bastug & Sankur), and JPEG robustness extended by 20–25 QF points (Rey et al.).
- I found no classical study that compares 5G LDPC, polar, LTE turbo, BCH, RS and repetition side by side at matched image quality. The requester's benchmark appears to have no direct classical precedent at that breadth.

### Gaps
- Not retrieved: the full text of Baudry et al. 2001 (their exact soft-BCH and Viterbi gains), Desset et al. 2002 (exact BER curves), Hernández/Rodríguez/Pérez-González (*Signal Processing* 2000), Pereira et al. 2000, Balado et al. 2001 and Kesal et al. 2000. All are paywalled or the fetch failed.
- No classical paper I found reports numbers for polar codes against LDPC or turbo codes in image watermarking. The polar-code papers found are 2020–2024 and do not benchmark other codes.

## 2. Theory: watermarking as communication with side information (Costa, QIM, capacity, dirty-paper and trellis codes)

### Takeaway
Blind watermarking is channel coding with side information at the encoder (Costa's "writing on dirty paper"). The capacity of the Gaussian case does not depend on the host interference.
- Chen & Wornell showed that uncoded binary STDM sits about 13.6 dB from capacity at a low error probability.
- At least 9.3 dB of that gap can be recovered through channel coding, vector quantisation and non-dithered quantisation. The remaining ≤4.3 dB QIM gap can be closed with distortion compensation.
- So channel coding is, in theory, the largest single lever. Informed-coding (dirty-paper) trellis codes carried 1380 bits in 240×368 images, where blind coding at the same fidelity failed.

### Cited Findings

**Chen & Wornell, IEEE Trans. Inf. Theory 47(4):1423–1443, May 2001. Full text read.**
- Distortion-constrained Gaussian embedding equals power-constrained communication over a Gaussian channel with host side information known at the encoder, which is Costa's channel. The capacity, expressed in DNR, is "independent of the" host signal. — [Chen & Wornell 2001](https://dsp-group.mit.edu/wp-content/uploads/2024/11/QuantizationIndexMod.pdf)
- Regular QIM (no distortion compensation) "is within 4.3 dB of capacity at low rates" and approaches capacity asymptotically at high rates. Distortion-compensated QIM (DC-QIM) achieves capacity. — [Chen & Wornell 2001](https://dsp-group.mit.edu/wp-content/uploads/2024/11/QuantizationIndexMod.pdf)
- At low rates, the minimum rate-normalised DNR for reliable embedding is about 1.4 dB. Their figure of merit normalises distortion-to-noise by rate, the analogue of Eb/N0. — [Chen & Wornell 2001](https://dsp-group.mit.edu/wp-content/uploads/2024/11/QuantizationIndexMod.pdf)
- Uncoded binary STDM with uniform scalar quantisers is "about 13.6 dB from capacity" at the paper's reference error probability (the exponent was lost in text extraction; see their Fig. 11). The paper continues: "One can reduce this gap by at least 9.3 dB through channel coding, vector quantization, and nondithered quantization", and the remaining ≤4.3 dB "can be closed with distortion compensation". — [Chen & Wornell 2001](https://dsp-group.mit.edu/wp-content/uploads/2024/11/QuantizationIndexMod.pdf)
- "It is fairly easy to close the gap between uncoded STDM ... and capacity by about 6 dB using practical channel codes and distortion compensation." — [Chen & Wornell 2001](https://dsp-group.mit.edu/wp-content/uploads/2024/11/QuantizationIndexMod.pdf)
- Comparisons with other schemes:
  - uncoded spread LBM is about 16 dB from capacity, 2.43 dB worse than STDM;
  - in their example (host-to-noise ratio 30 dB), STDM's SNR advantage over additive spread spectrum is 28.8 dB, because spread spectrum suffers host interference;
  - in the non-blind case (host known at the decoder), coded dither modulation with scalar quantisers is "at most 1.53 dB from capacity".
  — [Chen & Wornell 2001](https://dsp-group.mit.edu/wp-content/uploads/2024/11/QuantizationIndexMod.pdf)

**Scalar Costa scheme and turbo TCQ**
- Eggers, Bäuml, Tzschoppe & Girod, "Scalar Costa scheme for information embedding", IEEE TSP 51(4):1003–1019, 2003, analyse a practical scalar Costa scheme (SCS) with state-of-the-art codes (abstract-level). — [Typeset](https://typeset.io/pdf/scalar-costa-scheme-for-information-embedding-4odm36koo9.pdf)
- Bäuml et al. (SPIE 2003) report that binary SCS is near-optimal in capacity for 1-D embedding with an i.i.d. Gaussian host and AWGN attack (snippet-level). — [FAU record](https://cris.fau.de/publications/123530044)
- Le Guelvouit, *Traitement du Signal* 25(6):459–467, 2008 (abstract-level):
  - turbo trellis-coded quantisation (two parallel TCQs) "for an embedding rate of 1/1 and to reach an error bit rate lower than 10^-5 ... is 5.5 dB better than SCS";
  - on images (spread-transform DCT with waterfilling), 1200 watermarks were extracted from 1200 images without error under Gaussian noise;
  - better than the reference scheme under JPEG, but "not completely robust to scaling".
  — [IIETA](https://www.iieta.org/journals/ts/paper/10.3166/TS.25.459-467)

**Dirty-paper trellis codes: Miller, Doërr & Cox, IEEE TIP 13(6):792–807, 2004. Full text read.**
- The scheme embeds 1380 bits in 240×368 images with a dirty-paper trellis code. Each bit maps to N = 12 low-frequency block-DCT coefficients, and the trellis has 64 states with 64 arcs per state. Decoding uses a Viterbi decoder that picks the path with maximum correlation, and the scheme was tested on 2000 images. — [Miller, Doërr & Cox 2004](https://www.eurecom.fr/publication/1414/download/mm-doergw-040601.pdf)
- Message error rate (MER) by configuration:

| Coding | Embedding | Watson distance | MER |
|---|---|---|---|
| Blind | Blind | 200 | 99.85% |
| Blind | Informed | 201 | 12.5% |
| Informed | Blind | 101.8 | 56.55% |
| Informed | Informed | 101.5 | 0% |
| Informed | Informed, with perceptual shaping | 31.6 | 0.35% |

  — [Miller, Doërr & Cox 2004](https://www.eurecom.fr/publication/1414/download/mm-doergw-040601.pdf)
- Robustness was defined as MER < 20%. Under JPEG, blind coding stays robust only down to about QF 65, while informed coding stays robust down to QF 33. They also note that lattice/QIM codes "exhibit only limited robustness against simple valumetric scaling". — [Miller, Doërr & Cox 2004](https://www.eurecom.fr/publication/1414/download/mm-doergw-040601.pdf)
- The earlier ICIP 2002 paper ("Dirty-paper trellis codes for watermarking") introduced trellises where each bit value can be coded by several alternative arcs. — [Eurecom](https://www.eurecom.edu/en/publication/1823)

**Textbooks and tutorials**
- Cox, Miller, Bloom, Fridrich & Kalker, *Digital Watermarking and Steganography*, 2nd ed. (Morgan Kaufmann, 2008). Catalogue listings give these chapters: "Message Coding" (ch. 4), "Watermarking with Side Information" (ch. 5), "Structured/Practical Dirty-Paper Codes" (ch. 6) and "Analyzing Errors" (ch. 7). Titles vary by listing. — [Elsevier](https://shop.elsevier.com/books/digital-watermarking-and-steganography/cox/978-0-12-372585-1); [catalogue TOC](https://ebook.library.uitm.edu.my/Record/480/TOC)
- Miller et al. state that their trellis is similar to the E_TRELLIS8/D_TRELLIS8 system described in that book. — [Miller, Doërr & Cox 2004](https://www.eurecom.fr/publication/1414/download/mm-doergw-040601.pdf)
- Moulin & Koetter, "Data-hiding codes", Proc. IEEE 93(12):2083–2126, 2005, is the standard tutorial on code design for data hiding (bibliographic-level only). — [Typeset](https://typeset.io/papers/data-hiding-codes-36xs9do1i9)
- Pérez-González, Hernández & Balado, "Approaching the capacity limit in image watermarking: a perspective on coding techniques for data hiding applications" (*Signal Processing*, 2001): concatenated and turbo coding approach the hidden-channel capacity at sample level, with experiments (snippet-level). — [record](https://data.zhenzhi.com/details/1/874011655)
- Zhao (McMaster MASc thesis, 2020): nested LDGM–LDPC (dirty-paper style) code tested at embedding rate R = 0.001953, i.e. 1/512. — [McMaster](https://macsphere.mcmaster.ca/items/09c3095e-8054-420e-ab13-728748aab076)

### Inferences
- The invisible-watermark `dwtDctSvd` embedder is binary scalar QIM (dither modulation without distortion compensation).
  - It quantises the largest singular value of each 4×4 DCT block of the DWT approximation band with step `scale`. Each block makes a hard 0/1 decision, and the per-bit decision is the mean of those votes. Coded bits are assigned to blocks cyclically (`num % wmLen`).
  - Source: local library file `/home/ale/watermaking_tests/.venv/lib/python3.14/site-packages/imwatermark/dwtDctSvd.py`, lines 49–51, 64, 73 and 80.
  - In Chen & Wornell's terms, this is uncoded STDM-like QIM plus repetition. Theory therefore expects a large coding headroom, potentially 6–9 dB, but only if decoding is soft and the code operates in its waterfall region.
- Dirty-paper and informed coding is the classical route to large payloads (about 1000+ bits). It would require modifying the embedder, which the requester's rule keeps unmodified for baselines. It is therefore context for the report, not a candidate to test.

### Gaps
- Not read directly: Costa 1983, Moulin & O'Sullivan 2003 (IEEE TIT 49(3)) capacity expressions and the numbers in Moulin & Koetter's tutorial. Cited only via Chen & Wornell and Miller et al.
- The exact SCS turbo-coded operating points (WNR in dB at a given BER) from Eggers et al. 2003 were not retrieved.

## 3. The fixed-quality trade-off: redundancy costs embedding strength (energy per coded bit); optimal code rate

### Takeaway
Yes, the classical literature reports the requester's effect. At fixed distortion and fixed cover size, a longer codeword means fewer repetitions per coded bit, so less energy per coded bit. A stronger (lower-rate) code wins only if its coding gain outweighs that loss.
- Rey et al. 2003 observed exactly this: longer product codes lost because repetitions were divided by 4.
- Gu, Huang & Shi (2003, 2005) went further and argued that ECC generally fails to improve robustness under an imperceptibility constraint, except against cropping and jitter.
- Studies that normalise fairly (Bastug & Sankur, Darbon et al.) found strong codes helpful only above a per-coded-bit SNR threshold. Below it, repetition is better.

### Cited Findings
- Rey et al. 2003, at fixed 38 dB distortion:
  - "there is a much larger degradation when the code length is increased for codes with the same minimum distance ((16,11)² and (32,26)²)";
  - "as we increase code length for a given minimum distance the coding gain increases. However, this coding gain is not sufficient to compensate the loss due to the decrease in the replication factor L which is here divided by 4. The received signal energy per information bit is divided by 4";
  - "as we increase code length in order to achieve higher pay loads, there is a significant penalty in terms of robustness";
  - for a 512×512 image the replication factor is bounded at L < 57 for a 256-bit codeword and L < 15 for a 1024-bit codeword.
  — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- Rey et al. 2003 also state the general mechanism: "the introduction of an error correcting code ... increases the number of bits to hide; consequently the number of repetitions of each bit of the watermark decreases in the same proportion". — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- Darbon et al. 2001 on fair comparison:
  - "Whenever an (n,k) error correcting code is used, this figure Eb/N0 must be scaled by k/n for a fair comparison with the uncoded case";
  - because embedding strength cannot be adjusted continuously in watermarking, they compare codes at equal "number of pixels dedicated to carry one bit", i.e. an equal site budget;
  - repetition and BCH must be "judiciously dimensioned, given the available number of insertion sites and the payload size".
  — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Bastug & Sankur used fixed strength (α = 0.2, about 38 dB PSNR) and fixed sites (65,536). Payload was traded against chip rate and code rate. "The role of the repetition code is to increase the output SNR at the decoding stage ... providing more reliable soft demodulation outputs used by the belief network decoder." — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf)
- Gu, Huang & Shi, ISCAS 2003, "Analysis of the role played by error correcting coding in robust watermarking" (abstract-level): "the redundancy introduced by ECC will lead to a decrease of the watermark strength". Their theory and experiments conclude that "ECC cannot effectively improve the robustness of watermarking against most attacks", especially signal processing and noise, and "The only exception is attacks such as cropping". — [NJIT record](https://researchwith.njit.edu/en/publications/analysis-of-the-role-played-by-error-correcting-coding-in-robust-/)
- Huang, Gu & Shi, *Acta Automatica Sinica* 31(5):683–692, 2005, "Robustness of watermarking: Is error correcting coding effective" (abstract-level): same conclusion, with cropping and jitter as the exceptions; ECC should not be treated as a universal robustness measure. — [NJIT Digital Commons](https://digitalcommons.njit.edu/fac_pubs/19584)
- Mukherjee et al. (1998, as summarised by Darbon et al.): at high host quality, coding "causes loss of payload capacity without a commensurate increase in its security". — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Chen & Wornell measure performance as rate-normalised DNR (the Eb/N0 analogue). — [Chen & Wornell 2001](https://dsp-group.mit.edu/wp-content/uploads/2024/11/QuantizationIndexMod.pdf)

### Inferences
- **The requester's result matches the literature.** LDPC r1/2 beating r1/3 at fixed wPSNR is the same mechanism Rey et al. report.
  - Per the library code, every 4×4 block of the `dwtDctSvd` approximation band is modified regardless of codeword length. Image distortion therefore depends on `scale`, not on n. Calibrating strength per codeword length to wPSNR 40 dB should give nearly the same `scale` for every n.
  - The only lever left is votes per coded bit, roughly (number of blocks)/n.
  - For a 512-bit message, r1/2 (n = 1024) against r1/3 (n = 1536) means 4 votes against about 2.67. Because of the cyclic assignment, some coded bits get 3 votes and others 2. This is my calculation from the code; image size was not checked.
- **This is not a law of coding theory.** With ideal soft combining on an AWGN-like channel, repetition has 0 dB coding gain (Rey et al.). A capacity-approaching rate-1/3 code should then match or beat rate-1/2 code + repetition at equal total energy. When r1/2 wins in practice, it points to information lost before the decoder. Candidate causes:
  1. Hard 0/1 per-block decisions averaged into a vote fraction, a coarse quantised LLR. Even vote counts also produce ties: 2–2 maps to bit 1 because `0.5*255 > 127`.
  2. The per-coded-bit SNR falling below the code's threshold, which is the crossover described by Bastug & Sankur and by Darbon et al.
  3. Non-Gaussian, block-correlated JPEG-type errors.
  4. Finite-length effects at n ≈ 1–1.5k.
- The literature's prescription is to compare codes at a fixed site/energy budget (Darbon) or at rate-normalised SNR (Chen & Wornell). The requester's matched-wPSNR protocol already does the former.

### Gaps
- I found no paper that derives the optimal code rate as a closed-form function of document-to-watermark ratio and attack strength for practical finite-length codes. Comesaña et al. 2006 (section 4) optimise distortion compensation with repetition but do not optimise outer-code rate.
- The full texts of Gu/Huang/Shi were not available, so I could not check which codes, payloads or normalisations they used.

## 4. Soft- vs hard-decision decoding

### Takeaway
Every study that compared the two found soft information essential:
- turbo and product decoding fed with hard-decoded repetitions "decrease significantly" (Rey et al.);
- LDPC gains rely on maximum-likelihood soft demodulation with host-statistics models (Bastug & Sankur);
- weighting repetitions by estimated channel state helps on non-stationary, fading-like attack channels (Kundur & Hatzinakos, Comesaña et al.);
- RS codes, unlike RA codes, usually cannot benefit from soft decoding (Schlauweg et al., describing Solanki et al.).

### Cited Findings
- "When the repetition codes are hard-decoded, the performances of the turbo decoder decrease significantly." The Chase–Pyndiah decoder approximates the LLR from a near-ML search over test patterns built by flipping the least reliable positions. — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- Baudry et al. 2001 model hard extraction as a binary symmetric channel and soft extraction as an additive Gaussian channel, and present a soft Viterbi decoder for convolutional codes and a new soft-BCH algorithm (abstract/review-level). — [MaRDI/zbMATH record](https://portal.mardi4nfdi.de/wiki/Item:Q5941324)
- Bastug & Sankur: soft ML detection uses Weibull-modelled DFT magnitudes and generalised-Gaussian DCT coefficients, with parameters estimated from the marked image in 16 regions. — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf)
- Kundur & Hatzinakos, IEEE TSP 49(10):2383–2396, 2001 (abstract-level): attacks are treated as fading interference; the paper uses diversity and channel estimation, with a non-stationary parallel binary symmetric channel model. — [record](https://data.zhenzhi.com/details/1/886617488)
- Kundur & Hatzinakos 1998 (*Optics Express*) interleave test-pattern bits to estimate the local channel and weight each repetition, as described by Darbon et al. — [Darbon et al. 2001](https://lre.epita.fr/dload/papers/darbon.01.ei.pdf)
- Voloshynovskiy, Deguillaume, Pereira & Pun (SPIE 2001) argue that more repetitions may not help with linear combining under impulsive noise, and propose estimating the post-attack noise distribution (snippet-level; fetch failed). — [Univ. Geneva PDF](https://cvml.unige.ch/publications/postscript/2001/VoloshynovskiyDeguillaumePereiraPun_spie2001.pdf)
- Comesaña, Pérez-González & Balado, IEEE TSP 54(2):585–600, 2006 (abstract-level): exact BER analysis of distortion-compensated dither modulation with repetition. A weighted Euclidean-distance decoder and a vector distortion-compensation parameter give "significant performance gains". — [Univ. Vigo record](https://portalcientifico.uvigo.gal/documentos/5fa08319299952440aaeb2a9?lang=en); [preprint](https://gpscuvigo.webs.uvigo.gal/sites/default/files/publications/dcdm_uvigo05.pdf)
- Solanki et al. use RS codes or repeat-accumulate (RA) codes. RS is preferable only for bursty insertion/deletion errors, and "RS codes in contrast to RA codes usually cannot benefit from soft decoding". — [Schlauweg et al. 2008](https://www.int.uni-rostock.de/fileadmin/user_upload/publications/SITIS08_schlauweg.pdf)

### Inferences
- **Feed soft values to the decoders.** For the requester's `dwtDctSvd` pipeline, the most literature-supported change is to give LDPC, turbo and polar decoders a soft value per coded bit rather than thresholded bits. Options:
  - the vote fraction, with ties treated as LLR = 0 (erasure);
  - better, a per-block distance of `s[0] mod scale` to the decision boundary, computed outside the unmodified library.

  Hard-decision input costs roughly 2 dB in AWGN. That is a standard coding-theory figure, not sourced in the watermarking papers above. It could on its own explain part of the r1/2-over-r1/3 ranking.
- RS and BCH with hard decoding are expected to rank below soft LDPC and turbo codes, unless the error pattern is bursty (block-level or cropping), where RS's symbol structure helps.

### Gaps
- I found no image-watermarking paper that quantifies the soft-vs-hard gap in dB for the same code and embedder. Rey et al. show it only qualitatively in a figure.

## 5. Synchronisation: insertion/deletion and desynchronisation-resistant codes

### Takeaway
Ordinary ECC corrects substitutions only. Desynchronisation (from content-adaptive selection, feature points or small geometric shifts) causes insertions and deletions that turn into error bursts. The classical answers are:
- erasure-aware codes with puncturing (Solanki et al., RS or RA codes);
- Davey–MacKay "watermark codes" (an inner insertion/deletion code with soft resynchronisation, under an outer LDPC or turbo code), used by Coumou & Sharma and Schaathun;
- trellis or dynamic-programming decoders (Swart et al.; Schlauweg et al.).

In image watermarking, global geometric attacks were mostly handled by templates and invariant domains rather than by codes.

### Cited Findings
- Solanki, Jacobsen, Madhow, Manjunath & Chandrasekaran, IEEE TIP 13(12):1627–1639, 2004 (abstract-level):
  - locally adaptive embedding (only DCT coefficients above a threshold) desynchronises encoder and decoder;
  - non-embedded locations are treated as erasures and insertions/deletions as errors;
  - RS codes are used for the block-based scheme and repeat-accumulate codes for selective embedding;
  - the hidden data survive JPEG, AWGN, wavelet compression, resizing and limited tampering.
  — [UCSB record](https://vision.ece.ucsb.edu/node/384)
- Schlauweg, Pröfrock & Müller, SITIS 2008. Full text read.
  - Three approaches exist: concatenated coding (Davey–MacKay), dynamic programming (Swart et al.'s parallel Viterbi decoders) and punctured coding (Solanki).
  - Puncturing "fails to correct de-synchronization in second generation watermarking schemes, if the number of selected embedding locations is much smaller than the number of host signal samples".
  - Their trellis decoder at rate 1/2 beats the others when the insertion/deletion probability exceeds 1%. Below 1%, Davey–MacKay "seems to be better".
  — [Schlauweg et al. 2008](https://www.int.uni-rostock.de/fileadmin/user_upload/publications/SITIS08_schlauweg.pdf)
- Coumou & Sharma, ICME 2006 (speech; journal version IEEE TIFS 3(2):153–165, 2008). Full text read.
  - The scheme is a 16-ary outer LDPC code (K = 25, N = 100, rate 1/4) with a Davey–MacKay sparse inner code (n = 10), for an overall rate of 0.10.
  - It runs at about 8 bit/s with QIM on pitch and survives GSM 06.10 at 13 kbps and AMR at 5.1 kbps.
  - The paper calls synchronisation "the Achilles heel of a majority of current watermarking systems".
  — [Coumou & Sharma 2006](https://www.cecs.uci.edu/~papers/icme06/pdfs/0000849.pdf)
- Davey & MacKay (IEEE TIT 47(2):687–698, 2001): an inner "watermark" code allows probabilistic resynchronisation and passes soft outputs to an outer code. — [Background, arXiv 1204.3238](https://arxiv.org/pdf/1204.3238)
- Schaathun (UCD seminar 2008): image attacks look like pixel insertions and deletions. New results use a Davey–MacKay inner code with outer non-binary turbo codes (abstract-level). — [UCD](https://www.ucd.ie/mathstat/research/seminars-old/seminararchive/seminars2008/250208hans-georgschaathun)
- Buttigieg & Briffa: codebook and marker-sequence design for synchronisation-correcting codes, with image watermarking as the motivation (snippet-level). — [slides](https://api.sambuz.com/doc/codebook-and-marker-sequence-design-for-synchronization-ppt-presentation-269197)
- Rey et al. 2003 added "resynchronization bits" (about one per coded bit, α = 1) and used FFT/Hough and block-matching resynchronisation for global and local geometric distortion, separate from the ECC. — [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- Lefèvre, Carré & Gaborit (2022) show "how a specific code can address image cropping" (abstract-level). — [XJTLU record](https://scholar.xjtlu.edu.cn/en/publications/codes-and-watermarks/)

### Inferences
- For block-grid embedders like `dwtDctSvd`, small shifts and crops misalign the 4×4 block grid and the cyclic bit assignment. That produces insertion/deletion-like or burst errors that substitution codes cannot fix. If the requester's attack set includes geometric attacks, a synchronisation layer (template, invariant domain or ID code) matters more than the choice among LDPC, polar and turbo codes.

### Gaps
- I found no paper applying Davey–MacKay or marker codes to a DWT-DCT-SVD image watermark with numbers. The image-domain ID-code work found is seminar- or slide-level, apart from Solanki et al. and Schlauweg et al.

## 6. Has interest declined? Surveys, and whether studying ECC in watermarking is worthwhile

### Takeaway
Classical ECC-in-watermarking research clustered in about 1999–2005: Darbon, Baudry, Desset, Hernández/Pérez-González, Kesal/Moulin, Pereira/Pun, Bastug/Sankur, Rey, Solanki, Chen/Wornell and Miller/Doërr/Cox. After 2010 there are only sporadic applied papers (2013 EURASIP, 2015/2017 IEICE, 2019 AFRICON, 2020 KICS, 2021 arXiv, 2024 IEEE Access with polar codes) and one 2022 book chapter. I found no dedicated 2010–2026 survey of ECC in image watermarking. The literature leaves two things open: a fair, matched-quality, multi-code comparison with modern codes, and how codes interact with soft extraction. That makes the requester's study a reasonable contribution, provided it normalises energy and uses soft inputs.

### Cited Findings
- The 2022 Wiley chapter "Codes and watermarks" (Lefèvre, Carré & Gaborit, *Multimedia Security 1*, pp. 77–127) treats robust watermarking as "the classical application framework for the use of codes in watermarking". — [XJTLU record](https://scholar.xjtlu.edu.cn/en/publications/codes-and-watermarks/)
- The sceptical position, that ECC does not effectively improve robustness against most attacks under an imperceptibility constraint, comes from Gu, Huang & Shi (2003) and Huang, Gu & Shi (2005). — [NJIT 2003](https://researchwith.njit.edu/en/publications/analysis-of-the-role-played-by-error-correcting-coding-in-robust-/); [NJIT 2005](https://digitalcommons.njit.edu/fac_pubs/19584)
- The positive position, that soft iterative codes double payload or add about 20 JPEG-QF points at fixed PSNR, comes from Bastug & Sankur and from Rey et al. — [Bastug & Sankur](https://www.eurecom.fr/publication/1343/download/cm-bastah-040201.pdf); [Rey et al. 2003](https://www.eurecom.fr/publication/1360/download/mm-reych-030121.pdf)
- Recent polar-code use is driven by real-channel robustness (social networks) and by key or security uses of frozen bits. — [Evsutin et al. 2024](https://doaj.org/article/5b00baaef8044d8d9e8a2fdd1b4e02ee); [Lee & Shin 2020](https://journal.kics.or.kr/digital-library/37189)

### Inferences
- The two camps disagree mainly because of normalisation and decoder input. Studies that held the site/energy budget fixed and used soft decoding (Bastug & Sankur, Rey et al.) found gains. The sceptical study argued from reduced watermark strength. Its normalisation details could not be checked.
- The requester's protocol (fixed message, strength calibrated to wPSNR 40 dB per codeword length, no-ECC baseline, blind extraction) matches the fair-comparison practice of Darbon and Rey. Their r1/2-over-r1/3 finding is the expected classical result when votes per coded bit are few and the decoder input is coarse.
- ECC study is worthwhile when the per-coded-bit raw BER sits in the 1e-2 to about 0.15 window where codes have leverage. It matters less when attacks push the raw BER above about 0.2 (repetition territory) or when errors are desynchronisation-driven (ID codes or templates needed).
- Recommended reporting, following Darbon and Chen & Wornell: report the raw per-coded-bit BER for each attack. That places each condition relative to the published thresholds: BCH collapse at about 0.1, the repetition crossover at about 0.15–0.20, and the BSC limit of about 0.25 for dmin < n codes.

### Gaps
- No systematic bibliometric data (paper counts per year) were found to quantify the decline. The "clustered in 1999–2005" statement is my reading of the publication dates of the sources found, not a measured trend.
- No 2010–2026 survey dedicated to ECC in watermarking was found. General robust-watermarking surveys were not checked for ECC sections.
