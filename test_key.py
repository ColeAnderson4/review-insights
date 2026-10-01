from dotenv import load_dotenv
import anthropic

load_dotenv()  # reads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()

# Free check: lists available models without using credits
for m in client.models.list():
    print(m.id)