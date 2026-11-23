# EVALUATION_METHODOLOGY.md — Evaluation Framework & Mathematical Formulations
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Evaluation Philosophy & Principles
A core mandate of this project is:
> **Every model comparison must use a common evaluation dataset and consistent input conditions. Clearly distinguish automated evaluation from human evaluation. Never claim that a generated claim is factually correct merely because an LLM says so.**

To achieve this, the platform evaluates outputs across five orthogonal dimensions:
1. **Content Coverage**
2. **Text Similarity (N-gram & Semantic)**
3. **Factual Consistency & Hallucination Rate**
4. **Controllability & Constraint Compliance**
5. **Computational & Resource Efficiency**

---

## 2. Mathematical Formulations & Metrics

### 2.1 Content Coverage
Measures how comprehensively the generated output reflects the critical facts of the source document or reference gold-standard.

#### A. Key Fact Recall
Given a set of $M$ reference key facts $K = \{k_1, k_2, \dots, k_M\}$ extracted from the source document:
$$\text{Coverage}_{\text{KeyFacts}} = \frac{|\{k \in K \mid \text{entailed}(k, \text{Output})\}|}{|K|}$$

#### B. Named Entity Preservation
Given set of named entities $E_{\text{ref}}$ in the reference summary and $E_{\text{gen}}$ in the generated output:
$$\text{Recall}_{\text{Entity}} = \frac{|E_{\text{gen}} \cap E_{\text{ref}}|}{|E_{\text{ref}}|}$$

#### C. Numerical Fact Preservation
Given set of numerical and date expressions $N_{\text{ref}}$ and $N_{\text{gen}}$:
$$\text{Recall}_{\text{Num}} = \frac{|N_{\text{gen}} \cap N_{\text{ref}}|}{|N_{\text{ref}}|}$$

---

### 2.2 Text Similarity Metrics

#### A. ROUGE (Recall-Oriented Understudy for Gisting Evaluation)
- **ROUGE-1**: Unigram overlap F1-score.
- **ROUGE-2**: Bigram overlap F1-score capturing phrase-level fluency.
- **ROUGE-L**: Longest Common Subsequence (LCS) F1-score reflecting sentence structure preservation.

For n-grams:
$$\text{ROUGE-N} = \frac{\sum_{S \in \{\text{References}\}} \sum_{\text{gram}_n \in S} \text{Count}_{\text{match}}(\text{gram}_n)}{\sum_{S \in \{\text{References}\}} \sum_{\text{gram}_n \in S} \text{Count}(\text{gram}_n)}$$

#### B. BERTScore
Computes token-level semantic similarity using contextualized token embeddings:
$$\text{BERTScore-F1} = 2 \cdot \frac{P_{\text{BERT}} \cdot R_{\text{BERT}}}{P_{\text{BERT}} + R_{\text{BERT}}}$$
Where $R_{\text{BERT}} = \frac{1}{|x|} \sum_{x_i \in x} \max_{y_j \in y} \mathbf{x}_i^\top \mathbf{y}_j$ using cosine similarity over normalized embeddings.

---

### 2.3 Factual Consistency & Hallucination Scoring

Let the generated output be segmented into $T$ atomic factual claims:
$$C = \{c_1, c_2, \dots, c_T\}$$
Each claim $c_i$ is verified against source evidence chunks $S$ and assigned a verification status:
$$V(c_i) \in \{\text{SUPPORTED}, \text{PARTIALLY\_SUPPORTED}, \text{UNSUPPORTED}, \text{CONTRADICTED}\}$$

#### Factual Consistency Score (FCS)
$$\text{FCS} = \frac{N_{\text{supported}} + 0.5 \cdot N_{\text{partially\_supported}}}{T}$$
Where:
- $N_{\text{supported}} = |\{c \in C \mid V(c) = \text{SUPPORTED}\}|$
- $N_{\text{partially\_supported}} = |\{c \in C \mid V(c) = \text{PARTIALLY\_SUPPORTED}\}|$
- $T = |C|$ (Total claims)

#### Hallucination Rate (HR)
$$\text{HR} = \frac{N_{\text{unsupported}} + 2 \cdot N_{\text{contradicted}}}{T}$$
*Note: Contradictions are weighted $2\times$ because actively falsified information causes greater real-world harm than omitted or unverifiable information.*

---

### 2.4 Controllability Scoring

Controllability evaluates whether the model followed explicit instructions:
$$\text{Score}_{\text{Control}} = \frac{1}{4} (S_{\text{length}} + S_{\text{keywords}} + S_{\text{prohibited}} + S_{\text{format}})$$

Where:
1. **Length Score**:
   $$S_{\text{length}} = \max\left(0, 1 - \frac{|\text{ActualWords} - \text{TargetWords}|}{\text{TargetWords}}\right)$$
2. **Required Keywords Score**:
   $$S_{\text{keywords}} = \frac{|\text{Keywords Present}|}{|\text{Keywords Required}|}$$
3. **Prohibited Terms Score**:
   $$S_{\text{prohibited}} = \begin{cases} 1.0 & \text{if zero prohibited terms appear} \\ 0.0 & \text{if any prohibited term appears} \end{cases}$$
4. **Format & Section Score**:
   $$S_{\text{format}} = \frac{|\text{Expected Sections Present}|}{|\text{Expected Sections}|}$$

---

### 2.5 Computational Efficiency Metrics
- **Generation Latency ($t_{\text{gen}}$)**: Total wall-clock time in milliseconds.
- **Tokens per Second (TPS)**: $\frac{\text{Output Tokens}}{t_{\text{gen}} \text{ (seconds)}}$.
- **Peak Memory (VRAM / RAM)**: Recorded in Megabytes during inference.
- **Cost**: Estimated API expenditure in USD based on provider pricing tables.

---

## 3. Human Evaluation Protocol
In addition to automated metrics, human experts rate outputs on a 1–5 Likert scale across four rubrics:
1. **Factual Accuracy (1–5)**: 5 = No factual errors; 1 = Severe hallucinations or contradictions.
2. **Completeness (1–5)**: 5 = All essential points conveyed; 1 = Major omissions.
3. **Readability & Fluency (1–5)**: 5 = Polished, professional prose; 1 = Disjointed or incoherent.
4. **Audience Suitability (1–5)**: 5 = Perfectly calibrated tone and complexity; 1 = Inappropriate style or jargon.

*Human ratings are persisted separately from automated scores in the database.*
