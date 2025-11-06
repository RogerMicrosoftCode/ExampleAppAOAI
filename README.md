# ExampleAppAOAI

Example application demonstrating how to use Azure OpenAI service with Python.

## Overview

This repository contains simple Python examples that show how to integrate with Azure OpenAI service for chat completions and text generation.

## Features

- **Simple Completion Example**: Basic one-shot completion request
- **Interactive Chat Example**: Conversational AI with message history
- **Environment-based Configuration**: Secure API key management using .env files

## Prerequisites

- Python 3.7 or higher
- An Azure subscription
- An Azure OpenAI resource with a deployed model

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/RogerMicrosoftCode/ExampleAppAOAI.git
   cd ExampleAppAOAI
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Azure OpenAI credentials**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

## Usage

### Simple Completion Example

Run a basic one-shot completion:

```bash
python simple_example.py
```

This will send a single prompt to Azure OpenAI and display the response along with token usage information.

### Interactive Chat Example

Run an interactive chat session:

```bash
python chat_example.py
```

This starts an interactive conversation where you can chat with the AI. Type 'quit' or 'exit' to end the session.

## Examples

### Simple Completion
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-api-key",
    api_version="2024-02-15-preview"
)

response = client.chat.completions.create(
    model="your-deployment-name",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

## Configuration

### Environment Variables

- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI resource endpoint
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT_NAME`: The name of your deployed model
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)

## Getting Azure OpenAI Credentials

1. Go to the [Azure Portal](https://portal.azure.com/)
2. Navigate to your Azure OpenAI resource
3. Under "Keys and Endpoint", copy your endpoint and one of the keys
4. Under "Model deployments", note your deployment name

## Troubleshooting

### Common Issues

**Missing environment variables**
- Ensure you've copied `.env.example` to `.env` and filled in your credentials

**Authentication errors**
- Verify your API key is correct
- Check that your endpoint URL is properly formatted

**Model not found**
- Confirm your deployment name matches exactly with your Azure OpenAI deployment

## Security

- Never commit your `.env` file with real credentials
- Keep your API keys secure and rotate them regularly
- Use environment variables or Azure Key Vault for production deployments

## License

This is an example project for demonstration purposes.

## Resources

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Azure OpenAI Quickstart](https://learn.microsoft.com/azure/ai-services/openai/quickstart)
