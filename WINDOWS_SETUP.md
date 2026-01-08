# d42j Setup Guide for Windows 11 Pro

## Why Windows?

If ZScaler (or any VPN/security gateway) is required to access your Device42 and Jira instances, the backend API **must** run on a machine with ZScaler installed. Since that's your Windows 11 Pro machine, that's where the backend will run.

## Quick Start for Windows

### Prerequisites

1. **Python 3.9 or higher**
   - Download from: https://www.python.org/downloads/
   - ✅ **IMPORTANT**: During installation, check "Add Python to PATH"
   - Verify: Open Command Prompt and run `python --version`

2. **Node.js 16 or higher**
   - Download from: https://nodejs.org/ (LTS version)
   - Verify: Open Command Prompt and run `node --version`

3. **Git for Windows** (optional, if you cloned the repo)
   - Download from: https://git-scm.com/download/win

### Installation Steps

#### Backend Setup (5 minutes)

1. **Open Command Prompt** (or PowerShell)
   ```cmd
   cd path\to\d42j\backend
   ```

2. **Create virtual environment**
   ```cmd
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```cmd
   venv\Scripts\activate
   ```

   You should see `(venv)` appear in your prompt.

4. **Install dependencies**
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure the application**
   ```cmd
   python configure.py
   ```

   Enter your details:
   - Device42 host: `rhmd42` (or full URL)
   - Your super user credentials
   - Jira URL (full https:// URL)
   - Jira API token
   - Risk thresholds (press Enter for defaults)

6. **Test the backend**
   ```cmd
   python main.py
   ```

   You should see:
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

   Visit http://localhost:8000/docs to see the API documentation.

#### Frontend Setup (5 minutes)

1. **Open a NEW Command Prompt window**
   ```cmd
   cd path\to\d42j\frontend
   ```

2. **Install dependencies**
   ```cmd
   npm install
   ```

3. **Start development server**
   ```cmd
   npm start
   ```

   Your browser should automatically open to http://localhost:3000

### Running the Application

You'll need **two Command Prompt windows** open:

**Window 1 - Backend:**
```cmd
cd path\to\d42j\backend
venv\Scripts\activate
python main.py
```

**Window 2 - Frontend:**
```cmd
cd path\to\d42j\frontend
npm start
```

## Easy Startup Scripts

I've created batch files to make this easier (see below).

## Deployment Options for Windows

### Option 1: Local Only (Development/Testing)

**Setup:** Both backend and frontend run on localhost
**Access:** Only from your Windows machine
**Use case:** Testing, personal use, development

**Pros:**
- Simple setup
- No firewall config needed
- Secure (nothing exposed)

**Cons:**
- Only you can access it
- Must keep both terminals open

### Option 2: Expose Backend to Network

**Setup:** Backend exposed on network, frontend on GitHub Pages or local
**Access:** Dashboard accessible from other machines on your network
**Use case:** Team access, shared reporting

**Steps:**
1. Configure Windows Firewall to allow port 8000:
   ```cmd
   netsh advfirewall firewall add rule name="d42j API" dir=in action=allow protocol=TCP localport=8000
   ```

2. Find your Windows machine's IP:
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

3. Update frontend config:
   - Edit `frontend/src/config.js`
   - Change `API_BASE_URL` to `http://192.168.1.100:8000`

4. Update backend CORS:
   - Edit `backend/config.json`
   - Add your machine's IP to `server.cors_origins`

**Pros:**
- Team can access dashboard
- Centralized reporting

**Cons:**
- Windows machine must stay on
- IP address might change (consider static IP)

### Option 3: Production-like Setup on Windows

**Setup:** Both backend and frontend served from Windows
**Access:** Single URL for everything
**Use case:** Small team, internal use

**Steps:**
1. Build frontend:
   ```cmd
   cd frontend
   npm run build
   ```

2. Install a simple web server:
   ```cmd
   npm install -g http-server
   ```

3. Serve frontend:
   ```cmd
   cd frontend\build
   http-server -p 3000
   ```

4. Access at http://localhost:3000 or http://your-ip:3000

## Troubleshooting Windows-Specific Issues

### Python not found
- Reinstall Python and check "Add Python to PATH"
- Or manually add to PATH:
  1. Search for "Environment Variables" in Start Menu
  2. Edit System Environment Variables
  3. Add Python install directory to PATH

### Port already in use
```cmd
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### ZScaler certificate issues
If you get SSL errors when connecting to Device42/Jira:

1. In `backend/config.json`, set:
   ```json
   {
     "device42": {
       "verify_ssl": false
     }
   }
   ```

2. Or add ZScaler certificate to Python:
   ```cmd
   pip install python-certifi-win32
   ```

### Firewall blocking access
If you can't access from other machines:

1. **Check Windows Firewall:**
   - Control Panel → Windows Defender Firewall
   - Allow an app → Add Python and Node

2. **Or temporarily disable** (testing only):
   ```cmd
   netsh advfirewall set allprofiles state off
   ```

   Remember to turn back on:
   ```cmd
   netsh advfirewall set allprofiles state on
   ```

## Running as Windows Service (Advanced)

To run the backend as a Windows service (starts automatically):

1. Install NSSM (Non-Sucking Service Manager):
   - Download from: https://nssm.cc/download

2. Install service:
   ```cmd
   nssm install d42j-api "C:\path\to\d42j\backend\venv\Scripts\python.exe" "C:\path\to\d42j\backend\main.py"
   ```

3. Start service:
   ```cmd
   nssm start d42j-api
   ```

## Performance Tips

1. **Exclude from Windows Defender:**
   - Add `d42j` folder to exclusions for faster performance
   - Settings → Windows Security → Virus & threat protection → Exclusions

2. **Prevent sleep:**
   - Settings → System → Power & sleep
   - Set "When plugged in, PC goes to sleep after" to "Never"

3. **Static IP:**
   - If serving to network, set static IP in network adapter settings
   - Prevents IP changes on restart

## Next Steps

1. ✅ Install Python and Node.js
2. ✅ Run setup scripts (see batch files below)
3. ✅ Configure Device42 and Jira credentials
4. ✅ Test locally at http://localhost:3000
5. ⚠️ Decide on deployment option (local only vs network access)
6. 📊 Start analyzing your infrastructure!

## Getting Help

If you encounter issues:
1. Check error messages in Command Prompt
2. Verify ZScaler is connected
3. Test Device42/Jira access in browser first
4. Check logs: Backend window shows detailed error messages
