# ECC and payload design in deployed / industry image watermarking and provenance standards (status as of Nov 2026)

Scope: what production watermarking systems and standards do about payload size, error-correcting codes (ECC), and identifier recovery vs. presence detection. The goal is to judge whether ECC on watermarks matters in practice. Requester's setup: a fixed header tag ("AI-generated") plus a per-image random ID, comparing ECC families on dwtDctSvd vs. Meta ChunkySeal/Pixel Seal.

Conventions: **[V]** = verified from a primary source fetched in this session (spec, code, README, paper, official blog). **[S]** = secondary source or search-snippet only, not verified against the primary. **[M]** = vendor marketing claim. Inferences are kept in the "Inferences" subsections. Retrieval date: 2026-11-04.

---

## Q1. C2PA soft binding: how watermarks recover manifests, which algorithms are registered, and what payload/ECC they specify

### Takeaway
C2PA treats an invisible watermark as an **opaque, algorithm-specific lookup key** (the soft-binding `value`, a CBOR byte string). Manifests are recovered by an exact `alg` + `value` match at a Soft Binding Resolution API. The C2PA spec sets **no payload size, ECC, or false-positive requirement**: these are left entirely to each registered algorithm's own documentation. Of the 57 registered soft-binding algorithms (48 watermarks, 9 fingerprints; 27 watermarks cover images), only a handful state a payload size: 32, 40, 44/88, 100 (TrustMark) and 256 bits. None of the list entries mentions ECC. Google SynthID, OpenAI, Amazon and first-party Meta are **not** on the list.

### Cited Findings
**Spec definitions and rules (C2PA Technical Specification 2.5, Oct 2026; earlier versions were 2.4 in Apr 2026, 2.3 in Dec 2025 and 2.2 in May 2025) [V]**
- Soft binding is defined as "A content identifier that is either (a) not statistically unique, such as a fingerprint, or (b) embedded as an invisible watermark in the identified digital content" (§2.3.14). An invisible watermark is information "which can be used, for example, to uniquely identify the asset or to store a reference to a C2PA Manifest" (§2.4.3). A "Durable Content Credential" is one with soft bindings that "enable its discovery in a manifest repository" (§2.4.1). — [C2PA Spec 2.5](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)
- "A soft binding shall not be used as a hard binding." A manifest may contain at most one hard binding and "zero or more" soft-binding assertions. — [C2PA Spec 2.5 §12.2](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)
- The soft-binding assertion (`c2pa.soft-binding`) has the following fields:
  - `alg` (a string from the soft binding algorithm list)
  - `blocks[]`, each holding a `scope` (region or timespan) and a `value` (bstr, "in algorithm specific format")
  - optional `alg-params` (bstr), `bindingMetadata`, and zero-filled `pad`/`pad2`

  The spec contains **no field or rule about payload length, ECC or detection thresholds**. — [C2PA Spec 2.5 §16.3.7](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)
- "The format of alg-params and value fields are algorithm specific and described via a human readable information page referenced by informationalUrl." — [C2PA Spec 2.5 §16.3.7.4](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)
- Matching rule: "A soft binding assertion shall be considered a match if both the algorithm identifier (alg) and the value (value) … match … Matching is performed in the manner prescribed by the specified algorithm." The list is served at https://sbal.c2pa.org. — [C2PA Spec 2.5 §16.3.7.5.1](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)
- Watermarking actions:
  - `c2pa.watermarked.bound` is a watermark inserted "for the purpose of creating a soft binding".
  - `c2pa.watermarked.unbound` is a watermark inserted "without creating a soft binding", e.g. a pure AI-disclosure mark.
  - `c2pa.watermarked` is deprecated.
  - If `.bound` is present without a `c2pa.soft-binding` assertion, the claim is rejected with `assertion.action.softBindingMissing`.

  — [C2PA Spec 2.5 §14.10.4, §16.4.1.5](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)
- Recovered manifests: "Since most soft binding recovered manifests will contain a hard binding assertion that does not match the asset being looked up, it is to be expected that validation failures will be reported." Ingredients found this way carry `softBindingsMatched: true` and `softBindingAlgorithmsMatched`. — [C2PA Spec 2.5 §16.4.1.10](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)
- Spec 2.4 (Apr 2026) added a `c2pa.ai-disclosure` assertion for machine-readable AI transparency, and a `c2pa.repository-receipt` assertion. — [C2PA Spec 2.5 Annex F.2](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html)

