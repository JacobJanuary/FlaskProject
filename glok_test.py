
XAI_API_KEY = "xai-AEbygKMNvz46KLqCszO6UEp3RDpc0DyWmwLpwOnNlM18BWF0rUwuHGPVSUykOxAyRuGKoT48IzCOSvvm"
# Querying chat models with xAI
from anthropic import Anthropic

client = Anthropic(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai",
)

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}]
)
print(message.content)