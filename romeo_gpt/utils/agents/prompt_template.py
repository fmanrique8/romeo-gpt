# romeo-gtp/romeo_gpt/utils/agents/prompt_template.py


def get_prompt(language, text_chunks, question):
    prompt = (
        f"As an AI assistant, I have analyzed the following text chunks from the most relevant document to answer "
        f"your question in {language}:\n\n{text_chunks}\n\nYour question: {question}\n\nAnswer:"
    )
    return prompt
