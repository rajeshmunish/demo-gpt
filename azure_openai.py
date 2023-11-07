#from dotenv import load_dotenv
#import os
import openai

#load_dotenv()

# openai.api_type = os.getenv('OPENAI_API_TYPE')
# openai.api_base = os.getenv('OPENAI_API_BASE')
# openai.api_version = os.getenv('OPENAI_API_VERSION')
# deployment_name = os.getenv('OPENAI_API_DEPLOYMENT_NAME')
# openai.api_key = os.getenv('OPENAI_API_KEY')


openai.api_type = "azure"
openai.api_base = "https://ubti-d-ecanada-openai-ml.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
deployment_name = "ubti-gpt4-depmodel"
openai.api_key = "c99f5b66665a4284a7ab1f6f17ad9680"

def get_completion_from_messages(system_message, user_message, model=deployment_name, temperature=0, max_tokens=500) -> str:

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"Get Portfolio's Market price"},
        {'role': 'assistant', 'content': f"market price = marketprice from securitydolleranalytics join with security positions, portfolio. Use securityid and effectivedt/asofdate to join position and securitydolleranalytics. Use Portfoliocode to join portfolio and positions."},
        {'role': 'user', 'content': f"How to get the latest position"},
        {'role': 'assistant', 'content': f"Join with security, position and portfolio. Use securityid and effectivedt/asofdate to join position and security. Use Portfoliocode to join portfolio and positions."},
        {'role': 'user', 'content': f"{user_message}"}
    ]
    
    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    
    return response.choices[0].message["content"]

if __name__ == "__main__":
    system_message = "You are a helpful assistant"
    user_message = "Hello, how are you?"
    print(get_completion_from_messages(system_message, user_message))