# 🚀 KGAS UI Quick Start Instructions

## The UI is working! Here's how to access it:

### Option 1: Use the automatic start script
```bash
python ui/start_simple_ui.py
```

### Option 2: Manual start (if Option 1 doesn't work)
```bash
cd ui
python3 -m http.server 8899
```

## Then open your browser and go to:

1. **http://localhost:8899/simple_working_ui.html** (Full UI)
2. **http://localhost:8899/minimal_test.html** (Test page)

## If you see a blank/spinning page:

### Check 1: Server is actually running
- Look for "Serving HTTP on 0.0.0.0 port 8899" message
- If not, try a different port: `python3 -m http.server 8888`

### Check 2: Correct URL
- Make sure you're using the EXACT URL above
- Don't forget the `.html` at the end

### Check 3: Browser cache
- Try Ctrl+F5 (force refresh)
- Or open in incognito/private mode

### Check 4: JavaScript enabled
- Make sure JavaScript is enabled in your browser
- Check browser console (F12) for any errors

### Check 5: Try the minimal test first
- Go to **http://localhost:8899/minimal_test.html**
- If this works, the server is fine
- Then try the full UI

## What you should see:

When working correctly, you'll see:
- Purple gradient header with "🔬 KGAS Research UI"
- 5 tabs: Documents, Analysis, Graph, Query, Export
- Clicking tabs switches content
- Upload areas, buttons, and forms

## Troubleshooting:

If it's still not working:
1. Check the terminal for error messages
2. Try different browsers (Chrome, Firefox, Safari)
3. Make sure you're in the correct directory
4. Kill any other processes using the port: `lsof -ti :8899 | xargs kill -9`

## Debug Information:

The debug tool confirmed:
- ✅ Server starts successfully on port 8899
- ✅ HTML files are accessible (16KB+ size)
- ✅ No syntax errors in HTML/JavaScript
- ✅ All required files present

So the issue is likely browser-related or URL-related, not server-related.