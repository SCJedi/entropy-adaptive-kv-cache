# How to Submit Your Paper to arXiv

## Your Paper

**File:** `paper/main.tex` (this directory)
**GitHub:** https://github.com/SCJedi/entropy-adaptive-kv-cache/blob/main/paper/main.tex

## Step-by-Step

### 1. Create an arXiv Account
- Go to https://arxiv.org/user/register
- Fill in name, email, affiliation (can be "Independent Researcher")
- You'll get a confirmation email

### 2. First-Time Endorsement
- First-time submitters to cs.LG (Machine Learning) need an endorsement
- After registering, go to https://arxiv.org/auth/endorse
- Request endorsement for **cs.LG** category
- Options to get endorsed:
  - **Automatic:** If your email is from a known institution (.edu, research lab)
  - **Request from someone:** Ask anyone who's published on arXiv in cs.LG to endorse you
  - **Post on Twitter/X:** "Looking for an arXiv endorsement for cs.LG — publishing research on KV cache compression for LLMs" — ML researchers are generally happy to help
  - **r/MachineLearning:** Post asking for endorsement, include paper abstract
- Usually takes 1-3 days

### 3. Prepare the Submission
- arXiv compiles LaTeX for you — just upload `main.tex`
- If there are figures, include them too
- Package everything in a ZIP or tar.gz:
  ```
  cd paper/
  zip submission.zip main.tex
  ```
- Or just upload `main.tex` directly

### 4. Submit
- Go to https://arxiv.org/submit
- Select category: **cs.LG** (Machine Learning)
- Cross-list: **cs.CL** (Computation and Language)
- Upload your file(s)
- Fill in metadata:
  - **Title:** Lossless 12x KV Cache Compression in Hybrid Attention Models via Combined Entropy-Adaptive Eviction and Vector Quantization
  - **Authors:** SCJedi
  - **Abstract:** (copy from the paper)
  - **Comments:** "Code available at https://github.com/SCJedi/entropy-adaptive-kv-cache"
- Submit!

### 5. After Submission
- arXiv moderators review (usually same day or next day)
- Your paper gets an arXiv ID (e.g., 2604.XXXXX)
- It appears on the daily listing the following day
- You get a permanent citable URL: https://arxiv.org/abs/2604.XXXXX

### 6. Share It
- **Reddit r/LocalLLaMA:** "We achieved lossless 12x KV cache compression on hybrid models — paper + code"
- **Reddit r/MachineLearning:** "[R] Lossless 12x KV Cache Compression in Hybrid Attention Models"
- **Twitter/X:** Tag @GoogleAI, @AnthropicAI, @vaborenkov (vLLM), @ggaborenkov (ggml)
- **HuggingFace:** Post as a paper at https://huggingface.co/papers
- **Update your GitHub issues** on vLLM, llama.cpp, and TurboQuant with the arXiv link

## Alternative: HuggingFace Papers (No Endorsement Needed)
If arXiv endorsement takes too long:
1. Compile the LaTeX to PDF (use Overleaf.com — free, paste the LaTeX)
2. Upload to HuggingFace Papers: https://huggingface.co/papers
3. No endorsement required, immediate visibility in the HF community

## Quick PDF (if you want to review before submitting)
1. Go to https://www.overleaf.com (free account)
2. New Project → Upload → upload `main.tex`
3. Click "Recompile" → download PDF
4. Review, then submit to arXiv
