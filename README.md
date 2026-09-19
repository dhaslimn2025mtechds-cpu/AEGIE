AEGIE



A Research Framework for Agentic AI-Based Voice Interview Analysis



AEGIE is a CPU-compatible research prototype for technical voice-interview analysis. It integrates genuine voice capture, NVIDIA Parakeet speech-to-text, objective speech features, MiniLM semantic evidence, an agent-based evaluation workflow, and a transparent Flask dashboard.



Research scope: This repository contains a no-participant proof-of-concept implementation. It does not claim validated 1–5 interview scoring, population-level accuracy, human-vs-AEGIE agreement, or participant-study results.



1\. Core Pipeline



Voice Response

&#x20;     ↓

Audio Capture

&#x20;     ↓

FFmpeg Audio Processing

&#x20;     ↓

NVIDIA Parakeet TDT 0.6B V2 INT8

via Sherpa-ONNX

&#x20;     ↓

Transcript

&#x20;     ↓

Speech Feature Extraction

&#x20;     ↓

MiniLM Semantic Evidence

&#x20;     ↓

Evaluation Agent

&#x20;     ↓

Calibration / Adaptive Safety Gates

&#x20;     ↓

Research Prototype Dashboard



2\. Main Features



Browser-based technical voice interview using Flask



Six supported technical job roles



72 researcher-created interview questions



12 questions per role



4 Easy, 4 Medium, and 4 Hard questions per role



NVIDIA Parakeet TDT 0.6B V2 INT8 speech-to-text



Sherpa-ONNX CPU inference



MiniLM ONNX semantic evidence



Objective speech measurements:



response duration



word count



words per minute



filler-word count



pause count



filler rate



pause rate



Current-interview sample isolation



Agent-based evaluation architecture



Calibration-gated scoring



Adaptive/feedback safety gates



Proof-of-concept research dashboard



Reproducible descriptive experiment scripts



3\. Supported Job Roles



Data Scientist



Software Developer



Data Analyst



Machine Learning Engineer



Cloud DevOps Engineer



Cybersecurity Analyst



The reference validator checks all six roles and all 72 reference mappings.



4\. Agent Architecture



AEGIE currently contains the following logical agents:



Interview Agent — manages interview flow and question selection.



Evaluation Agent — creates evaluation features and semantic evidence.



Adaptive Decision Agent — remains gated until scientifically calibrated scoring is available.



Feedback Agent — remains gated until calibrated evaluation is available.



The system intentionally avoids generating unsupported interview scores.



5\. Semantic Evaluation



AEGIE uses an ONNX version of:



sentence-transformers/all-MiniLM-L6-v2



The participant transcript is compared with researcher-created reference knowledge.



The dashboard reports values such as:



Whole-answer MiniLM similarity

Sentence-level MiniLM best-match similarity



These are semantic evidence values, not validated 1–5 interview scores.



6\. Speech-to-Text



Active STT:



NVIDIA Parakeet TDT 0.6B V2 INT8



Inference is performed locally with:



Sherpa-ONNX



AEGIE converts browser-recorded audio to a compatible mono PCM WAV representation before transcription.



7\. Development Research Evidence



The current proof-of-concept experiment contains:



Development feature rows: 33

Unique sample IDs: 33

Duplicate sample rows: 0

Unique question IDs: 11



All main stored semantic and speech measurements were present in the analyzed feature store.



Overall Descriptive Results



Measure



Mean



Whole-answer MiniLM similarity



0.4582



Sentence-level MiniLM best similarity



0.5037



Response duration



16.9639 s



Word count



30.8182



WPM



111.5206



Filler count



0.0606



Pause count



0.9697



These values are descriptive proof-of-concept measurements only.



Difficulty-Level Descriptive Evidence



Difficulty



Samples



Whole Similarity



Sentence Similarity



Duration (s)



WPM



Pauses



Easy



15



0.5205



0.5273



13.9167



121.8407



0.4667



Medium



12



0.4194



0.5236



20.7550



101.9083



1.5833



Hard



6



0.3798



0.4046



17.0000



104.9450



1.0000



These observations must not be interpreted as causal or statistically validated differences.



8\. Repository Structure



AEGIE/

│

├── app.py

├── requirements.txt

├── .gitignore

│

├── annotations/

│   └── annotation\_rubric.txt

│

├── data/

│   ├── adaptive\_protocol.txt

│   └── question\_bank/

│       ├── cloud\_devops.csv

│       ├── cybersecurity\_analyst.csv

│       ├── data\_analyst.csv

│       ├── data\_scientist.csv

│       ├── ml\_engineer.csv

│       └── software\_developer.csv

│

├── research\_documents/

│   └── FINAL\_RESEARCH\_SCOPE.txt

│

├── results/

│   ├── prototype\_data\_quality.csv

