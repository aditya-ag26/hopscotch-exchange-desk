# Hopscotch Exchange Desk

Reads a customer's exchange request, checks the facts with tools, and picks **Approve**, **Decline** or **Escalate**.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add your OPENROUTER_API_KEY
```

## Run

```bash
python main.py                  # all test messages
streamlit run app.py            # UI
```
