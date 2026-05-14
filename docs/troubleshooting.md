# Troubleshooting

## "ModuleNotFoundError: No module named 'server'"

You're running `uvicorn` from inside the `server/` folder. Run it from the project root:

```bash
cd ~/path/to/Whendo  # NOT cd server/
make dev
```

## "externally-managed-environment" on pip install

You forgot to activate the virtual env. Run:

```bash
source .venv/bin/activate
# You should now see (.venv) in your prompt
which python  # should point to .venv/bin/python
```

## Web shows "Could not reach backend"

The frontend can't talk to the backend. Make sure Terminal 1 is still running and check:

```bash
curl http://localhost:8000/health
```

If that fails, the backend crashed — look at the logs in Terminal 1.

## Port 8000 or 3000 already in use

Something else is using that port. Kill it:

```bash
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:3000)
```

## "make: command not found"

Install `make`:

- Debian/Ubuntu: `sudo apt install make`
- macOS: `brew install make`
- Fedora: `sudo dnf install make`

## A recipe shows "failed" in the runs tab

Click the row to expand it — the `error` field has the full error message. Common causes:

- A secret (API key, token) is not configured. Visit `/settings` to set it.
- The external service rejected the request (wrong credentials, rate limit). Check the error text.
- The recipe YAML has a typo. Check `/api/recipes/errors` in the API or the server logs.

## Secrets in `/settings` are greyed out

You set a master password, so secrets are encrypted at rest. After every server restart you need to unlock them — open `/settings`, type your master password and click **Unlock**.

If you forgot the master password, the only way out is to delete `data/whendo.db` (you'll lose all settings and run history) and start over. There is no recovery — that's the whole point of encryption.
