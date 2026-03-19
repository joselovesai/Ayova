# 📘 AYOVA P2P - Complete User Guide
### Device-based, Trust-First Secure Messaging
#### By Ayogwokhai Josemaria

---

# Table of Contents
1. [Installation](#1-installation)
2. [First Time Setup](#2-first-time-setup)
3. [Sharing Your Identity](#3-sharing-your-identity)
4. [Trusting a Contact](#4-trusting-a-contact)
5. [Sending Messages](#5-sending-messages)
6. [Interactive Chat Mode](#6-interactive-chat-mode)
7. [Local Vault Mode](#7-local-vault-mode)
8. [Troubleshooting](#8-troubleshooting)

---

# 1. Installation

## Step 1: Open Terminal
On Mac: Press `Cmd + Space`, type "Terminal", press Enter.

## Step 2: Install Python (if needed)
```bash
curl -o python.pkg https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg
sudo installer -pkg python.pkg -target /
```

## Step 3: Install AYOVA (One Line!)
```bash
pip3 install git+https://github.com/joselovesai/ayova.git
```

**Expected Output:**
```
Collecting git+https://github.com/joselovesai/ayova.git
  Cloning https://github.com/joselovesai/ayova.git
  ...
Successfully installed ayova-2.0.0
```

---

# 2. First Time Setup

## Run the Setup Command
```bash
python3 -m ayova.cli setup
```

## What You Will See (Splash Screen):

```
╔═══════════════════════════════ ◉ A Y O V A ◉ ════════════════════════════════╗
║                                                                              ║
║              ▄▄▄       ███▄    █  ▒█████   ██▒   █▓ ▄▄▄                      ║
║              ▒████▄     ██ ▀█   █ ▒██▒  ██▒▓██░   █▒▒████▄                   ║
║              ▒██  ▀█▄  ▓██  ▀█ ██▒▒██░  ██▒ ▓██  █▒░▒██  ▀█▄                 ║
║              ░██▄▄▄▄██ ▓██▒  ▐▌██▒▒██   ██░  ▒██ █░░░██▄▄▄▄██                ║
║               ▓█   ▓██▒▒██░   ▓██░░ ████▓▒░   ▒▀█░   ▓█   ▓██▒               ║
║               ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░ ▒░▒░▒░    ░ ▐░   ▒▒   ▓▒█░               ║
║                ▒   ▒▒ ░░ ░░   ░ ▒░  ░ ▒ ▒░    ░ ░░    ▒   ▒▒ ░               ║
║                ░   ▒      ░   ░ ░ ░ ░ ░ ▒       ░░    ░   ▒                  ║
║                ░   ░           ░     ░ ░         ░      ░   ░                ║
║                                                                              ║
║                          ◉ P2P SECURE MESSENGER ◉                            ║
║                           by Ayogwokhai Josemaria                            ║
║                                                                              ║
║                   v2.0 Light Hybrid • Ed25519 • NaCl E2E                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Choose Your Username
```
╔════════════════════════════════════════════════╗
║  Choose your AYOVA username (e.g., @alice)     ║
╚════════════════════════════════════════════════╝
▶ @alice
✓ Identity created: @alice
```

## Your Identity Is Created!

```
╔════════════════════════════════════════════════════╗
║         ◉ Your AYOVA Identity ◉                    ║
╠════════════════════════════════════════════════════╣
║ Username:        @alice                            ║
║ Device ID:       abc123def456                      ║
║ Fingerprint:     🦁🦊🐼🐨🐯🐷🐸🐙 A1B2C3D4      ║
║ Public Key:      a1b2c3d4e5f6... (truncated)      ║
╚════════════════════════════════════════════════════╝
```

**Important:** Save this fingerprint! It helps you verify you're talking to the right person.

---

# 3. Sharing Your Identity

## Get Your Public Key
```bash
python3 -m ayova.cli id --export
```

## Output to Share With Friends:
```json
{
  "username": "alice",
  "device_id": "abc123def456789",
  "public_key": "a1b2c3d4e5f6789...",
  "fingerprint": "🦁🦊🐼🐨🐯🐷🐸🐙 A1B2C3D4"
}
```

## How to Share:
1. Copy the output above
2. Send via any method: iMessage, WhatsApp, Email, QR code
3. Your friend needs this to trust you

**Screenshot of what your friend sees:**
```
[You sending to Bob]

"Hey Bob! Here's my AYOVA ID so you can trust me:"

{
  "username": "alice",
  "public_key": "a1b2c3d4...",
  "fingerprint": "🦁🦊🐼🐨🐯🐷🐸🐙 A1B2C3D4"
}
```

---

# 4. Trusting a Contact

## The Trust Rule: **B Must Trust A First!**

Before Alice can message Bob, **Bob must trust Alice first.**

This prevents spam and unwanted messages!

## Step-by-Step: Trust Your Friend

### 1. Get Their Public Key (they send it to you)
```
Friend sends you:

{
  "username": "bob",
  "public_key": "e5f6g7h8i9j0...",
  "fingerprint": "🐨🐯🐷🐸🐙🦁🦊🐼 E5F6G7H8"
}
```

### 2. Add Them to Your Trust List
```bash
python3 -m ayova.cli trust @bob --pubkey e5f6g7h8i9j0...
```

**Expected Output:**
```
╔════════════════════════════════════════════════╗
║  Adding @bob to trust list...                  ║
╚════════════════════════════════════════════════╝
⠋ Processing...

✓ Now trusting @bob. They can now send you messages.
ℹ Use 'ayova send @bob "Hello"' to message them back.
```

### 3. Verify Your Trust List
```bash
python3 -m ayova.cli trusted
```

**Output:**
```
╔════════════════════════════════════════════════════╗
║         🔐 Trusted Contacts                        ║
╠════════════════════════════════════════════════════╣
║ Username      Fingerprint            Trusted Since ║
║ ─────────────────────────────────────────────────── ║
║ 🔴 @bob       🐨🐯🐷🐸🐙🦁🦊🐼 E5F6...   2026-03-19 ║
║ 🟠 @charlie   🐷🐸🐙🦁🦊🐼🐨🐯 C1D2...   2026-03-18 ║
╚════════════════════════════════════════════════════╝
```

---

# 5. Sending Messages

## Send a Message to Trusted Contact
```bash
python3 -m ayova.cli send @bob "Hello Bob! How are you?" --host bob-laptop.local --tcp
```

**What Happens (Visual Flow):**

```
Step 1: You type the message
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  You: "Hello Bob! How are you?"

Step 2: AYOVA checks trust
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Checking if @bob is trusted... ✓ Yes!
  Getting @bob's public key... ✓ Found!

Step 3: Encrypt the message
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔐 Encrypting with NaCl Box...
  Using Bob's public key: e5f6g7h8...
  Result: [Encrypted blob - unreadable by anyone except Bob]

Step 4: Send over network
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📤 Connecting to bob-laptop.local:23231...
  📤 Sending encrypted payload...
  📤 Delivery complete!

Step 5: Success!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ Message securely delivered to @bob ✨
```

**Terminal Output:**
```
╔═══════════════════════════════ ◉ A Y O V A ◉ ════════════════════════════════╗
║                                                                              ║
║              [Purple splash screen appears briefly...]                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

⠋ Encrypting message...
⠙ Connecting to bob-laptop.local...
⠹ Sending encrypted payload...

✓ Message securely delivered to @bob ✨
```

---

# 6. Interactive Chat Mode

## Start Interactive Mode
```bash
python3 -m ayova.cli chat
```

**What You See:**
```
╔═══════════════════════════════ ◉ A Y O V A ◉ ════════════════════════════════╗
║                                                                              ║
║              [Splash screen appears...]                                       ║
║                                                                              ║
║              Welcome alice! Interactive mode started.                        ║
║              Commands: send, trust, stats, inbox, help, exit                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

ayova> 
```

## Available Commands in Chat Mode

| Type This | What Happens |
|-----------|-------------|
| `send @bob "hi" --host 192.168.1.5` | Sends message to Bob |
| `trust @alice --pubkey abc...` | Trust someone new |
| `trusted` | Show your trust list |
| `stats` | Show your info |
| `inbox` | Check messages |
| `help` | Show all commands |
| `exit` | Quit AYOVA |

**Example Session:**
```
ayova> stats

╔════════════════════════════════════════════════╗
║         ◉ AYOVA Statistics ◉                   ║
╠════════════════════════════════════════════════╣
║ 📁 Total Messages    12                        ║
║ 🔐 Trusted Contacts  2                         ║
║ 👤 Identity          ✓ Created                 ║
║ 💾 Storage           ~/.ayova/                 ║
║ 🔒 Encryption        NaCl Box (Curve25519)     ║
║ 🌐 P2P Mode          Light Hybrid              ║
╚════════════════════════════════════════════════╝

ayova> send @bob "Hey!" --host 192.168.1.5
✓ Message securely delivered to @bob ✨

ayova> exit
ℹ Goodbye! 👋
```

---

# 7. Local Vault Mode

## Write a Private Note (No Network Needed)
```bash
python3 -m ayova.cli write "My secret password is..." --tag secrets
```

**Interactive Prompt:**
```
╔════════════════════════════════════════════════╗
║  Enter your vault password                     ║
╚════════════════════════════════════════════════╝
▶ *********

⠋ Encrypting...
✓ Local message saved! ID: #1, Tag: secrets
```

## Read Your Notes
```bash
python3 -m ayova.cli read --all
```

**Output:**
```
╔════════════════════════════════════════════════╗
║ 🔐 Messages (3 total)                         ║
╠════════════════════════════════════════════════╣
║ #1 secrets    2026-03-19 14:30:22             ║
║ #2 work       2026-03-19 13:15:00             ║
║ #3 personal   2026-03-18 22:45:10             ║
╚════════════════════════════════════════════════╝
```

## Decrypt a Specific Note
```bash
python3 -m ayova.cli read 1
```

**Interactive Decryption:**
```
╔════════════════════════════════════════════════╗
║  Enter password                                  ║
╚════════════════════════════════════════════════╝
▶ *********

⠙ Decrypting...

╔════════════════════════════════════════════════╗
║  #1 secrets          2026-03-19 14:30:22       ║
║                                                ║
║  🔓 decrypted content                          ║
║  My secret password is...                       ║
╚════════════════════════════════════════════════╝

✓ Decryption successful ✨
```

---

# 8. Troubleshooting

## Problem: "command not found: ayova"

**Cause:** PATH not set correctly.

**Fix 1 - Use Python module:**
```bash
python3 -m ayova.cli init
```

**Fix 2 - Add to PATH permanently:**
```bash
echo 'export PATH="/Library/Frameworks/Python.framework/Versions/3.9/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
ayova init  # Now this works!
```

---

## Problem: "No module named 'nacl'"

**Cause:** Missing PyNaCl library.

**Fix:**
```bash
pip3 install pynacl asyncssh
```

---

## Problem: "@bob not in trust list"

**Cause:** Trying to message someone you haven't trusted.

**Fix:**
```bash
# Step 1: Get their public key (they send it to you)
# Step 2: Trust them
python3 -m ayova.cli trust @bob --pubkey <their_key>

# Step 3: Now you can message them
python3 -m ayova.cli send @bob "Hello" --host their-ip
```

---

## Problem: "Failed to deliver message"

**Possible Causes:**
1. **Recipient offline** → They need to be online to receive
2. **Wrong IP/hostname** → Double-check the --host value
3. **Firewall blocking** → Port 23231 (TCP) or 22 (SSH) must be open

**Fix:**
```bash
# Test with localhost first
python3 -m ayova.cli send @bob "test" --host 127.0.0.1 --tcp
```

---

## Problem: Installation is slow

**Cause:** Compiling from source on old Mac.

**Fix - Use pre-built Python:**
```bash
# Cancel current installation (Ctrl+C)

# Download smaller Python
curl -o python.pkg https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg
sudo installer -pkg python.pkg -target /
rm python.pkg

# Then install AYOVA
pip3 install git+https://github.com/joselovesai/ayova.git
```

---

# Quick Reference Card

**Print this and keep it handy!**

```
╔════════════════════════════════════════════════════════╗
║              AYOVA Quick Commands                        ║
╠════════════════════════════════════════════════════════╣
║ Install:                                               ║
║   pip3 install git+https://github.com/joselovesai/ayova.git  ║
║                                                        ║
║ Setup:                                                 ║
║   python3 -m ayova.cli setup                           ║
║                                                        ║
║ Share Identity:                                        ║
║   python3 -m ayova.cli id --export                   ║
║                                                        ║
║ Trust Someone:                                       ║
║   python3 -m ayova.cli trust @user --pubkey KEY      ║
║                                                        ║
║ Send Message:                                        ║
║   python3 -m ayova.cli send @user "msg" --host IP    ║
║                                                        ║
║ Interactive Mode:                                    ║
║   python3 -m ayova.cli chat                          ║
║                                                        ║
║ Local Vault:                                         ║
║   python3 -m ayova.cli write "secret" --tag diary   ║
║   python3 -m ayova.cli read --all                    ║
╚════════════════════════════════════════════════════════╝
```

---

# Congratulations! 🎉

You now know how to use **AYOVA P2P** - the secure, trust-first messenger!

**Remember:**
- 🔐 **Trust first** - Add people before they can message you
- 💜 **Purple UI** - Look for the beautiful splash screen
- 🌐 **P2P** - No servers, direct device-to-device
- 💾 **Light** - Only ~120MB RAM needed

**Built with 💜 by Ayogwokhai Josemaria**

**GitHub:** https://github.com/joselovesai/ayova

---

*End of Guide*
