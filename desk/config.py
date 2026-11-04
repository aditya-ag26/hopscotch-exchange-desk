import os

import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

if not os.getenv("OPENROUTER_API_KEY"):
    raise SystemExit("OPENROUTER_API_KEY is missing: copy .env.example to .env and add your key.")

llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    model_name="openai/gpt-4o-mini-2024-07-18",
    default_headers={
        "HTTP-Referer": os.getenv("APP_URL", "http://localhost"),
        "X-Title": os.getenv("APP_NAME", "hopscotch-exchange-desk"),
    },
)

RETURN_WINDOW_DAYS = 10
HIGH_VALUE = 5000  # INR
VENDOR_SPIKE = 15  # %
MAX_TRIPS = 4

PINCODE_API = "https://api.postalpincode.in/pincode/"
