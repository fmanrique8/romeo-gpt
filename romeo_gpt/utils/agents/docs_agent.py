# romeo-gtp/romeo_gpt/utils/agents/main.py
from romeo_gpt.models import get_completion


def documents_agent(language, text_chunks, task, api_key):
    context_extractor_template = [
        (
            f"As an AI assistant, I have analyzed the following text chunks from the most relevant document to answer "
            f"your task in {language}:\n\n{text_chunks}\n\n Your task: {task}\n\n Answer:"
        )
    ]

    formatted_prompts = [
        template.format(language=language, text_chunks=text_chunks, task=task)
        for template in context_extractor_template
    ]
    prompt = "\n\n".join(formatted_prompts)
    answer = get_completion(prompt=prompt, api_key=api_key)
    return answer
