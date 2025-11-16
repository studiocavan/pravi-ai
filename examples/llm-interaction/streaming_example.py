"""
Streaming LLM Responses Example

This example demonstrates how to handle streaming responses from LLMs,
which is useful for real-time applications and better user experience.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# Load environment variables
load_dotenv()


def stream_openai():
    """Stream responses from OpenAI GPT"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("OpenAI Streaming Example:")
    print("Question: Write a short poem about AI")
    print("\nResponse (streaming):\n")

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Write a short poem about AI"}
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n\n" + "="*50 + "\n")


def stream_anthropic():
    """Stream responses from Anthropic Claude"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print("Anthropic Claude Streaming Example:")
    print("Question: Explain how neural networks learn")
    print("\nResponse (streaming):\n")

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Explain how neural networks learn in 3 paragraphs"}
        ]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n\n" + "="*50 + "\n")


def stream_with_events():
    """Stream with event handling for more control"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print("Streaming with Event Handling:")
    print("Question: What are the benefits of streaming LLM responses?")
    print("\nResponse:\n")

    word_count = 0

    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "What are the benefits of streaming LLM responses? Be concise."
            }
        ]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            # Count words as they arrive
            word_count += len(text.split())

    print(f"\n\nTotal words streamed: ~{word_count}")
    print("\n" + "="*50 + "\n")


async def async_stream_example():
    """Asynchronous streaming example"""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print("Async Streaming Example:")
    print("Question: List 5 uses of AI in healthcare")
    print("\nResponse:\n")

    async with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "List 5 uses of AI in healthcare"}
        ]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n\n" + "="*50 + "\n")


def main():
    """Run streaming examples"""
    import asyncio

    try:
        print("Streaming LLM Responses Examples\n")

        stream_openai()
        stream_anthropic()
        stream_with_events()

        # Run async example
        asyncio.run(async_stream_example())

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to set your API keys in a .env file")


if __name__ == "__main__":
    main()
