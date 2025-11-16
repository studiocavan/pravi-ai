"""
OpenAI GPT API Example

This example demonstrates how to interact with OpenAI's GPT models
for text generation, chat completions, and basic prompting.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


def simple_completion():
    """Basic text completion example"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        temperature=0.7,
        max_tokens=150
    )

    print("Simple Completion Response:")
    print(response.choices[0].message.content)
    print("\n" + "="*50 + "\n")


def chat_with_context():
    """Chat completion with conversation history"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {"role": "system", "content": "You are a knowledgeable AI assistant."},
        {"role": "user", "content": "Tell me about Python programming."},
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})

    print("Assistant:", assistant_message)

    # Follow-up question
    messages.append({"role": "user", "content": "What are its main advantages?"})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print("\nFollow-up Response:")
    print(response.choices[0].message.content)
    print("\n" + "="*50 + "\n")


def get_embeddings():
    """Generate text embeddings"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    text = "Embeddings are vector representations of text"

    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )

    embedding = response.data[0].embedding

    print("Text Embeddings Example:")
    print(f"Text: {text}")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print("\n" + "="*50 + "\n")


def main():
    """Run all examples"""
    try:
        print("OpenAI API Examples\n")

        simple_completion()
        chat_with_context()
        get_embeddings()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to set your OPENAI_API_KEY in a .env file")


if __name__ == "__main__":
    main()
