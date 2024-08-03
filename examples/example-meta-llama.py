# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="meta-llama/Meta-Llama-3.1-8B", max_new_tokens=512)
pipe("Hey how are you doing today?")