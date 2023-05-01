from romeo_gpt.utils.models.models import get_completion


def documents_agent(language, text_chunks, task, api_key):
    """
    Retrieve an answer from the most relevant document using text chunks and a task.

    Args:
        language (str): The language of the document.
        text_chunks (str): The analyzed text chunks from the relevant document.
        task (str): The task to be performed.
        api_key (str): The API key for accessing the completion model.

    Returns:
        str: The generated answer based on the text chunks and task.
    """
    # Prepare the context extractor template
    context_extractor_template = [
        (
            f"As an AI assistant, I have analyzed the following text chunks from the most relevant document to answer "
            f"your task in {language}:\n\n{text_chunks}\n\n Your task: {task}\n\n Answer:"
        )
    ]

    # Format the prompts using the template
    formatted_prompts = [
        template.format(language=language, text_chunks=text_chunks, task=task)
        for template in context_extractor_template
    ]

    # Join the formatted prompts with newlines as the prompt
    prompt = "\n\n".join(formatted_prompts)

    # Get the completion using the prompt and API key
    answer = get_completion(prompt=prompt, api_key=api_key)

    return answer
