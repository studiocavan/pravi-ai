"""
Anthropic Claude API Example

This example demonstrates how to interact with Anthropic's Claude models
for text generation, structured conversations, and advanced prompting.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()


def simple_message():
    """Basic message completion with Claude"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ]
    )

    print("Simple Message Response:")
    print(message.content[0].text)
    print("\n" + "="*50 + "\n")


def conversation_with_system_prompt():
    """Conversation with system prompt and context"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="You are a Python programming expert who explains concepts clearly.",
        messages=[
            {
                "role": "user",
                "content": "What is a decorator in Python and when should I use it?"
            }
        ]
    )

    print("Conversation with System Prompt:")
    print(message.content[0].text)
    print("\n" + "="*50 + "\n")


def multi_turn_conversation():
    """Multi-turn conversation maintaining context"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    messages = [
        {"role": "user", "content": "I'm learning about machine learning. What should I start with?"}
    ]

    # First turn
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=messages
    )

    print("Turn 1 - User: I'm learning about machine learning. What should I start with?")
    print(f"Assistant: {response.content[0].text}\n")

    # Add assistant's response to messages
    messages.append({"role": "assistant", "content": response.content[0].text})

    # Second turn
    messages.append({
        "role": "user",
        "content": "Can you recommend some good Python libraries for beginners?"
    })

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=messages
    )

    print("Turn 2 - User: Can you recommend some good Python libraries for beginners?")
    print(f"Assistant: {response.content[0].text}")
    print("\n" + "="*50 + "\n")


def structured_output_example():
    """Request structured output from Claude"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": """Analyze this sentence and return a JSON object with:
                - sentiment (positive/negative/neutral)
                - key_topics (list of main topics)
                - word_count

                Sentence: "I absolutely love programming in Python, it's so elegant and powerful!"

                Return only the JSON, no other text."""
            }
        ]
    )

    print("Structured Output Example:")
    print(message.content[0].text)
    print("\n" + "="*50 + "\n")


def main():
    """Run all examples"""
    try:
        print("Anthropic Claude API Examples\n")

        simple_message()
        conversation_with_system_prompt()
        multi_turn_conversation()
        structured_output_example()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to set your ANTHROPIC_API_KEY in a .env file")


if __name__ == "__main__":
    main()
