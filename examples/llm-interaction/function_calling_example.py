"""
Function Calling / Tool Use Example

This example demonstrates how to use function calling (OpenAI) and
tool use (Anthropic) to enable LLMs to interact with external tools and APIs.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# Load environment variables
load_dotenv()


# Example functions that the LLM can call
def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Simulated weather API call
    In a real application, this would call an actual weather API
    """
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 65
    }


def calculate_sum(numbers: list) -> float:
    """Calculate the sum of a list of numbers"""
    return sum(numbers)


def search_database(query: str, limit: int = 5) -> list:
    """
    Simulated database search
    In a real application, this would query an actual database
    """
    return [
        {"id": 1, "title": f"Result for '{query}' #1", "relevance": 0.95},
        {"id": 2, "title": f"Result for '{query}' #2", "relevance": 0.87},
        {"id": 3, "title": f"Result for '{query}' #3", "relevance": 0.76},
    ][:limit]


def openai_function_calling():
    """OpenAI function calling example"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Define the functions available to the model
    functions = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]

    messages = [
        {"role": "user", "content": "What's the weather like in Paris?"}
    ]

    print("OpenAI Function Calling Example:")
    print(f"User: {messages[0]['content']}\n")

    # First API call
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=functions,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"Function called: {function_name}")
            print(f"Arguments: {function_args}\n")

            # Call the actual function
            if function_name == "get_weather":
                function_response = get_weather(**function_args)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response)
            })

        # Second API call with function result
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        print(f"Assistant: {final_response.choices[0].message.content}")

    print("\n" + "="*50 + "\n")


def anthropic_tool_use():
    """Anthropic Claude tool use example"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Define tools
    tools = [
        {
            "name": "calculate_sum",
            "description": "Calculates the sum of a list of numbers",
            "input_schema": {
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numbers to sum"
                    }
                },
                "required": ["numbers"]
            }
        },
        {
            "name": "search_database",
            "description": "Search the database for relevant information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    ]

    print("Anthropic Tool Use Example:")
    user_message = "Can you search the database for 'machine learning' and also calculate the sum of 15, 23, and 42?"
    print(f"User: {user_message}\n")

    messages = [{"role": "user", "content": user_message}]

    # First API call
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    # Process tool use
    if response.stop_reason == "tool_use":
        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})

        # Process each tool use
        tool_results = []
        for content_block in response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input

                print(f"Tool used: {tool_name}")
                print(f"Input: {tool_input}\n")

                # Execute the tool
                if tool_name == "calculate_sum":
                    result = calculate_sum(tool_input["numbers"])
                elif tool_name == "search_database":
                    result = search_database(
                        tool_input["query"],
                        tool_input.get("limit", 5)
                    )

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": json.dumps(result)
                })

        # Add tool results to messages
        messages.append({"role": "user", "content": tool_results})

        # Second API call with tool results
        final_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"Assistant: {final_response.content[0].text}")

    print("\n" + "="*50 + "\n")


def main():
    """Run function calling examples"""
    try:
        print("Function Calling / Tool Use Examples\n")

        openai_function_calling()
        anthropic_tool_use()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to set your API keys in a .env file")


if __name__ == "__main__":
    main()
