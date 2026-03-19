"""AYOVA CLI - Light Hybrid P2P with device-based identity"""
import click
import asyncio
from . import ui, storage, crypto
from .identity import get_identity
from .trust import get_trust_manager
from .network import send_to_peer
from .protocol import pack_message, unpack_message
import base64
import json


@click.group()
@click.version_option(version="2.0.0")
def main():
    """
    ◉ AYOVA P2P - Secure Messenger ◉
    
    🔐 Device-based, trust-first, E2E encrypted messaging.
    By Ayogwokhai Jose Maria
    """
    pass


@main.command()
def setup():
    """Create your device identity (one-time setup)"""
    ui.show_splash(1.0)
    
    identity = get_identity()
    if identity.exists():
        ui.info("Identity already exists!")
        ui.show_identity(identity.get_public_identity())
        return
    
    username = ui.prompt_input("Choose your AYOVA username (e.g., @alice)")
    if not username:
        ui.error("Username required!")
        return
    
    with ui.show_loading("Generating Ed25519 identity keys..."):
        pub_id = identity.create(username)
    
    ui.success(f"Identity created: [bold]@{username}[/bold]")
    ui.show_identity(pub_id)


@main.command()
@click.option("--export", is_flag=True, help="Export public key for sharing")
def id(export):
    """Show your identity and public key"""
    identity = get_identity()
    if not identity.exists():
        ui.error("No identity found! Run 'ayova setup' first.")
        return
    
    ui.show_splash(0.3)
    pub_id = identity.get_public_identity()
    ui.show_identity(pub_id)
    
    if export:
        print("\n--- COPY BELOW TO SHARE ---")
        print(identity.export_public_key())
        print("--- END ---\n")


@main.command()
@click.argument("username")
@click.option("--pubkey", required=True, help="Base64-encoded public key")
@click.option("--device-id", help="Device ID (optional)")
@click.option("--fingerprint", help="Key fingerprint for verification")
@click.option("--notes", help="Optional notes about this contact")
def trust(username, pubkey, device_id, fingerprint, notes):
    """Trust a contact (required before they can message you)"""
    ui.show_splash(0.3)
    
    tm = get_trust_manager()
    
    # Verify key format
    try:
        base64.b64decode(pubkey)
    except Exception:
        ui.error("Invalid public key format! Must be base64.")
        return
    
    with ui.show_loading(f"Adding @{username} to trust list..."):
        success = tm.trust(username, pubkey, device_id, fingerprint, notes)
    
    if success:
        ui.success(f"Now trusting [bold]@{username}[/bold]. They can now send you messages.")
        ui.info(f"Use 'ayova send @{username} \"Hello\"' to message them back.")
    else:
        ui.error("Failed to add trust. Check the public key format.")


@main.command()
@click.argument("username")
def untrust(username):
    """Remove trust from a contact"""
    tm = get_trust_manager()
    if tm.untrust(username):
        ui.success(f"Removed trust from @{username}. They can no longer message you.")
    else:
        ui.warn(f"@{username} was not in your trust list.")


@main.command()
def trusted():
    """List all trusted contacts"""
    ui.show_splash(0.3)
    tm = get_trust_manager()
    contacts = tm.list_trusted()
    ui.show_trusted(contacts)


@main.command()
@click.argument("recipient")  # @username or username
@click.argument("message")
@click.option("--host", required=True, help="Recipient's hostname or IP")
@click.option("--port", default=22, help="Port (22 for SSH, 23231 for direct TCP)")
@click.option("--tcp", is_flag=True, help="Use direct TCP instead of SSH (lighter)")
def send(recipient, message, host, port, tcp):
    """Send encrypted message to a trusted contact"""
    ui.show_splash(0.5)
    
    identity = get_identity()
    if not identity.exists():
        ui.error("No identity! Run 'ayova setup' first.")
        return
    
    # Clean username
    recipient = recipient.lstrip('@')
    
    # Get recipient's public key from trust list
    tm = get_trust_manager()
    trusted = tm.get_trusted(recipient)
    if not trusted:
        ui.error(f"@{recipient} not in trust list!")
        ui.info(f"Run: ayova trust @{recipient} --pubkey <their_key>")
        return
    
    # Pack message with E2E encryption
    try:
        recipient_pubkey = base64.b64decode(trusted['public_key'])
        
        with ui.show_loading("🔐 Encrypting message..."):
            payload = pack_message(message, identity.signing_key, recipient_pubkey)
        
        # Send via network
        with ui.show_loading(f"📤 Sending to @{recipient} at {host}..."):
            success = asyncio.run(send_to_peer(
                recipient, host, payload, 
                use_ssh=not tcp, port=port
            ))
        
        if success:
            ui.show_send_success(recipient)
            # Save to local sent messages
            store = storage.MessageStore()
            store.save_message(payload, b'sent', f"sent:{recipient}")
        else:
            ui.error("Failed to deliver message. Is the recipient online?")
            
    except Exception as e:
        ui.error(f"Send failed: {str(e)}")


@main.command()
def inbox():
    """Check received messages (placeholder for listener mode)"""
    ui.show_splash(0.3)
    
    identity = get_identity()
    if not identity.exists():
        ui.error("No identity found!")
        return
    
    # For now, show placeholder - real listener needs async server
    ui.info("P2P Listener Mode")
    ui.console.print("""
[dim]To receive messages, the sender needs your hostname/IP.[/dim]
[dim]You must trust them first before they can message you.[/dim]

[bold]Quick start for receiving:[/bold]
1. Share your identity:  ayova id --export
2. Have them trust you:  ayova trust @you --pubkey <your_key>
3. They send:            ayova send @you "Hello" --host your-ip

[dim]Note: Full listener mode requires running 'ayova daemon' (coming soon)[/dim]
    """)


