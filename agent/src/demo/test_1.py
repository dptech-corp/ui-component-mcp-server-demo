import opik
from opik.evaluation import evaluate_prompt
from opik.evaluation.metrics import Hallucination
from dotenv import load_dotenv
from opik.evaluation.models.litellm.litellm_chat_model import LiteLLMChatModel
import os
load_dotenv()
MODEL = "gpt-4o"
# Create a dataset that contains the samples you want to evaluate
opik_client = opik.Opik()
dataset = opik_client.get_or_create_dataset("Evaluation test dataset")
dataset.insert([
    {"input": "Hello, world!", "expected_output": "Hello, world!"},
    {"input": "What is the capital of France?", "expected_output": "Paris"},
])
model=LiteLLMChatModel(
        model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_API_BASE_URL")),
# Run the evaluation
result = evaluate_prompt(
    dataset=dataset,
    messages=[{"role": "user", "content": "Translate the following text to French: {{input}}"}],
    model=model,  # or your preferred model
    scoring_metrics=[Hallucination()]
)
