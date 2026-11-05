import os
import json
from google import genai
from src.config import settings
from src.schemas import TranscriptChunk, ExtractedTopic
from src.distiller.prompts import TOPIC_EXTRACTION_PROMPT

class TopicExtractor:
    def __init__(self, comedy_threshold: float = 7.0):
        self.comedy_threshold = comedy_threshold
        # The genai client expects GOOGLE_API_KEY env var or explicitly passed
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-pro"

    def read_recent_chunks(self, filepath: str) -> list[TranscriptChunk]:
        """
        Reads all chunks from the JSONL file. In a real scenario, this would filter
        by a time interval (e.g., last 24 hours).
        """
        chunks = []
        if not os.path.exists(filepath):
            return chunks

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunk_data = json.loads(line)
                    chunks.append(TranscriptChunk(**chunk_data))
        return chunks

    def extract_topics(self, chunks: list[TranscriptChunk]) -> list[ExtractedTopic]:
        """
        Uses Gemini to extract high-value topics from transcript chunks.
        """
        if not chunks:
            return []

        # Format chunks into a readable string for the prompt
        transcript_text = "\n".join([f"[{c.timestamp}] {c.speaker_id}: {c.text} (ID: {c.ID})" for c in chunks])

        full_prompt = f"{TOPIC_EXTRACTION_PROMPT}\n\nTranscript:\n{transcript_text}"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            raw_json = response.text
            topics_data = json.loads(raw_json)

            extracted_topics = []
            for item in topics_data:
                topic = ExtractedTopic(**item)
                if topic.comedy_score >= self.comedy_threshold:
                    extracted_topics.append(topic)

            return extracted_topics

        except Exception as e:
            print(f"Error extracting topics: {e}")
            return []

def run_extraction():
    extractor = TopicExtractor()
    transcripts_file = os.path.join(settings.TRANSCRIPT_STORAGE_DIR, "transcripts.jsonl")
    chunks = extractor.read_recent_chunks(transcripts_file)
    topics = extractor.extract_topics(chunks)

    print(f"Extracted {len(topics)} topics with score >= {extractor.comedy_threshold}")
    for t in topics:
        print(f"- {t.title} (Score: {t.comedy_score})")

if __name__ == "__main__":
    run_extraction()