@main.command()
def daemon():
    """Start background listener for incoming messages (not implemented in Light Hybrid)"""
    ui.show_splash(0.5)
    ui.warn("Daemon mode not available in Light Hybrid.")
    ui.info("Light Hybrid is client-only to save RAM (~120MB vs ~250MB).")
    ui.console.print("""
[dim]For full P2P with daemon mode, use the SSH-based version.[/dim]
[dim]Trade-off: More RAM usage but can receive without initiating.[/dim]

[bold]Workaround for receiving messages:[/bold]
- Run AYOVA on a small VPS/cloud instance (512MB+ RAM)
- Use it as your "mailbox" - lightweight clients connect to it
- Or use direct TCP with port forwarding on your router
    """)


# Legacy local vault commands (preserved for backward compatibility)
@main.command()
@click.argument("message", required=True)
@click.option("--tag", "-t", default="general", help="Tag for categorization")
@click.option("--password", "-p", help="Encryption password")
def write(message: str, tag: str, password: str):
    """Write local encrypted message (legacy vault mode)"""
    ui.show_splash(0.5)
    
    if not password:
        password = ui.prompt_input("Enter password", password=True)
    
    with ui.show_loading("🔐 Encrypting..."):
        vault = crypto.CryptoVault(password)
        vault.set_password(password)
        encrypted, salt = vault.encrypt(message)
    
    store = storage.MessageStore()
    msg_id = store.save_message(encrypted, salt, tag)
    ui.success(f"Local message saved! ID: #{msg_id}, Tag: {tag}")


@main.command()
@click.argument("message_id", type=int, required=False)
@click.option("--tag", "-t", help="Filter by tag")
@click.option("--password", "-p", help="Decryption password")
@click.option("--all", "-a", is_flag=True, help="List all messages")
def read(message_id: int, tag: str, password: str, all: bool):
    """Read local encrypted messages"""
    ui.show_splash(0.3)
    
    store = storage.MessageStore()
    
    if not message_id or all:
        messages = store.get_messages(tag)
        ui.show_messages_list(messages, tag)
        return
    
    msg = store.get_message_by_id(message_id)
    if not msg:
        ui.error(f"Message #{message_id} not found!")
        return
    
    if not password:
        password = ui.prompt_input("Enter password", password=True)
    
    try:
        with ui.show_loading("🔓 Decrypting..."):
            vault = crypto.CryptoVault(password, msg['salt'])
            vault.set_password(password)
            decrypted = vault.decrypt(msg['encrypted_data'], msg['salt'])
        
        ui.console.print(ui.format_message_row(msg, decrypted))
        ui.success("Decrypted successfully ✨")
    except Exception:
        ui.error("Decryption failed! Wrong password.")


@main.command()
def stats():
    """Show AYOVA statistics"""
    ui.show_splash(0.3)
    
    store = storage.MessageStore()
    local_count = store.count_messages()
    
    tm = get_trust_manager()
    trusted_count = len(tm.list_trusted())
    
    identity = get_identity()
    
    ui.show_stats(local_count, trusted_count, identity.exists())


@main.command()
def init():
    """Initialize AYOVA (shows splash + quick start)"""
    ui.show_splash(1.5)
    
    identity = get_identity()
    if not identity.exists():
        ui.info("Welcome to AYOVA P2P!")
        ui.console.print("""
[bold]Quick start:[/bold]
  1. Create identity:    ayova setup
  2. Show your ID:      ayova id --export
  3. Trust a contact:   ayova trust @bob --pubkey <key>
  4. Send message:      ayova send @bob "Hello" --host bob.com
  5. View stats:        ayova stats

[dim]Your identity and messages are stored in ~/.ayova/[/dim]
        """)
    else:
        stats()


if __name__ == "__main__":
    main()
@main.command()
def chat():
    """Interactive chat mode - runs until you type 'exit'"""
    ui.show_splash(0.5)
    
    identity = get_identity()
    if not identity.exists():
        ui.error("No identity! Run 'ayova setup' first.")
        return
    
    ui.info(f"Welcome, {identity.username}! Type 'exit' to quit.")
    ui.console.print("Commands: trust, send, inbox, stats, or just type a message")
    ui.console.print()
    
    while True:
        try:
            # Get user input
            cmd = ui.console.input("[bold #9B8AE0]ayova> [/bold #9B8AE0]")
            
            if cmd.lower() in ['exit', 'quit', 'q']:
                ui.info("Goodbye! 👋")
                break
            elif cmd.lower() == 'stats':
                # Run stats command
                store = storage.MessageStore()
                local_count = store.count_messages()
                tm = get_trust_manager()
                ui.show_stats(local_count, len(tm.list_trusted()), True)
            elif cmd.lower().startswith('trust '):
                # Handle trust commands
                ui.info("Use: ayova trust @user --pubkey <key>")
            elif cmd.lower() == 'inbox':
                ui.show_inbox([])  # Placeholder
            else:
                ui.info(f"Unknown command: {cmd}. Try: trust, send, stats, inbox, exit")
                
        except KeyboardInterrupt:
            ui.info("\nGoodbye! 👋")
            break
        except EOFError:
            break
