#!/bin/bash
# Safety check before pushing to git

echo "======================================"
echo "Git Safety Check"
echo "======================================"
echo ""

# Check for common credential patterns
echo "Checking for potential secrets..."
if grep -r "sk-" . --exclude-dir=.git --exclude="*.sh" 2>/dev/null; then
    echo "❌ FOUND: Potential API keys (sk-)"
    exit 1
fi

if grep -r "Bearer [A-Za-z0-9]" . --exclude-dir=.git --exclude="*.sh" 2>/dev/null | grep -v "Bearer {credentials"; then
    echo "❌ FOUND: Potential hardcoded tokens"
    exit 1
fi

if grep -r '"password":\s*"[^{]' . --exclude-dir=.git --exclude="*.sh" 2>/dev/null; then
    echo "❌ FOUND: Potential hardcoded passwords"
    exit 1
fi

echo "✅ No obvious secrets found"
echo ""

# Check .gitignore exists
echo "Checking .gitignore..."
if [ -f .gitignore ]; then
    echo "✅ .gitignore exists"
else
    echo "❌ .gitignore missing!"
    exit 1
fi

# Check sensitive files are ignored
echo ""
echo "Checking sensitive files are in .gitignore..."
for file in ".env" "flask_session/" "*.db"; do
    if grep -q "$file" .gitignore; then
        echo "✅ $file is ignored"
    else
        echo "❌ $file NOT in .gitignore!"
        exit 1
    fi
done

echo ""
echo "Checking what will be committed..."
git status

echo ""
echo "======================================"
echo "✅ SAFE TO PUSH!"
echo "======================================"
echo ""
echo "To commit and push:"
echo "  git add ."
echo "  git commit -m 'Initial commit'"
echo "  git push origin main"
