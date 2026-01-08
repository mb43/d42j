# Complete Installation Guide for Windows 11 Pro

This guide assumes you're starting from scratch with nothing installed.

## 📋 Prerequisites Checklist

Before you begin, make sure you have:
- [ ] Windows 11 Pro (or Windows 10)
- [ ] Administrator privileges
- [ ] ZScaler connected (required for Device42/Jira access)
- [ ] Internet connection
- [ ] About 30 minutes

## 🔽 Step 1: Get the Code on Your Machine

You need to download the d42j code repository first. Choose ONE method:

### Method A: Using Git (Recommended)

**1.1 Install Git for Windows**
- Go to: https://git-scm.com/download/win
- Download and run installer
- Accept all defaults
- Verify: Open Command Prompt and type:
  ```cmd
  git --version
  ```

**1.2 Clone the repository**
```cmd
REM Navigate to where you want the code (e.g., Documents)
cd C:\Users\%USERNAME%\Documents

REM Clone the repository
git clone https://github.com/mb43/d42j.git

REM Navigate into the folder
cd d42j

REM You should see all the files now
dir
```

**Benefits:** Easy to get updates later with `git pull`

### Method B: Download ZIP (No Git Required)

**1.1 Download from GitHub**
1. Go to: https://github.com/mb43/d42j
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Save to your Downloads folder

**1.2 Extract the ZIP**
1. Right-click the downloaded ZIP file
2. Choose "Extract All..."
3. Extract to: `C:\Users\%USERNAME%\Documents\d42j`

**1.3 Verify**
Open Command Prompt:
```cmd
cd C:\Users\%USERNAME%\Documents\d42j
dir
```
You should see folders: `backend`, `frontend`, and files like `README.md`

## 💻 Step 2: Install Python 3.9+

**2.1 Download Python**
- Go to: https://www.python.org/downloads/
- Click the big yellow "Download Python 3.x.x" button
- Save the installer

**2.2 Run Python Installer**
- Double-click the installer
- ⚠️ **CRITICAL**: Check ✅ "Add Python to PATH"
- ⚠️ **CRITICAL**: Check ✅ "Install pip"
- Click "Install Now"
- Wait for installation (2-3 minutes)

**2.3 Verify Python Installation**
Open a **NEW** Command Prompt (important - restart it):
```cmd
python --version
```
Should show: `Python 3.9.x` or higher

```cmd
pip --version
```
Should show: `pip 23.x.x` or similar

**Troubleshooting:** If "python is not recognized":
- Close Command Prompt
- Reopen Command Prompt
- Try again
- If still fails: You need to add Python to PATH manually (see WINDOWS_SETUP.md)

## 📦 Step 3: Install Node.js 16+

**3.1 Download Node.js**
- Go to: https://nodejs.org/
- Download the **LTS** version (left button)
- Save the installer

**3.2 Run Node.js Installer**
- Double-click the installer
- Accept all defaults
- Click "Next" through all screens
- Click "Install"
- Wait for installation (2-3 minutes)

**3.3 Verify Node.js Installation**
Open a **NEW** Command Prompt:
```cmd
node --version
```
Should show: `v16.x.x` or higher

```cmd
npm --version
```
Should show: `8.x.x` or higher

## ⚙️ Step 4: Backend Setup

**4.1 Navigate to Backend**
```cmd
cd C:\Users\%USERNAME%\Documents\d42j\backend
```

**4.2 Run Setup Script**
```cmd
setup-windows.bat
```

This script will:
1. Create a Python virtual environment
2. Install all Python dependencies (FastAPI, requests, etc.)
3. Launch the configuration wizard

**4.3 Configuration Wizard**

You'll be asked for:

**Device42 Settings:**
```
Device42 hostname or IP [rhmd42]: rhmd42
Protocol (http/https) [https]: https
Port [443]: 443
Device42 username: your_username
Device42 password: ********
Verify SSL certificates? (yes/no) [yes]: yes
```
(If you get SSL errors later, re-run and choose "no" for SSL)

**Jira Settings:**
```
Jira URL (e.g., https://jira.company.com): https://your-jira.com
Jira username/email: your.email@company.com
Jira API token: ************************
Jira project key for infrastructure [IT]: IT
```

**To get Jira API Token:**
1. Log into Jira
2. Click your profile picture → Account Settings
3. Security → API Tokens → Create API Token
4. Copy the token and paste it here

**Risk Assessment:**
```
Maximum acceptable age (years) [7]: 7
Low risk threshold (years) [3]: 3
Medium risk threshold (years) [5]: 5
High risk threshold (years) [7]: 7
```
(Just press Enter to accept defaults)

**Manufacturer APIs:**
```
Enable DELL API integration? (yes/no) [no]: no
Enable HP API integration? (yes/no) [no]: no
Enable CISCO API integration? (yes/no) [no]: no
```
(Say "no" for now - you can add these later)

**Cache Settings:**
```
Cache TTL (hours) [6]: 6
```

**Server Settings:**
```
Server bind address [0.0.0.0]: 0.0.0.0
Server port [8000]: 8000
GitHub Pages URL:
```
(Leave blank for now)

