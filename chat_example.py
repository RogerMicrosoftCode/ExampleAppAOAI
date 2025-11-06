#!/usr/bin/env python3
"""
Example Azure OpenAI Chat Completion Application

This script demonstrates how to use the Azure OpenAI service to create
a simple chat completion application.
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv


def main():
    """Main function to run the Azure OpenAI chat example."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Validate required configuration
    if not all([endpoint, api_key, deployment_name]):
        print("Error: Missing required environment variables.")
        print("Please copy .env.example to .env and configure your Azure OpenAI settings.")
        return
    
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    print("Azure OpenAI Chat Example")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    # Message history for conversation context
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Create chat completion
            response = client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            # Get assistant's response
            assistant_message = response.choices[0].message.content
            
            # Add assistant message to history
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Display response
            print(f"\nAssistant: {assistant_message}\n")
            
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            # Remove the user message that caused the error
            messages.pop()


if __name__ == "__main__":
    main()
