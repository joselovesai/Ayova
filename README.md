# ◉ AYOVA ◉ - Secure Message Vault CLI

🔐 Encrypted messaging with gradient aesthetics by **Ayogwokhai Jose Maria**

![Version](https://img.shields.io/badge/version-1.0.0-cyan)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Crypto](https://img.shields.io/badge/crypto-AES--128--CBC-magenta)

## ✨ Features

- 🔐 **AES-128-CBC + HMAC** encryption via Fernet
- 🏷️ **Tag-based organization** (work, personal, secrets, etc.)
- 🎨 **Rich gradient UI** with animated ASCII splash
- 💾 **SQLite storage** in `~/.ayova/`
- 🔑 **Password-derived keys** with PBKDF2 (480k iterations)
- 📊 **Stats & tagging** with beautiful tables
- ⚡ **Fast, local-first** - no cloud dependencies

## 🚀 Installation

```bash
cd vault_cli
pip install -e .
```

## 📝 Commands

```bash
# Initialize (shows beautiful gradient splash)
ayova init

# Write encrypted message
ayova write "My secret note" --tag personal
ayova write "API key: sk-xxx" --tag work --password mypassword

# List messages (encrypted view)
ayova read --all
ayova read --tag work

# Read/decrypt specific message
ayova read 1
ayova read 1 --password mypassword

# Manage tags
ayova tags

# View statistics
ayova stats

# Delete message
ayova delete 1
```

## 🔐 How Messaging Works

### Encryption Flow
1. **Password Input** → You provide a password (never stored)
2. **Key Derivation** → PBKDF2-HMAC-SHA256 generates a 32-byte key (480k iterations)
3. **Salt Generation** → Random 16-byte salt unique per message
4. **Fernet Encryption** → AES-128-CBC + HMAC encrypts your message
5. **Storage** → Encrypted blob + salt saved to SQLite

### Decryption Flow
1. **Retrieve Message** → Load encrypted blob and salt from database
2. **Re-derive Key** → PBKDF2(password + stored salt) = same key
3. **Fernet Decrypt** → AES-128-CBC decryption + HMAC verification
4. **Plaintext** → Original message restored

### Security Model
```
Your Password ──┐
                ├── PBKDF2 (480k iterations) ──► Encryption Key
Random Salt ────┘                                 │
                                                  ▼
Plaintext ───────────────────────────────► Fernet (AES-128-CBC + HMAC)
                                                  │
                                                  ▼
                                           Encrypted Blob ──► SQLite
```

## 📁 Architecture

```
ayova/
├── cli.py      # Click commands & UX flow
├── ui.py       # Rich terminal UI + gradient ASCII
├── crypto.py   # Fernet encryption with PBKDF2
├── storage.py  # SQLite operations
└── __init__.py
```

## 🛡️ Security Details

| Component | Implementation |
|-----------|---------------|
| Encryption | AES-128-CBC via Fernet |
| Authentication | HMAC-SHA256 |
| Key Derivation | PBKDF2-HMAC-SHA256 |
| Iterations | 480,000 (OWASP recommended) |
| Salt | 16 bytes (random per message) |
| Key Length | 32 bytes (256-bit) |

## 📦 Requirements

- Python 3.8+
- click >= 8.0
- rich >= 13.0
- cryptography >= 41.0

## 👤 Author

**Ayogwokhai Jose Maria** — Built with 💜 and gradient aesthetics