**4.4 Setup Complete**
You should see:
```
Configuration completed successfully!
Configuration saved to: C:\Users\...\d42j\backend\config.json
```

## 🎨 Step 5: Frontend Setup

The frontend dependencies will be installed automatically when you first run `start-frontend.bat`.

**OR** install them manually:
```cmd
cd C:\Users\%USERNAME%\Documents\d42j\frontend
npm install
```
(This takes 2-5 minutes and downloads ~300MB of dependencies)

## 🚀 Step 6: First Run

**6.1 Ensure ZScaler is Connected**
- Check your system tray for ZScaler
- Make sure it's connected

**6.2 Test Device42/Jira Access**
Open browser and verify you can access:
- https://rhmd42 (Device42)
- https://your-jira.com (Jira)

If these don't work, the app won't work either.

**6.3 Start the Application**

Navigate to the d42j folder:
```cmd
cd C:\Users\%USERNAME%\Documents\d42j
```

Run the startup script:
```cmd
start-all.bat
```

**What happens:**
- Two new Command Prompt windows open
- Window 1: Backend API starts (takes ~10 seconds)
- Window 2: Frontend starts (takes ~30-60 seconds)
- Your browser opens to http://localhost:3000

**6.4 Verify Everything Works**

Backend health check:
- Open browser to: http://localhost:8000/health
- Should show:
  ```json
  {
    "status": "healthy",
    "connections": {
      "device42": true,
      "jira": true
    }
  }
  ```

Frontend dashboard:
- Should open automatically at http://localhost:3000
- You should see:
  - Total Assets count
  - Risk distribution chart
  - Summary cards with numbers
  - Navigation menu on left

**If you see data, you're done! 🎉**

## 📁 Where Everything Lives

After installation, you'll have:

```
C:\Users\YourName\Documents\d42j\
├── backend\
│   ├── venv\                  (Python virtual environment)
│   ├── config.json           (Your configuration - DON'T commit!)
│   ├── .encryption_key       (Encryption key - DON'T commit!)
│   └── main.py               (Backend API)
├── frontend\
│   ├── node_modules\         (Dependencies - large!)
│   └── src\                  (React code)
└── start-all.bat            (Easy startup)
```

## 🔄 Daily Usage

### Starting the App
```cmd
cd C:\Users\%USERNAME%\Documents\d42j
start-all.bat
```

### Stopping the App
- Close the two Command Prompt windows
- Or press `Ctrl+C` in each window

### Updating Data
- Click the Refresh icon in the dashboard (top-right)
- Or restart the backend

### Getting Updates (if using Git)
```cmd
cd C:\Users\%USERNAME%\Documents\d42j
git pull
cd backend
venv\Scripts\activate
pip install -r requirements.txt
cd ..\frontend
npm install
```

## 🆘 Troubleshooting

### "python is not recognized"
- Reinstall Python
- ✅ Check "Add Python to PATH"
- Restart Command Prompt

### "Port 8000 already in use"
```cmd
netstat -ano | findstr :8000
taskkill /PID <number> /F
```

### "Cannot connect to Device42/Jira"
1. Check ZScaler is connected
2. Test in browser: https://rhmd42
3. Re-run configure.py with `verify_ssl: false`:
   ```cmd
   cd backend
   venv\Scripts\activate
   python configure.py
   ```

### Frontend shows "Cannot connect to backend"
1. Check backend window - is it running?
2. Visit http://localhost:8000/health
3. Check for errors in backend window

### ZScaler Certificate Errors
Edit `backend\config.json`:
```json
{
  "device42": {
    "verify_ssl": false
  }
}
```
Restart backend.

## 📊 What You'll Get

Once running, the dashboard shows:
- **Total infrastructure asset count** from Device42
- **Risk distribution** (low/medium/high/critical)
- **Critical risk assets** needing immediate attention
- **Average infrastructure age** (for your 7-year policy case)
- **Expired support count**
- **Jira integration status**
- **Detailed risk assessments** with recommendations
- **Discrepancy reports** (Device42 vs Jira mismatches)

## 🎯 Success Criteria

✅ Backend shows: "Uvicorn running on http://0.0.0.0:8000"
✅ Frontend shows dashboard with asset counts
✅ Can navigate between pages (Assets, Risk, Discrepancies)
✅ Health check shows device42: true and jira: true
✅ No error messages in either window

## 📚 Next Steps

1. ✅ Explore the dashboard
2. ✅ Review Risk Assessment page
3. ✅ Check Discrepancies tab
4. ✅ Filter assets by type/risk
5. ✅ Export reports for management
6. ✅ Make your case for 7-year infrastructure replacement!

## 🔗 Additional Resources

- **WINDOWS_SETUP.md** - Detailed Windows configuration
- **WINDOWS_CHECKLIST.md** - Step-by-step checklist
- **QUICKSTART.md** - Quick reference guide
- **README.md** - Full feature documentation
- **API Docs** - http://localhost:8000/docs (when running)

---

**Estimated Total Time:** 30 minutes
- Software installation: 15 minutes
- Backend setup: 5 minutes
- Frontend setup: 5 minutes
- First run and verification: 5 minutes

You've got this! 🚀
