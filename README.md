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

## Oracle Connection

Oracle support in the second tab uses the official `python-oracledb` driver.

Official docs:
- [Installation](https://python-oracledb.readthedocs.io/en/v3.4.0/user_guide/installation.html)
- [Connection handling](https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html)

Install the driver with:

```powershell
python -m pip install oracledb --upgrade
```

Older Oracle servers may require Oracle Instant Client and Thick mode. This project looks for a local Instant Client under `vendor/oracle/`.
