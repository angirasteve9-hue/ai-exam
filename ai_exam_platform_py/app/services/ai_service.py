import os
import json
from openai import OpenAI

# Initialize client (ensure OPENAI_API_KEY is allowed in env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def structure_exam_content(raw_text: str):
    """
    Uses OpenAI to convert raw PDF text into a structured JSON exam format.
    """
    prompt = f"""
    You are an expert exam digitizer. Convert the following raw text from an exam paper into a structured JSON format.
    
    The JSON structure should be:
    {{
      "exam_title": "Title found in text",
      "subject": "Subject found in text",
      "questions": [
        {{
          "question_number": "1a",
          "text": "The full question text...",
          "marks": 5,
          "type": "short_answer" | "long_answer" | "multiple_choice"
        }}
        ...
      ]
    }}
    
    If you cannot find a mark allocation, estimate it or put 1.
    
    RAW TEXT:
    {raw_text[:15000]}  # Truncate to avoid context limits if necessary
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"AI parsing error: {e}")
        return None

def grade_answer(question_text: str, mark_scheme: str, user_answer: str, max_marks: int):
    """
    Grades a single answer against the mark scheme/question.
    """
    prompt = f"""
    You are an expert examiner. Grade the following student answer.
    
    Question: {question_text}
    Mark Scheme / Correct Answer: {mark_scheme}
    Student Answer: {user_answer}
    Max Marks: {max_marks}
    
    Return JSON:
    {{
        "score_awarded": 3,
        "feedback": "Good point on X, but missed Y.",
        "improvement_tip": "Always mention Z in this type of question."
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"AI grading error: {e}")
        return {"score_awarded": 0, "feedback": "AI Error during grading", "improvement_tip": "N/A"}
