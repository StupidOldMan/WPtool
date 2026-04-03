# WPtool

Python GUI project for experimenting with isolated tab-based tools.

## Run

```powershell
.venv\Scripts\Activate.ps1
python main.py
```

## Splunk Connection

```powershell
$env:SPLUNK_HOST="https://your-splunk-host:8089"
$env:SPLUNK_USERNAME="your-username"
$env:SPLUNK_PASSWORD="your-password"
python main.py
```

You can also save these values from the app's `Settings` popup. They are stored locally in `splunk_settings.json`.
