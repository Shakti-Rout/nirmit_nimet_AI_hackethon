# -*- coding: utf-8 -*-
"""
RAG (Retrieval-Augmented Generation) Engine for Prerana Agentic EdTech.
Handles document ingestion, PDF parsing, chunking, TF-IDF + Cosine similarity vector search,
and multilingual syllabus retrieval.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pypdf

class RAGEngine:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir

        self.kb_dir = os.path.join(self.data_dir, "knowledge_base")
        self.uploads_dir = os.path.join(self.data_dir, "uploads")
        os.makedirs(self.kb_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)

        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

        self._load_default_curriculum()
        self._load_custom_uploads()
        self._build_index()

    def _load_default_curriculum(self):
        """Pre-loads verified multilingual NCERT/State Board syllabus documents."""
        default_docs = [
            # Physics - Newton's Laws of Motion
            {
                "id": "phys_newton_en_1",
                "subject": "Physics",
                "topic": "Newton's Laws of Motion",
                "language": "en",
                "grade": "Class 9-10",
                "source": "NCERT Science Chapter 9",
                "text": (
                    "Newton's First Law states that every object continues in its state of rest or uniform motion "
                    "in a straight line unless acted upon by an external unbalanced force. This property is known as Inertia. "
                    "Mass is the quantitative measure of inertia: heavier objects require greater force to change their state."
                )
            },
            {
                "id": "phys_newton_en_2",
                "subject": "Physics",
                "topic": "Newton's Third Law of Motion",
                "language": "en",
                "grade": "Class 9-10",
                "source": "NCERT Science Chapter 9",
                "text": (
                    "Newton's Third Law states that for every action, there is an equal and opposite reaction. "
                    "Crucially, action and reaction forces act on TWO DIFFERENT bodies, which is why they never cancel each other out. "
                    "For example, when a swimmer pushes water backward (action), the water pushes the swimmer forward with an equal force (reaction)."
                )
            },
            {
                "id": "phys_newton_or_1",
                "subject": "Physics",
                "topic": "ନିଉଟନଙ୍କ ଗତି ନିୟମ (Newton's Laws of Motion)",
                "language": "or",
                "grade": "Class 9-10",
                "source": "ଓଡ଼ିଶା ମାଧ୍ୟମିକ ଶିକ୍ଷା ପରିଷଦ (BSE Odisha)",
                "text": (
                    "ନିଉଟନଙ୍କ ପ୍ରଥମ ଗତି ନିୟମ: କୌଣସି ବାହ୍ୟ ବଳ ପ୍ରୟୋଗ ନ ହେବା ପର୍ଯ୍ୟନ୍ତ ଏକ ସ୍ଥିର ବସ୍ତୁ ସ୍ଥିର ରହେ ଏବଂ ଏକ ଗତିଶୀଳ ବସ୍ତୁ ସମଗତିରେ ସରଳରେଖାରେ ଗତି କରିଚାଲେ। "
                    "ଏହି ଧର୍ମକୁ 'ଜଡ଼ତା' (Inertia) କୁହାଯାଏ। ବସ୍ତୁର ବସ୍ତୁତ୍ୱ (Mass) ହେଉଛି ତାର ଜଡ଼ତାର ପରିମାପ।"
                )
            },
            {
                "id": "phys_newton_or_2",
                "subject": "Physics",
                "topic": "ନିଉଟନଙ୍କ ତୃତୀୟ ଗତି ନିୟମ (Newton's Third Law)",
                "language": "or",
                "grade": "Class 9-10",
                "source": "ଓଡ଼ିଶା ମାଧ୍ୟମିକ ଶିକ୍ଷା ପରିଷଦ (BSE Odisha)",
                "text": (
                    "ନିଉଟନଙ୍କ ତୃତୀୟ ଗତି ନିୟମ: ପ୍ରତ୍ୟେକ କ୍ରିୟାର ସର୍ବଦା ଏକ ସମାନ ଏବଂ ବିପରୀତ ପ୍ରତିକ୍ରିୟା ଥାଏ। "
                    "ମନେରଖିବା କଥା ଯେ, କ୍ରିୟା ଏବଂ ପ୍ରତିକ୍ରିୟା ବଳ ଦୁଇଟି ପୃଥକ ବସ୍ତୁ ଉପରେ କାର୍ଯ୍ୟ କରେ, ତେଣୁ ସେମାନେ ପରସ୍ପରକୁ ନଷ୍ଟ ବା କ୍ୟାନ୍ସଲ କରନ୍ତି ନାହିଁ। "
                    "ଉଦାହରଣ: ଚିଲିକାରେ ଡଙ୍ଗା ଚଳାଇବା ବେଳେ ମଙ୍ଗୁଆଳ ପାଣିକୁ ପଛକୁ ଠେଲେ (କ୍ରିୟା), ଏବଂ ପାଣି ଡଙ୍ଗାକୁ ଆଗକୁ ଠେଲିଦିଏ (ପ୍ରତିକ୍ରିୟା)।"
                )
            },
            {
                "id": "phys_newton_ta_1",
                "subject": "Physics",
                "topic": "நியூட்டனின் மூன்றாம் விதி (Newton's Third Law)",
                "language": "ta",
                "grade": "Class 9-10",
                "source": "தமிழ்நாடு பாடநூல் கழகம் (TN SCERT)",
                "text": (
                    "நியூட்டனின் மூன்றாம் விதி: ஒவ்வொரு வினைக்கும் அதற்குச் சமமான மற்றும் எதிரான எதிர்வினை உண்டு. "
                    "வினையும் எதிர்வினையும் எப்போதும் வெவ்வேறு பொருள்களின் மீது செயல்படுகின்றன; எனவே அவை ஒன்றை ஒன்று ரத்து செய்வதில்லை. "
                    "எடுத்துக்காட்டாக, துப்பாக்கியிலிருந்து குண்டு பாயும்போது துப்பாக்கி பின்னோக்கி உதைக்கிறது."
                )
            },
            {
                "id": "phys_newton_te_1",
                "subject": "Physics",
                "topic": "న్యూటన్ మూడవ గమన నియమం (Newton's Third Law)",
                "language": "te",
                "grade": "Class 9-10",
                "source": "ఆంధ్రప్రదేశ్ & తెలంగాణ SCERT",
                "text": (
                    "న్యూటన్ మూడవ గమన నియమం: ప్రతి చర్యకు సమానమైన మరియు వ్యతిరేకమైన ప్రతిచర్య ఉంటుంది. "
                    "చర్య మరియు ప్రతిచర్యలు రెండు వేర్వేరు వస్తువులపై పనిచేస్తాయి, కాబట్టి అవి ఒకదానికొకటి రద్దు కావు. "
                    "ఉదాహరణ: తుపాకీ పేల్చినప్పుడు బుల్లెట్ ముందుకు వెళ్తుంది, తుపాకీ వెనక్కి తన్నుతుంది."
                )
            },
            {
                "id": "phys_newton_kn_1",
                "subject": "Physics",
                "topic": "ನ್ಯೂಟನ್ನಿನ ಮೂರನೇ ನಿಯಮ (Newton's Third Law)",
                "language": "kn",
                "grade": "Class 9-10",
                "source": "ಕರ್ನಾಟಕ ಪಠ್ಯಪುಸ್ತಕ ಸಂಘ (Karnataka DSERT)",
                "text": (
                    "ನ್ಯೂಟನ್ನಿನ ಮೂರನೇ ಚಲನೆಯ ನಿಯಮ: ಪ್ರತಿಯೊಂದು ಕ್ರಿಯೆಗೂ ಸಮಾನವಾದ ಮತ್ತು ವಿರುದ್ಧವಾದ ಪ್ರತಿಕ್ರಿಯೆ ಇರುತ್ತದೆ. "
                    "ಕ್ರಿಯೆ ಮತ್ತು ಪ್ರತಿಕ್ರಿಯೆ ಬಲಗಳು ಎರಡು ವಿಭಿನ್ನ ವಸ್ತುಗಳ ಮೇಲೆ ವರ್ತಿಸುವುದರಿಂದ ಅವು ಪರಸ್ಪರ ರದ್ದಾಗುವುದಿಲ್ಲ. "
                    "ಉದಾಹರಣೆಗೆ: ದೋಣಿಯನ್ನು ಹುಟ್ಟುಹಾಕುವಾಗ ನೀರನ್ನು ಹಿಂದಕ್ಕೆ ತಳ್ಳಲಾಗುತ್ತದೆ, ನೀರು ದೋಣಿಯನ್ನು ಮುಂದಕ್ಕೆ ತಳ್ಳುತ್ತದೆ."
                )
            },
            {
                "id": "phys_newton_ml_1",
                "subject": "Physics",
                "topic": "ന്യൂട്ടന്റെ മൂന്നാം ചലന നിയമം (Newton's Third Law)",
                "language": "ml",
                "grade": "Class 9-10",
                "source": "കേരള SCERT",
                "text": (
                    "ന്യൂട്ടന്റെ മൂന്നാം ചലന നിയമം: ഏതൊരു പ്രവർത്തനത്തിനും തുല്യവും വിപരീതവുമായ ഒരു പ്രതിപ്രവർത്തനം ഉണ്ടായിരിക്കും. "
                    "പ്രവർത്തനവും പ്രതിപ്രവർത്തനവും രണ്ട് വ്യത്യസ്ത വസ്തുക്കളിലാണ് അനുഭവപ്പെടുന്നത്, അതിനാൽ അവ പരസ്പരം റദ്ദാക്കപ്പെടുന്നില്ല. "
                    "ഉദാഹരണം: തോക്കിൽ നിന്ന് വെടിയുണ്ട പായുമ്പോൾ തോക്ക് പിന്നോട്ട് തള്ളപ്പെടുന്നു."
                )
            },

            # Biology - Photosynthesis
            {
                "id": "bio_photo_en_1",
                "subject": "Biology",
                "topic": "Photosynthesis and Plant Nutrition",
                "language": "en",
                "grade": "Class 7-10",
                "source": "NCERT Science Chapter 6 Life Processes",
                "text": (
                    "Photosynthesis is the process by which green plants synthesize glucose from carbon dioxide and water "
                    "in the presence of sunlight and chlorophyll. Oxygen is released as a byproduct through stomata. "
                    "Formula: 6CO2 + 6H2O + Light Energy -> C6H12O6 + 6O2. Plants store excess glucose as starch."
                )
            },
            {
                "id": "bio_photo_or_1",
                "subject": "Biology",
                "topic": "ଆଲୋକ ଶ୍ଳେଷଣ (Photosynthesis)",
                "language": "or",
                "grade": "Class 7-10",
                "source": "ଓଡ଼ିଶା ମାଧ୍ୟମିକ ଶିକ୍ଷା ପରିଷଦ (BSE Odisha)",
                "text": (
                    "ଆଲୋକ ଶ୍ଳେଷଣ ପ୍ରକ୍ରିୟା: ସବୁଜ ଉଦ୍ଭିଦମାନେ ସୂର୍ଯ୍ୟାଲୋକ ଓ ହରିତ୍‌କଣା (Chlorophyll) ସାହାଯ୍ୟରେ ବାୟୁମଣ୍ଡଳର ଅଙ୍ଗାରକାମ୍ଳ (CO2) "
                    "ଏବଂ ମାଟିରୁ ଜଳ (H2O) ଗ୍ରହଣ କରି ଗ୍ଲୁକୋଜ ପ୍ରସ୍ତୁତ କରନ୍ତି ଏବଂ ଅମ୍ଳଜାନ (O2) ଛାଡ଼ନ୍ତି। "
                    "ସମୀକରଣ: 6CO2 + 6H2O + ଆଲୋକ -> C6H12O6 + 6O2। ଏହି ଖାଦ୍ୟ ଉଦ୍ଭିଦରେ ଶ୍ୱେତସାର (Starch) ଭାବରେ ସଞ୍ଚିତ ହୁଏ।"
                )
            },
            {
                "id": "bio_photo_ta_1",
                "subject": "Biology",
                "topic": "ஒளிச்சேர்க்கை (Photosynthesis)",
                "language": "ta",
                "grade": "Class 7-10",
                "source": "தமிழ்நாடு பாடநூல் கழகம்",
                "text": (
                    "ஒளிச்சேர்க்கை: பசுந்தாவரங்கள் சூரிய ஒளி மற்றும் பச்சையம் உதவியுடன் கார்பன் டை ஆக்சைடு மற்றும் நீரைப் பயன்படுத்தி "
                    "குளுக்கோஸ் தயாரிக்கும் செயல்முறை ஒளிச்சேர்க்கை எனப்படும். இதன் மூலம் ஆக்சிஜன் வெளியேற்றப்படுகிறது."
                )
            },
            {
                "id": "bio_photo_te_1",
                "subject": "Biology",
                "topic": "కిరణజన్య సంయోగక్రియ (Photosynthesis)",
                "language": "te",
                "grade": "Class 7-10",
                "source": "తెలుగు అకాడమీ & SCERT",
                "text": (
                    "కిరణజన్య సంయోగక్రియ: మొక్కలు సూర్యకాంతి మరియు క్లోరోఫిల్ సమక్షంలో కార్బన్ డయాక్సైడ్ మరియు నీటిని ఉపయోగించి "
                    "గ్లూకోజ్ తయారుచేసే ప్రక్రియ. ఈ ప్రక్రియలో ఆక్సిజన్ ఉప ఉత్పత్తిగా విడుదలవుతుంది."
                )
            },

            # Mathematics - Pythagoras Theorem & Fractions
            {
                "id": "math_pyth_en_1",
                "subject": "Mathematics",
                "topic": "Pythagoras Theorem and Triangles",
                "language": "en",
                "grade": "Class 7-10",
                "source": "NCERT Mathematics Chapter 6",
                "text": (
                    "In a right-angled triangle, the square of the hypotenuse is equal to the sum of the squares of the other two sides. "
                    "Formula: a^2 + b^2 = c^2, where c is the hypotenuse (the side opposite the 90-degree angle). "
                    "Classic Pythagorean triples include (3, 4, 5) and (5, 12, 13)."
                )
            },
            {
                "id": "math_pyth_or_1",
                "subject": "Mathematics",
                "topic": "ପିଥାଗୋରାସ ଉପପାଦ୍ୟ (Pythagoras Theorem)",
                "language": "or",
                "grade": "Class 7-10",
                "source": "ଓଡ଼ିଶା ମାଧ୍ୟମିକ ଶିକ୍ଷା ପରିଷଦ (BSE Odisha)",
                "text": (
                    "ସମକୋଣୀ ତ୍ରିଭୁଜରେ କର୍ଣ୍ଣର ବର୍ଗ, ଅନ୍ୟ ଦୁଇ ବାହୁର ବର୍ଗର ଯୋଗଫଳ ସହିତ ସମାନ। "
                    "ସୂତ୍ର: କର୍ଣ୍ଣ^୨ = ଭୂମି^୨ + ଉଚ୍ଚତା^୨ (a^2 + b^2 = c^2)। "
                    "ଉଦାହରଣ: ଯଦି ଗୋଟିଏ ବାହୁ ୩ ସେମି ଓ ଅନ୍ୟଟି ୪ ସେମି, ତେବେ କର୍ଣ୍ଣ = √(୯ + ୧୬) = √୨୫ = ୫ ସେମି।"
                )
            },

            # Computer Science & Agentic AI
            {
                "id": "cs_agentic_en_1",
                "subject": "Computer Science",
                "topic": "Agentic AI Architecture vs Conventional Chatbots",
                "language": "en",
                "grade": "Advanced EdTech",
                "source": "Nextech 2.0 Agentic AI Architecture Guidelines",
                "text": (
                    "A conventional chatbot waits for a prompt, calls an LLM, and prints text. It lacks agency. "
                    "An Agentic AI system possesses: 1) Goal Formulation, 2) Multi-step Planning, 3) Tool Calling (RAG, Math, Diagnostics), "
                    "4) State and Memory Tracking, and 5) Self-Correction / Failure Handling. "
                    "In EdTech, the agent decides pedagogical interventions dynamically based on student cognitive state."
                )
            },
            {
                "id": "cs_agentic_or_1",
                "subject": "Computer Science",
                "topic": "ଏଜେଣ୍ଟିକ ଏଆଇ ବନାମ ସାଧାରଣ ଚାଟବଟ୍ (Agentic AI vs Chatbot)",
                "language": "or",
                "grade": "Advanced EdTech",
                "source": "ନେକ୍ସଟେକ୍ ୨.୦ ଏଜେଣ୍ଟିକ ନିର୍ଦ୍ଦେଶାବଳୀ",
                "text": (
                    "ସାଧାରଣ ଚାଟବଟ୍ କେବଳ ଉତ୍ତର ଦେଇଦିଏ, କିନ୍ତୁ ଏଜେଣ୍ଟିକ ଏଆଇ (Agentic AI) ଏକ ସ୍ୱୟଂଶାସିତ ଇଞ୍ଜିନ୍। "
                    "ଏହା ଛାତ୍ରର ଶିକ୍ଷଣ ଦକ୍ଷତା ମାପି ପରବର୍ତ୍ତୀ ପଦକ୍ଷେପ ନିଜେ ନିଷ୍ପତ୍ତି ନିଏ। ଏଥିରେ ଟୁଲ୍ କଲିଂ (RAG ତଥ୍ୟ ସନ୍ଧାନ, କୁଇଜ୍ ନିର୍ମାଣ, ତ୍ରୁଟି ସଂଶୋଧନ) "
                    "ଏବଂ ଅଫଲାଇନ୍ ସିଙ୍କ୍ ବ୍ୟବସ୍ଥା ଅନ୍ତର୍ଭୁକ୍ତ ଥାଏ।"
                )
            }
        ]
        self.chunks.extend(default_docs)

    def _load_custom_uploads(self):
        """Loads index file of custom uploaded documents if present."""
        index_file = os.path.join(self.uploads_dir, "custom_index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    custom_chunks = json.load(f)
                    self.chunks.extend(custom_chunks)
            except Exception as e:
                print(f"Error loading custom uploads: {e}")

    def _build_index(self):
        """Builds TF-IDF vectorizer over all text chunks."""
        if not self.chunks:
            return
        corpus = [f"{c['topic']} {c['subject']} {c['text']}" for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b"
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def query(self, query_text: str, top_k: int = 3, language_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant chunks using hybrid vector similarity and keyword boosting.
        """
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query_text])
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        scored_results = []
        q_tokens = set(re.findall(r"\w+", query_text.lower()))

        for idx, chunk in enumerate(self.chunks):
            base_score = float(sim_scores[idx])

            # Language priority boost
            if language_filter and chunk.get("language") == language_filter:
                base_score *= 1.35

            # Keyword presence bonus
            chunk_tokens = set(re.findall(r"\w+", chunk["text"].lower() + " " + chunk["topic"].lower()))
            overlap = len(q_tokens.intersection(chunk_tokens))
            keyword_boost = 0.05 * min(overlap, 5)

            final_score = base_score + keyword_boost
            scored_results.append((final_score, chunk))

        # Sort descending
        scored_results.sort(key=lambda x: x[0], reverse=True)

        top_results = []
        for score, chunk in scored_results[:top_k]:
            res = dict(chunk)
            res["score"] = round(float(score), 4)
            top_results.append(res)

        return top_results

    def ingest_text_document(self, title: str, text: str, subject: str = "General", language: str = "en", source: str = "Teacher Upload") -> int:
        """
        Splits uploaded text into chunks and updates index.
        """
        # Chunking by sentences or paragraphs (roughly 200 words per chunk)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]

        new_chunks = []
        for i, para in enumerate(paragraphs):
            chunk_id = f"custom_{len(self.chunks) + i + 1}"
            chunk = {
                "id": chunk_id,
                "subject": subject,
                "topic": title,
                "language": language,
                "grade": "Custom Curriculum",
                "source": source,
                "text": para
            }
            new_chunks.append(chunk)

        self.chunks.extend(new_chunks)
        self._build_index()

        # Persist custom chunks
        self._save_custom_index()
        return len(new_chunks)

    def ingest_pdf_file(self, file_path: str, title: str, subject: str = "General", language: str = "en") -> int:
        """Extracts text from PDF and ingests into RAG store."""
        reader = pypdf.PdfReader(file_path)
        extracted_text = []
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(page_text)

        full_text = "\n\n".join(extracted_text)
        return self.ingest_text_document(title, full_text, subject=subject, language=language, source=os.path.basename(file_path))

    def _save_custom_index(self):
        """Saves custom uploaded chunks to disk."""
        index_file = os.path.join(self.uploads_dir, "custom_index.json")
        custom_chunks = [c for c in self.chunks if c["id"].startswith("custom_")]
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(custom_chunks, f, ensure_ascii=False, indent=2)

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics for Developer telemetry dashboard."""
        lang_counts = {}
        for c in self.chunks:
            l = c.get("language", "unknown")
            lang_counts[l] = lang_counts.get(l, 0) + 1

        return {
            "total_chunks": len(self.chunks),
            "languages": lang_counts,
            "vector_dimension": self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0,
            "custom_uploads": len([c for c in self.chunks if c["id"].startswith("custom_")])
        }

# Global singleton instance
rag_engine = RAGEngine()
