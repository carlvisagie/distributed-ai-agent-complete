# Ubuntu Server Installation Guide (Lenovo)

## 🎯 Purpose

This guide provides step-by-step instructions for installing Ubuntu Server 24.04 LTS on the Lenovo machine, with specific fixes for common login issues.

---

## ⚠️ Common Issue: Cannot Login After Installation

**Problem:** After installing Ubuntu Server, you cannot log in with the username and password you created during installation. The system keeps rejecting your credentials or loops back to the login prompt.

**Root Causes:**
1. **Keyboard layout mismatch** during installation
2. **UEFI/Secure Boot conflicts**
3. **Installation corruption**
4. **Password not set correctly**

**Solution:** Follow this guide carefully with specific BIOS settings and installation steps.

---

## 📋 Prerequisites

### What You Need
- ✅ USB stick (8GB minimum)
- ✅ Another computer (HP OMEN or Predator Helios)
- ✅ Ethernet cable for Lenovo
- ✅ 2-3 hours of time
- ✅ Patience!

### Downloads
1. **Ubuntu Server 24.04 LTS ISO**
   - URL: https://ubuntu.com/download/server
   - File: `ubuntu-24.04.1-live-server-amd64.iso`
   - Size: ~2.5GB

2. **Rufus** (Windows) or **balenaEtcher** (Any OS)
   - Rufus: https://rufus.ie/
   - Etcher: https://etcher.balena.io/

---

## 🔧 Phase 1: BIOS Configuration (CRITICAL!)

### Step 1: Enter BIOS
1. Turn on Lenovo
2. Immediately press **F2** (or Del/F1 depending on model)
3. Keep pressing until BIOS menu appears

### Step 2: Critical BIOS Settings

#### A) Disable Secure Boot
```
Security → Secure Boot → Disabled
```
**Why:** Secure Boot can cause login issues with Ubuntu

#### B) Enable Virtualization
```
Advanced → CPU Configuration → Intel Virtualization Technology → Enabled
Advanced → CPU Configuration → VT-d → Enabled
```
**Why:** Required for Docker and virtualization

#### C) Set Boot Mode
```
Boot → Boot Mode → UEFI (not Legacy)
```
**Why:** Modern Ubuntu requires UEFI

#### D) Disable Fast Boot
```
Boot → Fast Boot → Disabled
```
**Why:** Can cause installation issues

### Step 3: Save and Exit
1. Press **F10** to save
2. Confirm "Yes"
3. System will reboot

---

## 💾 Phase 2: Create Bootable USB

### On Windows (Using Rufus)

1. **Insert USB stick**
   - Backup any files (will be erased!)

2. **Open Rufus**
   - Download from https://rufus.ie/
   - No installation needed

3. **Configure Rufus:**
   ```
   Device: [Your USB stick]
   Boot selection: [Click SELECT and choose Ubuntu ISO]
   Partition scheme: GPT
   Target system: UEFI (non CSM)
   File system: FAT32
   ```

4. **Start**
   - Click "START"
   - If prompted about ISO mode: Choose "Write in ISO Image mode"
   - Wait 5-10 minutes

5. **Done**
   - Rufus will show "READY" when complete
   - Close Rufus
   - **DO NOT remove USB yet**

### On Mac/Linux (Using Etcher)

1. **Install Etcher**
   ```bash
   # Download from https://etcher.balena.io/
   ```

2. **Run Etcher**
   - Select Ubuntu ISO
   - Select USB drive
   - Click "Flash!"
   - Wait 5-10 minutes

---

## 🖥️ Phase 3: Ubuntu Installation

### Step 1: Boot from USB

1. **Insert USB into Lenovo**
2. **Restart Lenovo**
3. **Press F12** immediately (Boot Menu)
4. **Select USB drive** from list
5. Wait for Ubuntu installer to load

### Step 2: Language & Keyboard

**CRITICAL: Keyboard Layout**
```
Language: English
Keyboard layout: English (US)
Keyboard variant: English (US)
```

**Test your keyboard:**
- Type your password in the test field
- Make sure special characters work correctly
- **This is where many login issues start!**

### Step 3: Network Configuration

```
Network connections: Use DHCP (automatic)
```
- Plug in Ethernet cable
- Wait for IP address to appear
- **Do not configure WiFi** (can be done later)

### Step 4: Proxy & Mirror

```
Proxy: [Leave blank]
Mirror: [Use default]
```

### Step 5: Storage Configuration

**CRITICAL: This will erase everything on the Lenovo!**

```
Storage configuration: Use entire disk
  ✅ Set up this disk as an LVM group
  ✅ Encrypt the LVM group (optional but recommended)
```

**Review summary:**
- Should show entire disk will be used
- Confirm and continue

### Step 6: Profile Setup

**CRITICAL: This is where you create your login!**

```
Your name: Carl Visagie
Your server's name: lenovo-server
Pick a username: carl
Choose a password: [STRONG PASSWORD]
Confirm your password: [SAME PASSWORD]
```

**Password Tips:**
- Use at least 12 characters
- Mix uppercase, lowercase, numbers, symbols
- **WRITE IT DOWN!**
- Test typing it in the password field
- Make sure you can type it correctly!

