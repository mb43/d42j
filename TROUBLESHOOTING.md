# Troubleshooting Guide - Windows with ZScaler/Corporate Proxy

## Common Issues and Solutions

### Issue 1: "unable to get issuer cert" - npm install fails

**Symptom:**
```
npm ERR! unable to get issuer certificate
npm ERR! certificate has expired
```

**Cause:** ZScaler intercepts HTTPS connections and npm can't verify the certificate.

**Solution A - Quick Fix (Recommended for Internal Use):**
```cmd
npm config set strict-ssl false
```

Then retry:
```cmd
cd frontend
npm install
```

**Solution B - Use ZScaler Certificate:**

1. Export ZScaler certificate from browser:
   - Open Chrome/Edge
   - Visit any HTTPS site
   - Click padlock → Connection details → Certificate
   - Export/Copy to file as `zscaler.crt`

2. Configure npm:
   ```cmd
   npm config set cafile "C:\path\to\zscaler.crt"
   ```

**Solution C - Use the Helper Script:**
```cmd
fix-zscaler.bat
```
Choose option 1 for quick fix.

---

### Issue 2: "SSL: CERTIFICATE_VERIFY_FAILED" - pip install fails

**Symptom:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Cause:** ZScaler intercepts HTTPS and Python can't verify PyPI's certificate.

**Solution A - Configure pip to trust PyPI:**
```cmd
pip config set global.trusted-host "pypi.org pypi.python.org files.pythonhosted.org"
```

**Solution B - Install packages without SSL verification:**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Solution C - Use the Helper Script:**
```cmd
fix-zscaler.bat
```

---

### Issue 3: Backend can't connect to Device42/Jira - SSL errors

**Symptom:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
Device42 connection failed
```

**Cause:** ZScaler certificate not trusted by Python's requests library.

**Solution - Disable SSL verification in config:**

Edit `backend/config.json`:
```json
{
  "device42": {
    "verify_ssl": false
  }
}
```

Or re-run configuration:
```cmd
cd backend
venv\Scripts\activate
python configure.py
```
Answer "no" when asked "Verify SSL certificates?"

---

### Issue 4: "Port 8000 already in use"

**Symptom:**
```
ERROR: [Errno 10048] error while attempting to bind on address
```

**Solution - Kill the process:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <number> /F
```

Or change the port in `backend/config.json`:
```json
{
  "server": {
    "port": 8001
  }
}
```

---

### Issue 5: "Python is not recognized"

**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Solution - Add Python to PATH:**

**Option A - Reinstall Python:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ **Check "Add Python to PATH"**
4. Install

**Option B - Add manually:**
1. Find Python location (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3X`)
2. Press Windows key, search "Environment Variables"
3. Edit System Environment Variables → PATH
4. Add Python folder and Scripts folder

**Option C - Use py launcher:**
Replace `python` with `py`:
```cmd
py --version
py -m venv venv
```

---

### Issue 6: "failed to build" errors (pandas, cryptography, etc.)

**Symptom:**
```
Building wheel for pandas (pyproject.toml) ... error
Microsoft Visual C++ 14.0 or greater is required
```

**Cause:** Package requires compilation and you don't have build tools.

**Solution - Already fixed in latest code:**
```cmd
cd d42j
git pull
cd backend
rmdir /s /q venv
setup-windows.bat
```

The latest requirements.txt has Windows-compatible versions that don't need compilation.

**If still failing:**
```cmd
pip install <package> --only-binary <package>
```

Example:
```cmd
pip install pandas --only-binary pandas
```

---

### Issue 7: Frontend shows "Cannot connect to backend API"

**Symptoms:**
- Dashboard loads but shows no data
- Browser console shows connection errors
- "Network Error" messages

**Troubleshooting:**

**1. Check backend is running:**
```cmd
# Should return JSON with health status
curl http://localhost:8000/health
```

**2. Check CORS configuration:**

Edit `backend/config.json`:
```json
{
  "server": {
    "cors_origins": [
      "http://localhost:3000",
      "*"
    ]
  }
}
```
Restart backend after changes.

**3. Check frontend API config:**

Edit `frontend/src/config.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

**4. Check Windows Firewall:**
```cmd
netsh advfirewall firewall add rule name="d42j API" dir=in action=allow protocol=TCP localport=8000
```

---

### Issue 8: ZScaler blocks Device42/Jira connections

**Symptom:**
Backend health check shows:
```json
{
  "connections": {
    "device42": false,
    "jira": false
  }
}
```

**Troubleshooting:**

**1. Test in browser first:**
- Open browser
- Go to https://rhmd42 (Device42)
- Go to your Jira URL
- If these don't load, ZScaler is blocking them

**2. Check ZScaler is connected:**
- Look for ZScaler icon in system tray
- Ensure it's connected (not paused)

**3. Disable SSL verification:**

Edit `backend/config.json`:
```json
{
  "device42": {
    "host": "rhmd42",
    "verify_ssl": false
  }
}
```

---

### Issue 9: "venv\Scripts\activate" doesn't work

**Symptom:**
```
'venv\Scripts\activate' is not recognized
venv folder doesn't exist
```

**Solution:**

**1. Check if venv exists:**
```cmd
dir backend\venv
```

**2. If missing, create it:**
```cmd
cd backend
python -m venv venv
```

**3. If Python venv module missing:**
```cmd
pip install virtualenv
virtualenv venv
```

**4. If using PowerShell instead of Command Prompt:**
```powershell
venv\Scripts\Activate.ps1
```

If you get "execution policy" error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue 10: npm install is very slow

**Symptom:**
npm install takes 10+ minutes or hangs

**Solutions:**

**1. Clear npm cache:**
```cmd
npm cache clean --force
npm install
```

**2. Use a faster registry:**
```cmd
npm config set registry https://registry.npmjs.org/
```

**3. Increase timeout:**
```cmd
npm config set fetch-timeout 60000
npm config set fetch-retries 5
```

**4. Exclude from Windows Defender:**
- Settings → Windows Security → Virus & threat protection → Exclusions
- Add `C:\Users\YourName\Documents\d42j\frontend\node_modules`

---

## Getting Help

If none of these solutions work:

1. **Check the error message carefully** - copy the full error
2. **Verify ZScaler is connected** - test browser access first
3. **Check Python and Node.js versions:**
   ```cmd
   python --version  (should be 3.9+)
   node --version    (should be 16+)
   ```
4. **Try the setup in a fresh directory** to rule out corrupted files
5. **Check system requirements:**
   - Windows 11 Pro or Windows 10
   - 4GB RAM minimum
   - 5GB free disk space

## Quick Diagnostic Commands

Run these to diagnose issues:

```cmd
REM Check software versions
python --version
node --version
npm --version
git --version

REM Check if ports are free
netstat -ano | findstr :8000
netstat -ano | findstr :3000

REM Check npm configuration
npm config list

REM Test ZScaler connectivity
ping rhmd42
curl https://rhmd42

REM Check Python packages
cd backend
venv\Scripts\activate
pip list
```

## Emergency Reset

If everything is broken, start fresh:

```cmd
REM 1. Clean up
cd d42j\backend
rmdir /s /q venv

cd ..\frontend
rmdir /s /q node_modules

REM 2. Clear caches
npm cache clean --force
pip cache purge

REM 3. Fix ZScaler
cd ..
fix-zscaler.bat

REM 4. Start over
cd backend
setup-windows.bat

cd ..\frontend
npm install
```
