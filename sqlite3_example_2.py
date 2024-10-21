import json
from typing import List, Type
import sqlite3
import openai
import os
from dotenv import load_dotenv
from pydantic import Field, create_model

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

pydantic_types = {
    "VARCHAR": str,
    "INTEGER": int,
    "VARCHAR[]": List[str],
}


def create_pydantic_model(model_name: str, struct: dict, struct_descr: dict) -> Type:
    fields = {}

    for field_name, field_type in struct.items():
        fields[field_name] = (
            pydantic_types[field_type],
            Field(..., description=struct_descr[field_name]),
        )

    return create_model(model_name, **fields)


def prompt(*args) -> str:
    text = args[0]
    response_model = None

    if len(args) == 2:
        struct_dict = json.loads(args[1])
        struct = struct_dict["struct"]
        struct_descr = struct_dict["struct_descr"]

        response_model = create_pydantic_model("ResponseModel", struct, struct_descr)

    kwargs = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text},
        ],
    }

    if response_model:
        kwargs["response_format"] = response_model

    try:
        if response_model:
            chat_completion = openai.beta.chat.completions.parse(**kwargs)
            if chat_completion.choices[0].message.parsed:
                return str(chat_completion.choices[0].message.parsed.model_dump_json())
        else:
            chat_completion = openai.chat.completions.create(**kwargs)
            return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    connection = sqlite3.connect("top_hn_articles.db")
    connection.create_function("prompt", 2, prompt)

    cursor = connection.cursor()

    result = cursor.execute(
        """SELECT title, time, prompt('Extract this data from the article' || markdown, '{
            "struct": {
                "topic": "VARCHAR",
                "sentiment": "INTEGER",
                "technologies": "VARCHAR[]"
            },
            "struct_descr": {
                "topic": "topic of the post, single word",
                "sentiment": "sentiment of the post on a scale from 1 (neg) to 5 (pos)",
                "technologies": "technologies mentioned in the post"
            }
        }') as my_output 
        from top_articles limit 5"""
    ).fetchall()

    for row in result:
        print(row)


if __name__ == "__main__":
    main()
