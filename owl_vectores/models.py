# owl-vectores/owl_vectores/models.py
import openai
import numpy as np
import warnings
import yaml

with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

EMBEDDING_MODEL = config["models"]["embedding"]["model"]
COMPLETION_MODEL = config["models"]["completion"]["model"]
MAX_TOKENS = config["models"]["completion"]["max_tokens"]


def get_embedding(text, api_key, model="text-embedding-ada-002"):
    openai.api_key = api_key
    try:
        if text is None or len(text) == 0:
            return None

        input_list = [text]
        response = openai.Embedding.create(input=input_list, model=model)
        return np.array(response["data"][0]["embedding"])
    except Exception as e:
        warnings.warn(f"Embedding failed for text: {text}. Error: {str(e)}")
        return None


def get_completion(prompt, api_key, model="text-davinci-002", max_tokens=100):
    openai.api_key = api_key
    try:
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        warnings.warn(f"Completion failed for prompt: {prompt}. Error: {str(e)}")
        return None
