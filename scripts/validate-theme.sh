#!/bin/bash
# Local validation test script
# Run this before pushing to test the same validations that CI will run

echo "🧪 Running Local Theme Validation Tests"
echo "======================================="

# Change to theme directory if not already there
cd "$(dirname "$0")"

echo ""
echo "1. 🔍 Theme Check (Shopify Liquid validation)"
echo "----------------------------------------------"
if command -v shopify >/dev/null 2>&1; then
    shopify theme check --fail-level=error || {
        echo "❌ Theme check failed with errors"
        exit 1
    }
    echo "✅ Theme check passed"
else
    echo "⚠️ Shopify CLI not installed, skipping theme check"
fi

echo ""
echo "2. 📄 Settings Schema Validation"
echo "-------------------------------"
if [ -f "config/settings_schema.json" ]; then
    if python3 -c "import json; json.load(open('config/settings_schema.json'))" 2>/dev/null; then
        echo "✅ Settings schema JSON is valid"
    else
        echo "❌ Settings schema has JSON syntax errors"
        exit 1
    fi
else
    echo "⚠️ No settings schema found"
fi

echo ""
echo "3. 🌐 Locale Files Validation"
echo "----------------------------"
if [ -d "locales" ]; then
    failed_files=()
    valid_count=0
    skipped_count=0
    
    for locale_file in locales/*.json; do
        if [ -f "$locale_file" ]; then
            # Skip files that start with comments
            if head -1 "$locale_file" | grep -q "^/\*\|^//"; then
                echo "⚠️ $(basename "$locale_file") contains comments, skipping validation"
                skipped_count=$((skipped_count + 1))
                continue
            fi
            
            if python3 -c "import json; json.load(open('$locale_file'))" 2>/dev/null; then
                valid_count=$((valid_count + 1))
            else
                echo "❌ $(basename "$locale_file") invalid JSON"
                failed_files+=("$(basename "$locale_file")")
            fi
        fi
    done
    
    echo "✅ $valid_count locale files validated successfully"
    echo "⚠️ $skipped_count files skipped (contain comments)"
    
    if [ ${#failed_files[@]} -gt 0 ]; then
        echo "❌ Failed locale files: ${failed_files[*]}"
        exit 1
    fi
else
    echo "⚠️ No locales directory found"
fi

echo ""
echo "🎉 All validation tests passed!"
echo "Your theme is ready to push to CI/CD pipeline."