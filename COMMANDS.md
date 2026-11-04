# Commands

Run everything from the project folder (`hopscotch-exchange-desk`). Commands are for Windows PowerShell; macOS/Linux differences are noted.

## 1. Create and activate the venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # macOS/Linux: source .venv/bin/activate
```

If PowerShell blocks the activate script, run this once, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 2. Install requirements

```powershell
pip install -r requirements.txt
```

## 3. Add your API key

```powershell
copy .env.example .env              # macOS/Linux: cp .env.example .env
```

Open `.env` and set:

```
OPENROUTER_API_KEY=your-key
```

The name must be exactly `OPENROUTER_API_KEY`.

## 4. Run the backend (terminal)

```powershell
python main.py
```

Runs every test message through the desk and prints the claim, tone, tool trips and outcome.

## 5. Run the frontend (Streamlit UI)

```powershell
streamlit run app.py
```

Open http://localhost:8501. Press `Ctrl+C` in the terminal to stop it.

The UI runs the graph itself, so you don't need to start the backend first.

## Every new terminal

Activate the venv again before running anything:

```powershell
.\.venv\Scripts\Activate.ps1
```
