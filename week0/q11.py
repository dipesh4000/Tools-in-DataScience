# Create a FastAPI endpoint for batch sentiment analysis
# Build a POST endpoint at /sentiment that accepts multiple sentences and returns their sentiments. You can use any method (Ollama, rule-based, ML model, etc.).

# Requirements:
# Accept JSON with array of sentences: {"sentences": ["I love this!", "I'm sad.", ...]}
# Return JSON with results array: {"results": [{"sentence": "I love this!", "sentiment": "happy"}, ...]}
# Valid sentiments: "happy", "sad", or "neutral"
# Return all sentences in the same order as input
# Pass at least 7 out of 10 test cases to get full score
# Example Request:
# POST http://localhost:8000/sentiment
# Content-Type: application/json

# {
#   "sentences": [
#     "I love this product!",
#     "This is terrible.",
#     "The meeting is at 3 PM."
#   ]
# }
# Example Response:
# {
#   "results": [
#     {"sentence": "I love this product!", "sentiment": "happy"},
#     {"sentence": "This is terrible.", "sentiment": "sad"},
#     {"sentence": "The meeting is at 3 PM.", "sentiment": "neutral"}
#   ]
# }
# Enter your FastAPI URL:
# http://localhost:8000
# Error: Request failed: Failed to fetch
# Note: The evaluation will test 10 random sentences in a single POST request.


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HAPPY = {"love", "great", "excellent", "amazing", "wonderful", "fantastic", "good", "happy", "joy", "best", "awesome", "superb", "glad", "excited", "brilliant", "perfect", "nice", "enjoy", "enjoyed", "delightful", "pleased", "thrilled", "grateful", "thankful", "fun", "beautiful", "incredible"}
SAD = {"hate", "terrible", "awful", "bad", "sad", "worst", "horrible", "disappointing", "disappointed", "upset", "angry", "annoyed", "frustrated", "depressed", "miserable", "poor", "unhappy", "regret", "sorry", "fail", "failed", "useless", "broken", "disgusting", "dreadful", "pathetic"}

class SentimentRequest(BaseModel):
    sentences: List[str]

@app.post("/sentiment")
def sentiment(req: SentimentRequest):
    results = []
    for sentence in req.sentences:
        words = set(sentence.lower().split())
        if words & HAPPY:
            sentiment = "happy"
        elif words & SAD:
            sentiment = "sad"
        else:
            sentiment = "neutral"
        results.append({"sentence": sentence, "sentiment": sentiment})
    return {"results": results}
