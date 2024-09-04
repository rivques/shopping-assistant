# a simple client for the OpenAI Chat Completion API
# no openai library, just raw http requests

class OpenAIClient:
    def __init__(self, requests, api_key, base_url="https://api.openai.com/v1/"):
        self.requests = requests
        self.api_key = api_key
        self.base_url = base_url

    def create_completion(self, model, messages, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": model,
            "messages": messages,
        }
        data.update(kwargs)
        print(f"Sending request to {self.base_url}chat/completions")
        response = self.requests.post(
            f"{self.base_url}chat/completions",
            headers=headers,
            json=data,
        )
        print(f"Got response (code {response.status_code})")

        return response.json()