│   ├── prototype\_difficulty\_summary.csv

│   ├── prototype\_experiment\_metadata.json

│   ├── prototype\_experiment\_report.txt

│   ├── prototype\_overall\_summary.csv

│   └── prototype\_question\_summary.csv

│

├── src/

│   ├── agents/

│   ├── audio\_features.py

│   ├── calibrated\_score\_store.py

│   ├── download\_parakeet\_model.py

│   ├── download\_semantic\_model.py

│   ├── evaluation\_feature\_store.py

│   ├── parakeet\_adapter.py

│   ├── quality\_check.py

│   ├── run\_no\_participant\_experiments.py

│   ├── speech\_features.py

│   ├── test\_parakeet\_aegie\_audio.py

│   ├── transcription.py

│   └── validate\_semantic\_model.py

│

└── templates/

&#x20;   ├── index.html

&#x20;   ├── interview.html

&#x20;   └── results.html



Local model files, raw audio, development response data, and abandoned participant-study artifacts are intentionally excluded from Git.



9\. Requirements



Recommended environment:



Python 3.11

Windows 10/11 or compatible Linux environment

FFmpeg available on PATH

CPU inference supported



Install Python dependencies:



python -m pip install -r requirements.txt



10\. Download the Models



Run:



python src/download\_parakeet\_model.py

python src/download\_semantic\_model.py



The downloaded model artifacts are stored locally and are intentionally excluded from GitHub.



Expected model directories include:



models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8

models/semantic\_minilm



11\. Run AEGIE



Start the Flask application:



python app.py



Open:



http://127.0.0.1:5000



The default research-safe collection mode is:



DEVELOPMENT



Local development CSV files are created automatically when required.



12\. Validate the 72-Question Reference Layer



Run:



python src/agents/role\_reference\_validator.py



Expected final validation:



PASS: ALL SIX ROLE REFERENCE MAPPINGS ARE VALID.

Validated roles: 6 / 6

Validated references: 72 / 72



Reference content should still receive domain-expert review before being treated as validated research ground truth.



13\. Run the Prototype Experiment Analysis



After local development responses exist, run:



python src/run\_no\_participant\_experiments.py



Generated outputs:



results/prototype\_overall\_summary.csv

results/prototype\_difficulty\_summary.csv

results/prototype\_question\_summary.csv

results/prototype\_data\_quality.csv

results/prototype\_experiment\_metadata.json

results/prototype\_experiment\_report.txt



The script performs descriptive analysis only and does not claim validated interview-scoring accuracy.



14\. Research Integrity



AEGIE intentionally separates:



Measured evidence

from

Validated interview scoring



The current public proof-of-concept does not claim:



validated 1–5 candidate scores



candidate-selection accuracy



population-level generalization



human-vs-AEGIE agreement



validated adaptive-difficulty effectiveness



participant-study findings



If a calibrated model is unavailable, scoring remains unavailable instead of being generated using arbitrary thresholds.



15\. Data Privacy



The public repository excludes:



raw audio recordings



local development transcripts/datasets



model binaries



development feature-store records



abandoned pilot-study files



human annotation records



private backups



This keeps the repository focused on reproducible code, question/reference resources, aggregate proof-of-concept results, and research methodology.



16\. Limitations



Current limitations include:



development evidence is not a participant study



the current descriptive feature store is limited in role coverage



speech-to-text errors can affect downstream semantic evidence



MiniLM cosine similarity is not equivalent to interview quality



reference answers require expert review



adaptive and feedback stages are calibration-gated



no validated scoring model is included in the public proof-of-concept



17\. Future Work



Subject to appropriate mentor/institutional approval:



independent expert review of question/reference knowledge



approved multi-participant evaluation



independent human annotation



inter-rater agreement analysis



calibrated scoring



held-out model evaluation



validated adaptive question selection



broader job-role evaluation



STT WER/CER benchmarking



production deployment and monitoring



18\. Current Research Contribution



AEGIE demonstrates a transparent, CPU-compatible architecture that integrates:



Voice

\+ Local STT

\+ Speech Features

\+ Semantic Evidence

\+ Agentic Workflow

\+ Research-Safe Gating

\+ Evidence Dashboard



The main contribution of the current version is the implemented research framework and reproducible proof-of-concept pipeline, rather than a claim of validated automated hiring decisions.



19\. Technology Stack



Python 3.11



Flask



pandas



NumPy



ONNX Runtime



Hugging Face Tokenizers



Hugging Face Hub



Sherpa-ONNX



NVIDIA Parakeet TDT



MiniLM



scikit-learn



SciPy



Joblib



FFmpeg



HTML/CSS/JavaScript



Git / GitHub



20\. Disclaimer



AEGIE is a research and educational prototype. It should not be used as the sole basis for real employment decisions. The current version reports evidence and system behavior, not validated candidate suitability.
