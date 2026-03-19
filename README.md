# ◉ AYOVA ◉ P2P Secure Messenger

🔐 **Device-based, trust-first, E2E encrypted messaging**  
by **Ayogwokhai Josemaria**

[![Version](https://img.shields.io/badge/version-2.0.0-purple)](https://github.com/joselovesai/ayova)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://python.org)
[![Crypto](https://img.shields.io/badge/crypto-NaCl%20E2E-green)](https://nacl.cr.yp.to/)

---

## 🚀 One-Line Installation

```bash
pip3 install git+https://github.com/joselovesai/ayova.git
```

**Requirements:** Python 3.8+ (includes pip3)

---

## ✨ What is AYOVA?

AYOVA is a **secure peer-to-peer messenger** that puts you in control:

| Feature | How AYOVA Does It |
|---------|------------------|
| 🔐 **E2E Encryption** | NaCl Box (Curve25519 + XSalsa20 + Poly1305) |
| 🤝 **Trust-First** | Only trusted contacts can message you |
| 🎭 **Device Identity** | Ed25519 keys - one device = one account |
| 🌐 **P2P Messaging** | Direct device-to-device, no servers |
| 💜 **Light Hybrid** | ~120MB RAM (perfect for old laptops!) |
| 💾 **Local Vault** | Encrypted diary when offline |

---

## 🎯 Quick Start (5 Minutes)

### 1. Create Your Identity
```bash
python3 -m ayova.cli setup
```
Choose a username (e.g., `@alice`). This creates your Ed25519 keypair.

### 2. Share Your Public Key
```bash
python3 -m ayova.cli id --export
```
Copy this and send to friends so they can trust you.

### 3. Trust a Friend (So They Can Message You)
```bash
python3 -m ayova.cli trust @bob --pubkey <paste_bobs_key_here>
```
**Important:** You must trust someone BEFORE they can message you!

### 4. Send a Secure Message
```bash
python3 -m ayova.cli send @bob "Hello Bob!" --host bob-laptop.local --tcp
```

### 5. Interactive Mode (Chat Loop)
```bash
python3 -m ayova.cli chat
```
Runs until you type `exit`. Use commands: `send`, `trust`, `stats`, `help`

---

## 📚 All Commands

| Command | Description | Example |
|---------|-------------|---------|
| `setup` | Create your identity | `python3 -m ayova.cli setup` |
| `id --export` | Show your public key | `python3 -m ayova.cli id --export` |
| `trust @user --pubkey KEY` | Trust someone | `python3 -m ayova.cli trust @alice --pubkey abc123...` |
| `untrust @user` | Remove trust | `python3 -m ayova.cli untrust @alice` |
| `trusted` | List trusted contacts | `python3 -m ayova.cli trusted` |
| `send @user "msg" --host IP` | Send message | `python3 -m ayova.cli send @bob "Hi" --host 192.168.1.5 --tcp` |
| `chat` | Interactive mode | `python3 -m ayova.cli chat` |
| `inbox` | Check messages | `python3 -m ayova.cli inbox` |
| `stats` | Show your info | `python3 -m ayova.cli stats` |
| `write "msg" --tag X` | Local vault | `python3 -m ayova.cli write "secret" --tag diary` |
| `read --all` | Read local messages | `python3 -m ayova.cli read --all` |

---

## 🔐 How It Works

### The Trust Model (Why AYOVA is Special)

```
Traditional Messengers:
Anyone ──► Server ──► You  ❌ Server can read everything!

AYOVA P2P:
Alice ──🔐──► Bob  ✅ Only Bob can read it!
   ↑
   └── Only works if Bob trusts Alice first
```

### Security Flow

**Sending a Message:**
1. You trust Bob → Store his public key
2. Type message → Encrypt with Bob's public key (NaCl Box)
3. Send via TCP or SSH → Encrypted blob travels network
4. Bob decrypts with his private key → Reads message

**Receiving:**
1. Check if sender is in trust list → Reject if not
2. Verify sender's public key matches → Reject if mismatch
3. Decrypt with your private key → Show message

---

## 🛡️ Security Details

| Component | Implementation | Why It Matters |
|-----------|---------------|---------------|
| **Identity** | Ed25519 keypair | Unique per device, can't be faked |
| **E2E Encryption** | NaCl Box (Curve25519) | Unbreakable, used by Signal/Wire |
| **Forward Secrecy** | Ephemeral keys per message | Old messages safe even if key leaked |
| **Trust Model** | Whitelist-based | No spam, no strangers messaging you |
| **Transport** | SSH or direct TCP | Your choice, both encrypted |
| **RAM Usage** | ~120MB (Light Hybrid) | Runs on old laptops! |

---

## 📦 System Requirements

- **OS:** macOS, Linux, Windows (with Python)
- **Python:** 3.8 or newer
- **RAM:** 150MB available (Light Hybrid mode)
- **Network:** Internet or LAN for P2P

**Tested On:**
- macOS Catalina (3GB RAM)
- Ubuntu 22.04
- Kali Linux

---

## 🎨 The Purple Aesthetic

AYOVA features a custom purple gradient UI inspired by modern design:

```
╔═══════════════════════════════ ◉ A Y O V A ◉ ════════════════════════════════╗
║                                                                              ║
║              ▄▄▄       ███▄    █  ▒█████   ██▒   █▓ ▄▄▄                      ║
║                                                                              ║
║                   ◉ P2P SECURE MESSENGER ◉                                  ║
║                        by Ayogwokhai Josemaria                             ║
║                                                                              ║
║              v2.0 Light Hybrid • Ed25519 • NaCl E2E                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 🆘 Troubleshooting

### Command not found: `ayova`
```bash
# Use python module instead:
python3 -m ayova.cli init
```

### Module not found: `nacl`
```bash
pip3 install pynacl asyncssh
```

### Permission denied with Homebrew
```bash
# Use official Python installer instead
curl -o python.pkg https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg
sudo installer -pkg python.pkg -target /
```

---

## 🤝 Sharing AYOVA

**Tell your friends:**
```
🔐 AYOVA P2P - Secure messenger by Ayogwokhai Josemaria
Install: pip3 install git+https://github.com/joselovesai/ayova.git
GitHub: https://github.com/joselovesai/ayova
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

Built with 💜 by **Ayogwokhai Josemaria**

---

## 🙏 Credits

- **NaCl/libsodium** - Encryption library (Daniel Bernstein)
- **Rich** - Terminal UI (Will McGugan)
- **Click** - CLI framework (Armin Ronacher)
- **asyncssh** - SSH library (Ron Frederick)
