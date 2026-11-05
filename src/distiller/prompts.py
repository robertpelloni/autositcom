TOPIC_EXTRACTION_PROMPT = """
You are an expert sitcom writer and narrative distiller.
Read the provided transcript chunks of real-life conversations.
Your task is to identify and extract high-value, humorous, absurd, or deep conversation topics that would make excellent seeds for a sitcom episode.

For each interesting topic found:
1. Provide a 'topic_id' (a unique string like 'topic_xyz').
2. Provide a short 'title' for the topic.
3. Provide a 'summary' explaining why this topic is funny or interesting, and what the core character dynamics are.
4. Extract an array of 'key_quotes' (exact quotes from the transcript) that highlight the topic.
5. Assign a 'comedy_score' from 0.0 to 10.0 based on its comedic potential or narrative value.
6. Provide a list of 'source_chunk_ids' from which this topic was derived.

Return ONLY a valid JSON array of objects matching this exact structure:
[
  {
    "topic_id": "string",
    "title": "string",
    "summary": "string",
    "key_quotes": ["string", "string"],
    "comedy_score": 8.5,
    "source_chunk_ids": ["chunk_id_1", "chunk_id_2"]
  }
]
"""