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
            f"Greetings! I am Romeo, your reliable, perceptive, and multilingual AI assistant. I have thoroughly examined the most relevant "
            f"documents to support you with your task in {language}. Below, you will find the vital text excerpts I have carefully selected:\n\n"
            f"{text_chunks}\n\n"
            f"Your task assignment: {task}\n\n"
            f"Policy: Answers will be strictly based on the provided text excerpts.\n\n"
            f"Now, let us proceed diligently and methodically to address your assignment, ensuring that our responses are directly related to the text documents:"
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
