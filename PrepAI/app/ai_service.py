import json
from openai import OpenAI
from .config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_quiz_questions_from_text(text: str):
    # Simple chunking strategy
    words = text.split()
    chunk_size = 1500
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    all_questions = []

    for chunk in chunks:
        prompt = f"""
        Based on the following text, generate 2 multiple-choice questions.
        The output must be a valid JSON object containing a list of questions.
        Each question object must have the following keys: "question_text", "options" (a list of 4 strings), and "correct_answer" (the string of the correct option).
        The options should be plausible and relevant to the text.

        Text:
        ---
        {chunk}
        ---
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates quiz questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        try:
            questions_data = json.loads(response.choices[0].message.content)
            all_questions.extend(questions_data.get("questions", []))
        except (json.JSONDecodeError, KeyError) as e:
            # Handle cases where the LLM response is not valid JSON or doesn't have the expected structure
            print(f"Error parsing LLM response: {e}")
            continue

    return all_questions