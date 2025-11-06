#!/usr/bin/env python3
"""
Simple Azure OpenAI Completion Example

This script demonstrates a simple one-shot completion using Azure OpenAI.
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv


def main():
    """Main function to run a simple Azure OpenAI completion example."""
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
    
    print("Azure OpenAI Simple Completion Example")
    print("=" * 50)
    
    # Create a simple completion request
    prompt = "Explain what Azure OpenAI is in one sentence."
    
    print(f"\nPrompt: {prompt}\n")
    
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        # Get and display the response
        completion = response.choices[0].message.content
        print(f"Response: {completion}\n")
        
        # Display usage information
        print(f"Tokens used: {response.usage.total_tokens}")
        print(f"  - Prompt tokens: {response.usage.prompt_tokens}")
        print(f"  - Completion tokens: {response.usage.completion_tokens}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
