# Security & Credentials

## ✅ Safe to Push to GitHub

This codebase is designed to be **completely safe** to push to public repositories. Here's why:

### No Hardcoded Credentials
- ❌ No API tokens in code
- ❌ No passwords in code
- ❌ No secret keys hardcoded
- ✅ All sensitive data stored in sessions (runtime only)
- ✅ Environment variables for production secrets

### Session Storage Only
User credentials are stored in Flask sessions:
- **Access Token**: Stored in `session['access_token']` (server-side, encrypted)
- **Property ID**: Stored in `session['property_id']` (server-side, encrypted)
- Sessions expire after 7 days of inactivity
- Session data is **never** committed to git

### .gitignore Protection
The following sensitive files are automatically ignored:
```
.env                    # Environment variables with secrets
flask_session/          # Flask session files
*.db                    # Any database files
*.sqlite*               # SQLite databases
.cloudbeds_*.json       # Old config files (if any exist)
```

### What Gets Committed
Only these safe files are tracked by git:
- ✅ `.env.example` - Template only, no real values
- ✅ `main.py` - Application code (no secrets)
- ✅ `templates/` - HTML templates
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Deployment config
- ✅ `Dockerfile` - Container config
- ✅ Documentation files (README, DEPLOY, etc.)

## Production Security Checklist

When deploying to production:

1. **Set SECRET_KEY environment variable**
   ```bash
   # Generate a random secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Then set it in your hosting platform's environment variables.

2. **Set FLASK_ENV=production**
   This disables debug mode and other development features.

3. **Use HTTPS**
   All major hosting platforms (Render, Railway, Heroku) provide free HTTPS.

4. **Keep credentials in environment**
   Never hardcode API tokens - always use environment variables or session storage.

## How Credentials Are Handled

### Development (Local)
1. User enters credentials in browser
2. Credentials stored in encrypted session cookie
3. Session persists for 7 days or until cleared
4. Session data stays in memory/temp files (never committed)

### Production (Hosted)
Same as development:
1. Each user enters their own credentials
2. Stored in their browser session
3. Never saved to database or files
4. Never logged or exposed

## Verifying Before Push

To double-check nothing sensitive is being committed:

```bash
# See what files would be added
git status

# See the actual changes
git diff

# Search for potential secrets (should return nothing)
grep -r "sk-" .
grep -r "password.*=" .
grep -r "token.*=" .
```

## If You Accidentally Commit Secrets

If you accidentally commit credentials:

1. **Immediately revoke** the exposed credentials in Cloudbeds
2. **Remove from git history**:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if already pushed):
   ```bash
   git push origin --force --all
   ```
4. **Generate new credentials** in Cloudbeds

## Questions?

If you're unsure about any file, check:
- Is it in `.gitignore`? If yes, it won't be committed
- Does it contain actual secrets? If yes, add it to `.gitignore`
- Is it a template/example? Make sure it has placeholder values only

**When in doubt, don't push!** Ask for a review first.
