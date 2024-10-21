import sqlite3
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def prompt(*args) -> str:
    text = args[0]

    try:
        chat_completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text},
            ],
            max_tokens=150,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    connection = sqlite3.connect(":memory:")
    connection.create_function("prompt", 1, prompt)

    cursor = connection.cursor()

    cursor.execute("CREATE TABLE texts (id INTEGER PRIMARY KEY, content TEXT)")
    cursor.execute(
        "INSERT INTO texts (content) VALUES ('SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.')"
    )
    cursor.execute(
        "INSERT INTO texts (content) VALUES ('Python is an interpreted high-level general-purpose programming language. It was created by Guido van Rossum and first released in 1989')"
    )

    result = cursor.execute(
        "SELECT prompt('Which programming language is in this text: ' || content) FROM texts"
    ).fetchall()
    print("Summary:", result)


if __name__ == "__main__":
    main()