**Soft Binding Resolution API (2.5) [V]**
- Endpoints:
  - `GET/POST /matches/byBinding`: base64 `value` plus `alg`, with `maxResults` (default 10). It returns zero or more active-manifest IDs.
  - `POST /matches/byContent`: the server computes the binding from an uploaded asset.
  - Optional `hintAlg`/`hintValue` let a second soft binding (e.g. a fingerprint) assist resolution.
  - Results can carry a `similarityScore`: "An integer score in the range (0-100) representing the strength of match, if appropriate."

  — [C2PA Soft Binding API 2.5](https://spec.c2pa.org/specifications/specifications/2.5/softbinding/Decoupled.html)
- Optional decentralized Key-Value store on a distributed ledger: "The key is the soft binding value, such as may be incorporated in an asset via a watermark. The value is a URI of an endpoint implementing the soft binding resolution API." — [C2PA Soft Binding API 2.5 §2](https://spec.c2pa.org/specifications/specifications/2.5/softbinding/Decoupled.html)
- Anti-spoofing: "A check may performed to verify that the recovered manifest matches the query asset bearing the watermark. This mitigates the possibility of attacking the watermarking system to spoof (e.g., transfer) a watermark from one asset to another." The recommended way is to store a fingerprint in the manifest and compare it. — [C2PA Soft Binding API 2.5 §1.2.2.3](https://spec.c2pa.org/specifications/specifications/2.5/softbinding/Decoupled.html)

**Soft Binding Algorithm List (SBAL), snapshot of 2026-11-04 [V]**
- 57 entries: 48 watermark, 9 fingerprint. None is deprecated. 9 entries declare a resolution API. The latest entry was dated 2026-10-28. — [c2pa-org/softbinding-algorithm-list JSON](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json)
- Image-capable watermarks (27): Digimarc Validate (#1), ATSC A/336, Adobe TrustMark Q/C (2024-05-17), Steg.AI (#7), Trufo PawPrint, Overlai, castLabs, TrustMark P (2025-02-05), IMATAG `com.imatag.lamark.v1` (2025-02-26), NAGRA NexGuard, Mentaport, Microsoft InvisMark (2025-10-12), ContentLens ×3, LumaTrace, MarkAny, AIWatermark PixelSeal, Sasha, VerdaAI, BlockFact, Museblossom, Reconize VideoSeal, Diker Sigi, TrustMark F ("FiLMCAM Conditional Access Watermarking", 2026-10-14), QuatMark. Adobe also registered FlowMark (video) and HierMark (audio) on 2026-08-13. — [SBAL JSON](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json)
- Entries that state a payload:

  | Entry | Media | Stated payload |
  |---|---|---|
  | Trufo PawPrint | image/audio/video | "44/88 bit payload" |
  | AIWatermark PixelSeal | image | "Embeds a 256-bit payload" |
  | Reconize VideoSeal | image/video | "a 256-bit identity payload" |
  | ImmoStory VideoSeal | video | "256-bit payload (64-bit public ImmoStory constant + 192-bit per-video identifier)" |
  | BlockFact | audio/image/video | "a 32-bit lookup key derived from blockchain registration hash" |
  | AIDR SilentCipher | audio | "40-bit payload (public AIDR brand byte 0xAD + 32-bit per-clip identifier)" |
  | DeepMark Vigil | audio | "128-bit-per-second" |
  | QuatMark | image | "a compact record identifier" (no size given) |

  No SBAL entry mentions ECC. — [SBAL JSON](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json)
- Inclusion criteria require only that the algorithm "support embedding, extracting, or both, of a soft binding identifier for the purpose of manifest recovery". There are **no robustness, capacity or false-positive criteria**. — [SBAL README](https://github.com/c2pa-org/softbinding-algorithm-list)
- No SBAL entry exists for Google/SynthID, OpenAI, Amazon or first-party Meta. Meta's models appear only via third-party deployments (AIWatermark, Reconize, ImmoStory). — [SBAL JSON](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json)

### Inferences
- In the C2PA soft-binding path, a watermark is useful only if the **identifier is recovered exactly**: lookup is an exact `value` match unless the algorithm defines a tolerant matching. This is exactly the regime where ECC matters, so the requester's "exact ID recovery" framing matches the C2PA durable-content-credential use case.
- C2PA pushes the ECC choice and the false-positive control onto each vendor. A study comparing ECC families answers a design question C2PA explicitly leaves open.
- The two-part designs registered in 2026 (ImmoStory: 64-bit constant + 192-bit ID; AIDR: 8-bit brand byte + 32-bit ID) are structurally the same as the requester's "fixed header + random ID" scheme. Neither describes ECC on the ID.
- `similarityScore` and `maxResults>1` indicate that resolvers may return approximate or nearest matches, e.g. Hamming-nearest IDs. This is a soft-decision alternative to ECC (database-side decoding) that a deployer can use when the ID space is sparse.

### Gaps
- The informational pages of IMATAG, Digimarc Validate, Steg.AI and AIWatermark (403 when fetched) were not read, so their payload/ECC formats are unknown.
- No C2PA document found sets a minimum ID length, collision probability or FPR for watermark soft bindings.
- Whether Adobe's Content Authenticity resolver uses exact or Hamming-tolerant matching for TrustMark IDs was not found.

---

## Q2. Adobe TrustMark: payload sizes, BCH variants, data bits left, robustness

### Takeaway
TrustMark carries a fixed **100-bit raw payload**: 96 bits of data+ECC plus 4 version bits, of which 2 are reserved and 2 select the schema. It offers four BCH schemas: 40/61/68/75 data bits correcting 8/5/4/3 errors. The default is variant Q with BCH_5, i.e. a 61-bit ID. In the reference code, **"watermark present" is simply "BCH decoding succeeded"**, so the ECC doubles as the detector. Adobe's own sizing argument: about 96% bit accuracy at 42–45 dB, i.e. about 4 flips per 100 bits, which BCH corrects at a cost of about 30 bits.

### Cited Findings
- "TrustMark encodes a payload … of 100 bits." The version bits "comprise two reserved (unused) bits, and two bits encoding an integer value 0-3 that specifies the data schema: 0: BCH_SUPER, 1: BCH_5, 2: BCH_4, 3: BCH_3." — [TrustMark README](https://github.com/adobe/trustmark)
- Schema table:

  | Encoding | Protected payload | ECC bits | Bit flips corrected |
  |---|---|---|---|
  | BCH_5 | 61 bits | 35 | 5 |
  | BCH_4 | 68 bits | 28 | 4 |
  | BCH_3 | 75 bits | 21 | 3 |
  | BCH_SUPER | 40 bits | 56 | 8 |

  "The decoder automatically detects the data schema." "Note that even 40 bits gives a key space of around one trillion." The default configuration is "variant Q, 100% strength, BCH_5 error correction". — [TrustMark CONFIG.md](https://github.com/adobe/trustmark/blob/main/python/CONFIG.md)
- Code details:
  - `BCH_POLYNOMIAL = 137`, built as `BCH(t, 137)` with t = 5/4/3/8.
  - The schema is read from "last 2 bits of the 4 version bits".
  - If `bch_decoder.decode` returns −1, or if correction touches byte-alignment padding ("Byte alignment adds zero bits that were never transmitted"), decode returns `wm_present=False`. Otherwise it returns `True`.

  — [trustmark/datalayer.py](https://github.com/adobe/trustmark/blob/main/python/trustmark/datalayer.py)
- Model variants:

  | Variant | PSNR (dB) | Decoder |
  |---|---|---|
  | Q (default) | 43–45 | ResNet-50 |
  | B | 43–45 | ResNet-50 |
  | C | 38–39 | ResNet-18 |
  | P | 48–50 | ResNet-50 |

  Strength `WM_STRENGTH` defaults to 1.0. 1.5 is used to survive printing; 0.7–0.8 still decodes "in low noise situations (including passing through most social content platforms)", gaining "almost 5dB". — [CONFIG.md](https://github.com/adobe/trustmark/blob/main/python/CONFIG.md); [FAQ](https://github.com/adobe/trustmark/blob/main/FAQ.md)
- Robustness claim (Adobe FAQ, citing the paper): "in default operation (variant Q) TrustMark can exceed 96% bit accuracy at around 42-45dB PSNR quality under severe noise degradations. Given 100 bits of raw payload, that allows for 4 bit flips which are correctable using BCH error correction at a cost of around 30 bits, providing a protected identifier space of around 70 bits. The paper compares several state of the art watermarking techniques which can achieve only around 70% bit accuracy at this level of payload and robustness." Variant P: "95% bit accuracy at 48-50dB PSNR." — [TrustMark FAQ](https://github.com/adobe/trustmark/blob/main/FAQ.md) [V, author claim]
- Robust to "18 different noise sources within the Kornia Python lib", JPEG, and "random four-sided cropping up to around 20% image area loss". Works on images down to about 150 px on the short side. — [FAQ](https://github.com/adobe/trustmark/blob/main/FAQ.md) [V, author claim]
- C2PA usage: "TrustMark encodes a random identifier via one of the encoding types … to reflect the identifier within the C2PA manifest using a soft binding assertion." **Signpost mode**: "the encoding should be `Encoding.BCH_SUPER` and the payload contain an integer identifier that describes the co-present watermark", taken from the SBAL. — [trustmark/c2pa README](https://github.com/adobe/trustmark/blob/main/c2pa/README.md)
- Anti-spoofing: Adobe recommends checking recovered metadata against "a digital fingerprint (perceptual hash) stored within the metadata". TrustMark is open, non-steganographic (no key), and ships removal code. — [FAQ](https://github.com/adobe/trustmark/blob/main/FAQ.md)
- Publication: arXiv 2311.18297 (Nov 2023), later published at ICCV 2025. Python package 0.9.x: v0.9.0 (2025-10-01) added "Bounding box detection and localisation". The newest entry, 0.9.3, notes a "Validation edge case fixed in BCH error correction library". — [README](https://github.com/adobe/trustmark); [CHANGELOG](https://github.com/adobe/trustmark/blob/main/python/CHANGELOG.md)

### Inferences
- Polynomial 137 = x^7+x^3+1, so the code is a BCH over GF(2^7) (natural length 127) shortened to 96 bits. That is why parity = 7·t (35/28/21/56 bits).
- The 2 schema bits are **not ECC-protected**. One flip there routes the word to the wrong BCH decoder, and the read is then rejected or misdecoded.
- Ideal bounded-distance false-accept probability on a uniformly random 96-bit word is V(96,t)/2^(96−k):

  | Schema | False-accept per read |
  |---|---|
  | BCH_SUPER | ≈ 2.0×10⁻⁶ |
  | BCH_5 | ≈ 1.9×10⁻³ |
  | BCH_4 | ≈ 1.3×10⁻² |
  | BCH_3 | ≈ 7.0×10⁻² |

  These are my calculations. The padding check lowers them somewhat, and real decoder outputs on unwatermarked images are not i.i.d. uniform, so they must be measured empirically. So **ECC-as-detector gives only modest FPR at the default BCH_5**. This is a concrete reason why a separate header/known-bit check or statistical detector (as in the requester's header tag) is worth keeping alongside the ECC.
- TrustMark is the clearest public industrial evidence that ECC on watermark IDs is practically used. It uses a classical bounded-distance BCH, not LDPC/polar/turbo, and a fixed 100-bit frame. It shows no evidence of soft-decision decoding.

### Gaps
- The paper's per-attack bit-accuracy tables were not re-read here. The numbers above are from Adobe's FAQ.
- No public word-error-rate (exact ID recovery) figures per BCH schema were found.
- No details were found on TrustMark F (FiLMCAM) payload or ECC.
- Whether Adobe's production services (Content Authenticity app, Firefly) use BCH_5 or another schema was not found.

---

## Q3. Other industry systems: what is public about payload and error correction

### Takeaway
Public payload/ECC detail exists only for a few systems:
- **Microsoft InvisMark**: 256 bits, with UUID + ECC.
- **Digimarc** (patents): about 47 data bits + 24 CRC, convolutional/other FEC expanded to about 1024 coded bits, with chip spreading.
- **Google SynthID-O**: a 136-bit payload, but no ECC described.
- **Meta**: research models carrying 96/256/1024 raw bits, with no ECC in the releases.
- **Stability/diffusers**: a fixed 48- or 136-bit dwtDct tag, no ECC.

Amazon, OpenAI, IMATAG, Steg.AI and Truepic publish no payload or ECC detail. The 2026 landscape is consolidating around **SynthID as a cross-vendor AI-disclosure watermark**: OpenAI, NVIDIA, Kakao and ElevenLabs adopted it, Apple coverage was announced, and over 180 billion images and videos have been marked. **C2PA soft-binding watermarks** with IDs (Adobe, Microsoft, Digimarc, others) are used for manifest recovery.

### Cited Findings
**Google SynthID**
- SynthID-Image is a post-hoc, model-independent system that is "currently watermarking all of Google's AI-generated imagery". It has been used on "over ten billion images and video frames" (paper, Oct 2025). — [SynthID-Image, arXiv 2510.09263](https://arxiv.org/abs/2510.09263) [V]
- Payload: "SynthID-O can encode 136-bit payloads within 512×512 pixel images." The payload serves "different generative models, users and deployment scenarios", and in the as-a-service setting "payloads need to be used to distinguish between different customers". Detection and payload are solved "separately". Detection uses a conformal p-value where "thresholding … at α guarantees a FPR of at most α". Evaluations are at 0.1% FPR. — [arXiv 2510.09263 (HTML)](https://arxiv.org/html/2510.09263v1) [V]
- ECC: the paper describes no BCH/repetition code for SynthID payloads. Baselines are evaluated "without any error code correction". — [arXiv 2510.09263](https://arxiv.org/html/2510.09263v1) [V; the last ~35% of the paper was not read]
- Robustness (SynthID-O):
  - TPR at 0.1% FPR: 99.98% (aggregate, random transforms), 99.72% (aggregate worst-case), 98.06% (combination worst-case).
  - Payload bit accuracy: 99.59% / 98.07% / 89.46% for the same settings.
  - Detection via payload matching (aggregate worst-case): 98.84–98.90%.

  — [arXiv 2510.09263](https://arxiv.org/html/2510.09263v1) [V]
- Security posture:
  - Detector access is restricted ("trusted testers", "through partnerships") and query rate-limited.
  - "our main goal is to make black-box attacks computationally infeasible at scale".
  - The paper notes open detectors make removal easy via adversarial examples.

  — [arXiv 2510.09263](https://arxiv.org/html/2510.09263v1) [V]
- Oct 7, 2026 (updated Oct 29): SynthID Detector is available "globally in English" for image, video and audio. It covers AI "from Google or our partners", naming OpenAI, NVIDIA, Kakao and Apple. Over "180 billion images and videos" and 240,000 years of audio have been watermarked. Verification in Search/Gemini/Chrome handles ">1 million requests daily". The post does not say whether the detector reports an identifier or only presence. — [Google blog, Oct 2026](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/synth-id-ai-content/) [V]
- Google I/O (May 2026): "companies like OpenAI, Kakao and ElevenLabs are bringing SynthID technology to more of their AI-generated content." SynthID verification in the Gemini app has been "used 50 million times", and Google is "adding verification for C2PA Content Credentials". — [Google I/O 2026: 100 announcements](https://blog.google/innovation-and-ai/technology/ai/google-io-2026-all-our-announcements/) [V]
- A forensic preprint reports that OpenAI announced SynthID adoption on 19 May 2026. It found SynthID in 36 of 200 GPT-Image-2 images, about 18%, implying a partial rollout at sampling time. — [arXiv 2607.05434](https://arxiv.org/pdf/2607.05434) [S, search snippet only]
- SynthID-Text (Nature, Oct 2024) is a generation-time scoring watermark detected by a threshold on a score, with no multi-bit payload. — [Dathathri et al., Nature 2024](https://www.nature.com/articles/s41586-024-08025-4) [from background knowledge; not re-fetched this session]

**Meta**
- Meta says it applies "both invisible watermarks and metadata embedded within image files" to photorealistic Meta AI images. It detects C2PA/IPTC "AI generated" signals from Google, OpenAI, Microsoft, Adobe, Midjourney and Shutterstock. Stable Signature is presented as FAIR research ("we're developing"). The post does not say which watermark is in production or what payload it carries. — [Meta Newsroom, Feb 2024 (upd. Apr 2025)](https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/) [V]
- Open models (videoseal repo): VideoSeal v0.0 has **96 bits** (Dec 2024). VideoSeal v1.0 has **256 bits** (Mar 2025, "Stable"). **PixelSeal** has 256 bits (arXiv 2512.16874) and **ChunkySeal** has **1024 bits** (arXiv 2510.12812); both were released Dec 2025. The README mentions no ECC. — [facebookresearch/videoseal](https://github.com/facebookresearch/videoseal) [V]
- "Meta Seal" is an MIT-licensed, open-weight umbrella (AudioSeal, VideoSeal, PixelSeal, ChunkySeal, SyncSeal, TextSeal, DistSeal, Stable Signature, WMAR, WMForger), framed for "scientific exploration". No official statement of production use by Meta products was found. — [Meta Seal page (via search snippet; page 404'd on fetch)](https://facebookresearch.github.io/meta-seal) [S]
- Third parties deploy Meta models as C2PA soft bindings with raw 256-bit payloads (AIWatermark PixelSeal, Reconize VideoSeal, ImmoStory VideoSeal). ImmoStory's layout:
  - "The first 64 bits are a fixed public constant, 0x484e32cf1da65dbf."
  - A video counts as theirs if at least "56 of these 64 bits" match.
  - The remaining 192 bits are a random ID that "resolves to the original C2PA manifest".
  - No ECC is stated.

  — [ImmoStory provenance page](https://immostory.ai/en/provenance) [V, vendor]; [SBAL](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json)

**Microsoft**
- InvisMark (Microsoft Responsible AI, WACV 2025): "successful encoding of 256-bit watermarks", PSNR ≈ 51 dB, SSIM ≈ 0.998, ">97% bit accuracy across various image manipulations". It enables "embedding of UUIDs with error correction codes" with "near-perfect decoding success rates even under challenging image distortions". The abstract gives no exact WER. — [arXiv 2411.07795](https://arxiv.org/abs/2411.07795) [V]
- InvisMark (`com.microsoft.invismark.1`, image/video) and WavMark (audio) were registered on the C2PA SBAL on 2025-10-12. — [SBAL](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json) [V]
- The Azure OpenAI "Content Credentials" doc (updated June 2026) describes only a C2PA manifest:
  - `description: "AI Generated Image"`
  - `softwareAgent: "Azure OpenAI DALL-E"` or `"Azure OpenAI ImageGen"`
  - `when`

  The fetched page does not mention an invisible watermark. — [Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/content-credentials) [V]
- 2024 press: Azure OpenAI announced invisible watermarks on DALL·E images, "identified by specialized detection tools", robust to resizing/cropping. No payload or ECC was disclosed. — [Neowin](https://www.neowin.net/news/invisible-watermarks-are-coming-to-images-generated-using-dall-e-on-azure-openai-service/) [S/M]

**OpenAI**
- OpenAI attaches C2PA Content Credentials to images and is adopting SynthID (see the Google sources above). OpenAI's help page returned 403. A search summary of it states that images carry C2PA plus SynthID. — [OpenAI Help 8912793](https://help.openai.com/en/articles/8912793-content-credentials-for-images-and-video) [S, not fetched]
- No OpenAI-owned watermark payload or ECC information was found.

**Amazon**
- Titan Image Generator adds an invisible watermark to every output by default. The `DetectGeneratedContent` API returns `GENERATED`/`NOT_GENERATED` plus a confidence level, i.e. a **presence-detection interface**. No payload or ECC was disclosed. Launch: Apr 2024; the API was then in preview. — [AWS News Blog](https://aws.amazon.com/blogs/aws/amazon-titan-image-generator-and-watermark-detection-api-are-now-available-in-amazon-bedrock); [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2024/04/watermark-detection-amazon-titan-image-generator-bedrock/) [V summary via search, S for HIGH/MEDIUM/LOW tiers]

**Digimarc** (patent disclosures; the current product format is not public)
- Payload: "a plural-symbol message payload (e.g., 47 binary bits … GTIN) together with 24 associated CRC bits". "Suitable coding methods include block codes, BCH, Reed Solomon, convolutional codes, turbo codes, etc." The "coder output may comprise hundreds or thousands of binary bits, e.g., 1024". The bits are scrambled by XOR with a key, and each raw bit modulates a PN carrier of 16 chips. A 128×128 location tile maps to a 256×256 block. Decoding falls back to another method if checksum fails. "The robust redundancy and error correction … make false decodes essentially a nullity." — [US 11,568,165 B1 (Digimarc)](https://patents.google.com/patent/US11568165B1/en) [V]
- A variant: 40-bit GTIN payload, coder output "e.g., 4,096" raw bits for a 256×256 tile, or 1024 for 128×128. Synchronization uses "dozens of magnitude peaks … in the Fourier domain". — [US 11,704,765 B2 (Digimarc)](https://patents.google.com/patent/US11704765B2/en) [V]
- Another Digimarc patent reportedly specifies 47+24 = 71 bits convolutionally encoded at "base rate of 1/13" to 924 bits. — [US 12,654,374](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12654374) [S, search snippet; this conflicts in coded length (924 vs 1024) with US 11,568,165, likely different embodiments]
- Digimarc Validate is SBAL entry #1 (audio/video/text/image). — [SBAL](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json)

**IMATAG, Steg.AI, Truepic, Hugging Face**
- IMATAG is registered as `com.imatag.lamark.v1` (images, 2025-02-26). A review site says detection uses an encryption key. No payload, ECC or FPR figures were found. — [SBAL](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json) [V]; [TrustRadius](https://www.trustradius.com/products/imatag/reviews) [S]
- Steg.AI is registered as `ai.steg.api` (image/video/application, 2024-05-20). Its informational URL is the CVPR 2019 "Light Field Messaging" paper. No payload or ECC information was found. — [SBAL](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json)
- Truepic × Steg.AI × Hugging Face (experimental proof of concept): a watermark is added to pixels after C2PA signing. If metadata is stripped, the watermark retrieves "a restored, signed version of the image". No payload details are given. — [Truepic: Hugging Face](https://truepic.com/hugging-face); [HF blog](https://huggingface.co/blog/alicia-truepic/identify-ai-generated-content) [S/V summary]

**Stability AI / invisible-watermark (the classical dwtDct family)**
- SD 1.x reference `txt2img.py` embeds the fixed bytes `"StableDiffusionV1"` (17 bytes = 136 bits) with **`dwtDct`**. — [CompVis/stable-diffusion txt2img.py](https://github.com/CompVis/stable-diffusion/blob/main/scripts/txt2img.py) [V]
- SDXL in diffusers embeds a fixed **48-bit** message `0b101100111110110010010000011110111011000110011110` with **`dwtDct`**. — [diffusers SDXL watermark.py](https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion_xl/watermark.py) [V]
- Library caveats: "The algorithm cannot guarantee to decode the original watermarks 100% accurately even though we don't apply any attack." It is "not robust to resize or aspect ratio changed crop". `dwtDctSvd` is "3x slower" than `dwtDct`. Defaults are 32–64-bit examples. There is no ECC in the library. — [ShieldMnt/invisible-watermark README](https://github.com/ShieldMnt/invisible-watermark) [V]

### Inferences
- Among public industrial designs, **ECC on the payload is the norm whenever an identifier must be recovered exactly**:
  - TrustMark: BCH.
  - InvisMark: UUID + ECC.
  - Digimarc: CRC + FEC + spreading, decades in production for retail barcodes.

  It is **absent** when the payload is a fixed tag used for presence detection (SD/SDXL dwtDct, ImmoStory's 64-bit constant).
- No public industrial system reports using 5G LDPC, polar or turbo codes for image watermarks. Digimarc patents list turbo/convolutional as options. The modern-FEC comparison is therefore novel relative to disclosed practice. The SynthID/Meta neural systems disclose no ECC; their raw payloads (136/256/1024 bits) leave room for one.
- Stability's deployed tag used `dwtDct`, not `dwtDctSvd`. A dwtDctSvd baseline is a close cousin of, not identical to, what was shipped.
- SynthID's evaluation already shows the gap between presence detection (TPR about 98–99.7% at 0.1% FPR worst case) and per-bit payload accuracy (89–98% worst case). Exact recovery of a 136-bit payload at 89% bit accuracy would be nearly impossible without ECC. This is a quantitative argument that **ECC is the enabling factor for ID recovery under strong attacks, while presence detection does not need it** (my inference).

### Gaps
- Amazon (Titan/Nova), OpenAI (pre-SynthID), IMATAG, Steg.AI and Digimarc Validate's current payload length and FEC are not public in any source found.
- SynthID-Image does not disclose its production payload size (only SynthID-O's 136 bits) or whether any coding protects it.
- No evidence was found that Meta's production watermark on Meta AI images is Stable Signature, VideoSeal or PixelSeal.
- InvisMark's specific ECC (type and rate) and its WER numbers were not extracted; the full paper needs reading.
- Hugging Face runs no watermark of its own beyond hosting demos and the diffusers code.

---

## Q4. Do industry systems use zero-bit detection plus database lookup instead of multi-bit IDs? How are false-positive rates set?

### Takeaway
Both patterns are deployed, usually for different jobs:
1. **AI-disclosure detectors** (SynthID Detector, Amazon DetectGeneratedContent, Meta's labelling) expose a **presence decision with a confidence**, and keep any payload internal. SynthID calibrates FPR statistically with conformal p-values (evaluated at 1e-3).
2. **Provenance/soft-binding watermarks** (TrustMark, InvisMark, Digimarc, Video Seal deployments) carry a **multi-bit ID used as a database key**. ECC/CRC success, or a fixed known-bits header, doubles as the presence test.

Hybrids are common: SynthID solves detection and payload separately, ImmoStory uses a 64-bit header threshold plus a 192-bit ID, and TrustMark's signpost mode uses BCH_SUPER for a 40-bit "which watermark is here" integer.

### Cited Findings
- SynthID-Image: detection and payload "solved … separately". The detection threshold on a conformal p-value "guarantees a FPR of at most α", with results reported at 0.1% FPR. Payload matching can also be used for detection, giving 98.84–98.90% TPR in the aggregate worst case vs 99.72% for the dedicated detector. — [arXiv 2510.09263](https://arxiv.org/html/2510.09263v1) [V]
- Amazon: the API returns `GENERATED`/`NOT_GENERATED` plus a confidence score. — [AWS blog](https://aws.amazon.com/blogs/aws/amazon-titan-image-generator-and-watermark-detection-api-are-now-available-in-amazon-bedrock) [V via search summary]
- Google's public detector says only whether media "was made with AI from Google or our partners", which is presence/attribution at the provider level. — [Google blog Oct 2026](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/synth-id-ai-content/) [V]
- TrustMark: `wm_present` is true iff BCH decoding succeeds (and padding is clean). The ID is then used as a key into a manifest store ("Durable Content Credential"). — [datalayer.py](https://github.com/adobe/trustmark/blob/main/python/trustmark/datalayer.py); [c2pa README](https://github.com/adobe/trustmark/blob/main/c2pa/README.md) [V]
- Digimarc: CRC/checksum validates decoded payloads, and "robust redundancy and error correction … make false decodes essentially a nullity". — [US 11,568,165](https://patents.google.com/patent/US11568165B1/en) [V]
- ImmoStory: a known-constant threshold of ≥56/64 matching bits identifies its videos, and the 192-bit ID resolves to the manifest. — [ImmoStory](https://immostory.ai/en/provenance) [V]
- AIDR (audio): a public brand byte (0xAD) plus a 32-bit per-clip ID "issued by AIDR's watermark register". — [SBAL](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json) [V]
- The C2PA resolution API returns up to `maxResults` (default 10) candidates with a 0–100 `similarityScore`, and recommends a fingerprint cross-check to defeat watermark transfer. — [C2PA Soft Binding API 2.5](https://spec.c2pa.org/specifications/specifications/2.5/softbinding/Decoupled.html) [V]
- Meta labels content partly via C2PA/IPTC metadata detection, not only watermarks. — [Meta Newsroom](https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/) [V]

### Inferences
- The requester's design (fixed "AI-generated" header plus random ID) mirrors the deployed hybrid pattern. The header implements zero-bit-style detection with an analytically settable FPR. For example, ImmoStory's ≥56/64 rule gives P(false match) ≈ 2.8×10⁻¹⁰ under i.i.d. uniform bits (my calculation). The ID part implements the C2PA soft-binding key, where ECC matters.
- With a database of N issued IDs, the system-level false-attribution rate is roughly FPR_header × P(decoded ID ∈ DB). A sparse ID space (e.g. 2^61 IDs with 10^9 issued) adds about 2^-31 of protection (my inference). A database lookup with Hamming tolerance is therefore a practical alternative or complement to strong ECC. This is what `similarityScore`/`maxResults` allow.
- Using ECC decode success as the only detector (the TrustMark default) gives weak FPR at high-rate codes: about 10⁻³ for BCH_5 and about 10⁻¹ for BCH_3 on random words (my calculation). A separate header/statistical test is advisable, and this is how SynthID and ImmoStory separate the two functions.
- Industry FPR targets are rarely published. The only explicit operating point found in a deployed system's paper is SynthID's 0.1% FPR evaluation. The system-level target is not disclosed.

### Gaps
- No vendor publishes production FPR targets (e.g. 1e-6, 1e-9) or the database-side matching tolerance.
- Whether SynthID Detector decodes the payload to name the specific partner or model is not stated.
- Amazon's confidence calibration method is not disclosed.

---

## Q5. Regulatory drivers implying identifier recovery

### Takeaway
The EU AI Act Art. 50(2) and its June 2026 Code of Practice require machine-readable marking that makes content **detectable as AI-generated**. That is a presence requirement. The Code makes an imperceptible watermark the mandatory base layer, adds signed metadata where the format allows, and makes a model ID/version **optional**. Identifier content is pushed to metadata, not the watermark. California SB 942 (as amended by AB 853, operative 2 Aug 2026) is the clearest driver toward **identifying information in the latent disclosure**: provider, system and version, timestamp, and per secondary sources a unique identifier. This favours watermark-keyed lookup or an ID payload, and therefore ECC. No binding US federal payload requirement was found.

### Cited Findings
- EU timeline:
  - The final Code of Practice on marking and labelling AI-generated content was published **10 June 2026**. It is voluntary.
  - Transparency obligations apply from **2 August 2026**.
  - Systems already on the market have a transitional period until **2 December 2026**.
  - The Code will be reviewed "at least every 2 years".
  - The Code text calls for solutions "effective, interoperable, robust and reliable, as far as technically feasible".

  — [EC Q&A on the Code](https://digital-strategy.ec.europa.eu/en/faqs/code-practice-transparency-ai-generated-content); [EC news](https://digital-strategy.ec.europa.eu/en/news/commission-publishes-code-practice-marking-and-labelling-ai-generated-content) [V]
- Code content per law-firm summaries:
  - "all AI-generated or manipulated content must be marked with an imperceptible watermark", with relaxed reliability for texts under 200 tokens.
  - A second layer of "metadata that is digitally signed, time-stamped and tamper-proof" is required for formats that support it.
  - Providers are "encouraged" to include AI system name, provider name and timestamp. Model identifier and version are optional.
  - "Fingerprinting or logging may be used as a supplementary measure" only.
  - Robustness to "typical processing operations" (mirroring, format changes, screenshots) and to "malicious modification attempts".
  - A free "detection solution", with results available "in a digitally signed format".
  - The deadline for the watermark interoperability solution is **2 Feb 2027**.

  — [Gleiss Lutz](https://www.gleisslutz.com/en/know-how/new-eu-code-practice-transparency-ai-generated-content-impact-and-options) [S, law-firm summary of final text]; [Jones Day](https://www.jonesday.com/en/insights/2026/06/european-commission-publishes-final-code-of-practice-on-marking-and-labelling-aigenerated-content) [S] ("at least two layers of machine-readable marking where necessary")
- Deployers on the C2PA SBAL explicitly position ID-bearing watermarks as the "EU AI Act Art. 50(2) second marking layer": ImmoStory (Video Seal, 192-bit ID) and AIDR (SilentCipher, 32-bit ID). — [SBAL](https://github.com/c2pa-org/softbinding-algorithm-list/blob/main/softbinding-algorithm-list.json) [V]
- California SB 942 / AB 853:
  - Latent disclosures in image, video and audio became operative **2 Aug 2026** for providers with more than 1M monthly California users.
  - A free public detection tool is required.
  - Per one source, the latent disclosure must identify the provider, system name/version and creation/alteration date, and "uniquely identify the content"; it must be "permanent or extraordinarily difficult to remove" "to the extent technically feasible".
  - Penalties reported at $5,000 per violation per day.
  - Platform duties from 1 Jan 2027, and capture devices from 1 Jan 2028.
  - Amendments (SB 1000, AB 2713) are pending.

  — [Morgan Lewis, Aug 2026](https://www.morganlewis.com/pubs/2026/08/new-california-ai-disclosure-rules-become-operative); [AB 853 legislative analysis](https://billtexts.s3.amazonaws.com/ca/ca-analysishttps-leginfo-legislature-ca-gov-faces-billAnalysisClient-xhtml-bill-id-202520260AB853-ca-analysis-392900.pdf) [S, statute text (Bus. & Prof. Code §22757 et seq.) not read]
- US federal: NIST AI 100-4 (Nov 2024, final) surveys covert watermarking, its trade-offs and testing (§3.1.1, §4.1.1). It is guidance, not a mandate. — [NIST AI 100-4](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-4.pdf) [S, PDF not read]

### Inferences
- EU compliance can be met with **zero-bit watermarks plus signed metadata**, so the EU does not by itself force ECC-protected IDs in the watermark. The requirement for signed, verifiable detection results and the 2027 interoperability push, however, favour watermarks that can **link back to signed metadata** after stripping, which is the C2PA soft-binding pattern. That needs exact ID recovery.
- California's "unique identifier" and provenance-data requirements are the strongest regulatory rationale for multi-bit, error-protected watermark payloads, or for a watermark-keyed registry. Vendors may still satisfy them via metadata plus a provider-level watermark. Confirm against the statute.
- Overall relevance verdict: ECC is **practically relevant for the identifier/manifest-recovery use** (C2PA durable credentials, CA latent disclosure IDs, Digimarc-style serialization). It is **marginal for pure AI-disclosure presence detection**, which industry handles with statistical detectors calibrated to an FPR. The requester's header-plus-ID split maps onto exactly this division.

### Gaps
- The official final Code PDF was not located or read. Exact measure wording, numbering and any FPR/robustness metrics need checking against the Commission's text.
- The California statute text was not read directly. Whether "unique identifier" must live in the watermark or may live in metadata is unconfirmed.
- No US federal binding watermark-payload requirement was found. The current status of US federal guidance after 2025 was not researched.
- No standard (C2PA, ISO/IEC, JPEG Trust, IEEE) found that specifies watermark payload ECC or bit-error tolerance.
