from opik import Opik, track
from opik.evaluation import evaluate
from opik.evaluation.metrics import Equals, Hallucination
from opik.integrations.openai import track_openai
import openai
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()
MODEL = "gpt-4o"
@track
def _llm_model_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs) -> str:
    """LLM 模型函数"""
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    chat_completion = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=messages,
        temperature=kwargs.get("temperature", 0),
        top_p=kwargs.get("top_p", 1),
        n=kwargs.get("n", 1),
    )
    return chat_completion.choices[0].message.content




# def your_llm_application(input: str) -> str:
#     response = openai_client.chat.completions.create(
#         model=MODEL,
#         messages=[{"role": "user", "content": input}],
#     )
#     return response.choices[0].message.content
print(_llm_model_func("What is the capital of France?"))






# Define the evaluation task
def evaluation_task(x):
    return {
        "output": _llm_model_func(x['input'])
    }

# Create a simple dataset
client = Opik()
dataset = client.get_or_create_dataset(name="Example dataset")
dataset.insert([
    {"input": "What is the capital of France?"},
    {"input": "What is the capital of Germany?"},
])

# Define the metrics
hallucination_metric = Hallucination()

evaluation = evaluate(
    dataset=dataset,
    task=evaluation_task,
    scoring_metrics=[hallucination_metric],
    experiment_config={
        "model": MODEL
    }
)


# import opik
# from opik.evaluation import evaluate
# from opik.evaluation.metrics import ContextPrecision, ContextRecall

# # Create a dataset with questions and their contexts
# opik_client = opik.Opik()
# dataset = opik_client.get_or_create_dataset("RAG evaluation dataset")
# dataset.insert([
#     {
#         "input": "What are the key features of Python?",
#         "context": "Python is known for its simplicity and readability. Key features include dynamic typing, automatic memory management, and an extensive standard library.",
#         "expected_output": "Python's key features include dynamic typing, automatic memory management, and an extensive standard library."
#     },
#     {
#         "input": "How does garbage collection work in Python?",
#         "context": "Python uses reference counting and a cyclic garbage collector. When an object's reference count drops to zero, it is deallocated.",
#         "expected_output": "Python uses reference counting for garbage collection. Objects are deallocated when their reference count reaches zero."
#     }
# ])

# def rag_task(item):
#     # Simulate RAG pipeline
#     output = "<LLM response placeholder>"

#     return {
#         "output": output
#     }

# # Run the evaluation
# result = evaluate(
#     dataset=dataset,
#     task=rag_task,
#     scoring_metrics=[
#         ContextPrecision(),
#         ContextRecall()
#     ],
#     experiment_name="rag_evaluation"
# )