### Step 7: SSH Setup

```
✅ Install OpenSSH server
```
**IMPORTANT:** Check this box!

```
Import SSH identity: No
```

### Step 8: Featured Server Snaps

```
Skip all (we'll install Docker manually)
```

### Step 9: Installation

- Wait 15-20 minutes
- Do not interrupt!
- When complete, select "Reboot Now"
- **Remove USB stick when prompted**

---

## 🔐 Phase 4: First Login

### Step 1: Wait for Boot

After reboot:
1. Wait for login prompt
2. Should show: `lenovo-server login:`

### Step 2: Login

```
login: carl
Password: [your password]
```

**If login fails:**
1. Try typing password very slowly
2. Check Caps Lock is OFF
3. Try username in lowercase only
4. If still fails, see Troubleshooting section below

### Step 3: Verify Login Success

```bash
# You should see:
carl@lenovo-server:~$

# Test sudo access:
sudo whoami
# Should output: root
```

**Success!** You're logged in! 🎉

---

## 🚀 Phase 5: Post-Installation Setup

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Git

```bash
sudo apt install -y git
```

### Step 3: Clone Repository

```bash
git clone https://github.com/carlvisagie/distributed-ai-agent-complete.git
cd distributed-ai-agent-complete
```

### Step 4: Run Setup Script

```bash
cd lenovo/scripts
chmod +x ubuntu_server_setup.sh
sudo ./ubuntu_server_setup.sh
```

**This script will:**
- ✅ Install Docker & Docker Compose
- ✅ Configure SSH (key-only authentication)
- ✅ Set up firewall (UFW)
- ✅ Install fail2ban
- ✅ Configure automatic updates
- ✅ Optimize for server use

### Step 5: Reboot

```bash
sudo reboot
```

---

## 🐛 Troubleshooting

### Problem: Still Can't Login After Installation

**Solution 1: Reset Password from Recovery Mode**

1. **Reboot Lenovo**
2. **Hold Shift** during boot to show GRUB menu
3. **Select:** Advanced options for Ubuntu
4. **Select:** Recovery mode
5. **Select:** root (Drop to root shell prompt)
6. **Remount filesystem:**
   ```bash
   mount -o remount,rw /
   ```
7. **Reset password:**
   ```bash
   passwd carl
   # Enter new password twice
   ```
8. **Reboot:**
   ```bash
   reboot
   ```

**Solution 2: Reinstall with Different Settings**

1. **In BIOS:** Try disabling Secure Boot if not already disabled
2. **During installation:** 
   - Choose "English (US)" keyboard explicitly
   - Test password typing multiple times
   - Use simpler password for first login (change it later)

**Solution 3: Use Live USB to Check Installation**

1. Boot from USB again
2. Choose "Try Ubuntu" instead of "Install"
3. Open terminal
4. Mount installed system:
   ```bash
   sudo mount /dev/sda2 /mnt  # Adjust device name
   sudo chroot /mnt
   passwd carl  # Reset password
   exit
   sudo reboot
   ```

### Problem: Keyboard Types Wrong Characters

**Solution:**
1. During installation, carefully select keyboard layout
2. Test in the test field before continuing
3. Common issue: UK keyboard selected instead of US

### Problem: "Authentication failure" Even with Correct Password

**Solution:**
1. Check Caps Lock is off
2. Try typing username in all lowercase
3. Wait 2-3 seconds between login attempts
4. Use recovery mode to reset password (see above)

### Problem: System Boots to Black Screen

**Solution:**
1. Press Ctrl+Alt+F2 to switch to text console
2. Login there
3. Check display driver:
   ```bash
   sudo ubuntu-drivers autoinstall
   sudo reboot
   ```

---

## ✅ Success Checklist

After successful installation and setup:

- [ ] Can login with username and password
- [ ] `sudo` works without errors
- [ ] System is updated (`sudo apt update`)
- [ ] Git is installed (`git --version`)
- [ ] Repository is cloned
- [ ] Setup script ran successfully
- [ ] Docker is installed (`docker --version`)
- [ ] Can SSH from another machine
- [ ] Firewall is active (`sudo ufw status`)

---

## 📞 Next Steps

Once Ubuntu is installed and working:

1. **Deploy AI Agent System**
   - See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

2. **Configure Network**
   - Set static IP (optional)
   - Configure port forwarding

3. **Test System**
   - Deploy in mock mode
   - Verify all services start

4. **Enable Real AI**
   - Get Anthropic API key
   - Enable OpenHands mode

---

## 💡 Tips for Success

1. **Take your time** - Don't rush the installation
2. **Test keyboard** - Make sure you can type your password correctly
3. **Write down password** - Keep it safe!
4. **Use Ethernet** - WiFi can be configured later
5. **Disable Secure Boot** - Prevents many issues
6. **Keep USB stick** - Useful for recovery

---

## 🎉 You Did It!

Once you can login successfully, the hard part is over!

The rest of the setup is automated with scripts.

**Welcome to your new Ubuntu Server!** 🚀

---

**Need Help?**
- Check the troubleshooting section above
- Review BIOS settings
- Try recovery mode password reset
- Reinstall if necessary (it gets easier each time!)
