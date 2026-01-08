# Windows Installation & Setup Checklist

## Pre-Installation Checklist

- [ ] Windows 11 Pro (or Windows 10)
- [ ] ZScaler connected (required for Device42/Jira access)
- [ ] Administrator privileges (for installing software)
- [ ] Internet connection

## Software Installation

### 1. Install Python 3.9+

- [ ] Download from https://www.python.org/downloads/
- [ ] Run installer
- [ ] ✅ **CRITICAL**: Check "Add Python to PATH"
- [ ] ✅ **CRITICAL**: Check "Install pip"
- [ ] Click "Install Now"
- [ ] Verify installation:
  ```cmd
  python --version
  pip --version
  ```

### 2. Install Node.js 16+

- [ ] Download LTS version from https://nodejs.org/
- [ ] Run installer (accept all defaults)
- [ ] Verify installation:
  ```cmd
  node --version
  npm --version
  ```

### 3. Install Git (Optional)

- [ ] Download from https://git-scm.com/download/win
- [ ] Run installer (accept all defaults)
- [ ] Verify installation:
  ```cmd
  git --version
  ```

## First-Time Setup

### Backend Setup

- [ ] Open Command Prompt or PowerShell
- [ ] Navigate to project:
  ```cmd
  cd path\to\d42j\backend
  ```
- [ ] Run setup script:
  ```cmd
  setup-windows.bat
  ```
  This will:
  - Create Python virtual environment
  - Install all dependencies
  - Run configuration wizard

### Configuration Wizard

Have this information ready:

**Device42:**
- [ ] Hostname: `rhmd42` (or your Device42 hostname)
- [ ] Username: Your super user account
- [ ] Password: Your password
- [ ] Protocol: `https` (press Enter for default)
- [ ] Port: `443` (press Enter for default)
- [ ] Verify SSL: `yes` or `no` (try `yes` first, use `no` if ZScaler certificate issues)

**Jira:**
- [ ] URL: Full Jira URL (e.g., `https://jira.yourcompany.com`)
- [ ] Username: Your Jira email/username
- [ ] API Token: Generate from Jira profile settings
  - Go to Jira → Profile → Personal Access Tokens
  - Create new token, copy it
- [ ] Project Key: `IT` (or your project key for infrastructure tickets)

**Risk Assessment:**
- [ ] Max age: `7` years (or press Enter for default)
- [ ] Low threshold: `3` years (or press Enter)
- [ ] Medium threshold: `5` years (or press Enter)
- [ ] High threshold: `7` years (or press Enter)

**Manufacturer APIs (Optional - can skip for now):**
- [ ] Dell: `no` (or provide API key)
- [ ] HP: `no` (or provide API key)
- [ ] Cisco: `no` (or provide API key)
- [ ] Juniper: `no` (or provide API key)
- [ ] NetApp: `no` (or provide API key)
- [ ] VMware: `no` (or provide API key)

### Frontend Setup

- [ ] Open NEW Command Prompt window
- [ ] Navigate to frontend:
  ```cmd
  cd path\to\d42j\frontend
  ```
- [ ] Install dependencies:
  ```cmd
  npm install
  ```
  (This takes 2-5 minutes)

## First Run

### Easy Method (Recommended)

- [ ] Double-click `start-all.bat` in the d42j folder
- [ ] Two windows will open (backend and frontend)
- [ ] Wait for "Webpack compiled successfully" message
- [ ] Browser should auto-open to http://localhost:3000

### Manual Method

**Terminal 1 - Backend:**
```cmd
cd path\to\d42j\backend
venv\Scripts\activate
python main.py
```
- [ ] Wait for "Uvicorn running on http://0.0.0.0:8000"

**Terminal 2 - Frontend:**
```cmd
cd path\to\d42j\frontend
npm start
```
- [ ] Wait for browser to open

## Verification

- [ ] Backend API responding: http://localhost:8000/health
  - Should show: `{"status":"healthy","connections":{"device42":true,"jira":true}}`
- [ ] Frontend loads: http://localhost:3000
- [ ] Dashboard shows data (total assets count)
- [ ] Can navigate to "All Assets" page
- [ ] Can view "Risk Assessment" page

## Troubleshooting

### Python not found
- [ ] Reinstall Python with "Add to PATH" checked
- [ ] Or add manually via Environment Variables

### Port 8000 already in use
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Port 3000 already in use
```cmd
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Cannot connect to Device42/Jira
- [ ] Verify ZScaler is connected
- [ ] Test Device42 access in browser: `https://rhmd42`
- [ ] Test Jira access in browser
- [ ] Check credentials in `backend\config.json`
- [ ] Try `verify_ssl: false` in config if certificate errors

### ZScaler certificate issues
- [ ] Set `verify_ssl: false` in `backend/config.json`:
  ```json
  {
    "device42": {
      "verify_ssl": false
    }
  }
  ```
- [ ] Restart backend

### Frontend shows "Cannot connect to backend"
- [ ] Verify backend is running (check Terminal 1)
- [ ] Visit http://localhost:8000/health in browser
- [ ] Check CORS settings in `backend/config.json`
- [ ] Check `frontend/src/config.js` has correct API_BASE_URL

## Daily Usage

### Starting the Application

**Option 1 - Easy Start:**
- [ ] Double-click `start-all.bat`

**Option 2 - Manual Start:**
- [ ] Double-click `backend\start-backend.bat`
- [ ] Double-click `frontend\start-frontend.bat`

### Stopping the Application

- [ ] Close the Command Prompt windows
- [ ] Or press `Ctrl+C` in each window

### Refreshing Data

- [ ] In dashboard, click Refresh icon (top-right)
- [ ] Or visit: http://localhost:8000/docs
- [ ] Click "POST /api/refresh" → Try it out → Execute

## Network Access (Optional)

If you want others to access the dashboard from their machines:

### 1. Find Your IP Address
```cmd
ipconfig
```
- [ ] Note your IPv4 Address (e.g., `192.168.1.100`)

### 2. Configure Firewall
```cmd
netsh advfirewall firewall add rule name="d42j API" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="d42j Frontend" dir=in action=allow protocol=TCP localport=3000
```

### 3. Update Frontend Config
- [ ] Edit `frontend/src/config.js`
- [ ] Change `API_BASE_URL` to `http://YOUR-IP:8000`
- [ ] Restart frontend

### 4. Update Backend CORS
- [ ] Edit `backend/config.json`
- [ ] Add to `server.cors_origins`: `"http://YOUR-IP:3000"`
- [ ] Restart backend

Now others can access: `http://YOUR-IP:3000`

## Production Deployment (Optional)

For always-on access:

- [ ] See `WINDOWS_SETUP.md` for Windows Service setup
- [ ] Or use Task Scheduler to auto-start on login
- [ ] Consider static IP for your Windows machine

## Getting Help

If stuck:
1. Check error messages in Command Prompt windows
2. Review `WINDOWS_SETUP.md` for detailed troubleshooting
3. Verify ZScaler connection
4. Test Device42/Jira in browser first
5. Check backend logs for specific errors

## Success!

✅ You're ready when:
- Backend shows "Uvicorn running"
- Frontend shows dashboard with asset data
- Can navigate between pages
- Risk assessments display
- No error messages in either window

Happy infrastructure assessment! 🎯
