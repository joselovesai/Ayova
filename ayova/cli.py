"""AYOVA CLI - Light Hybrid P2P with Interactive Chat Mode"""
import click
import asyncio
from . import ui, storage, crypto
from .identity import get_identity
from .trust import get_trust_manager
from .network import send_to_peer
from .protocol import pack_message, unpack_message
import base64
import json


@click.group(invoke_without_command=True)
@click.option('--chat', is_flag=True, help='Start interactive chat mode')
@click.version_option(version="2.0.0")
def main(chat):
    """
    ◉ AYOVA P2P - Secure Messenger ◉
    
    🔐 Device-based, trust-first, E2E encrypted messaging.
    By Ayogwokhai Josemaria
    
    Run 'ayova --chat' for interactive mode
    """
    if chat:
        interactive_chat()


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
@click.argument("recipient")
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
    
    recipient = recipient.lstrip('@')
    
    tm = get_trust_manager()
    trusted = tm.get_trusted(recipient)
    if not trusted:
        ui.error(f"@{recipient} not in trust list!")
        ui.info(f"Run: ayova trust @{recipient} --pubkey <their_key>")
        return
    
    try:
        recipient_pubkey = base64.b64decode(trusted['public_key'])
        
        with ui.show_loading("🔐 Encrypting message..."):
            payload = pack_message(message, identity.signing_key, recipient_pubkey)
        
        with ui.show_loading(f"📤 Sending to @{recipient}..."):
            success = asyncio.run(send_to_peer(
                recipient, host, payload, 
                use_ssh=not tcp, port=port
            ))
        
        if success:
            ui.show_send_success(recipient)
        else:
            ui.error("Failed to deliver. Is recipient online?")
            
    except Exception as e:
        ui.error(f"Send failed: {str(e)}")


@main.command()
def inbox():
    """Check received messages"""
    ui.show_splash(0.3)
    
    identity = get_identity()
    if not identity.exists():
        ui.error("No identity found!")
        return
    
    ui.info("P2P Listener Mode (Light Hybrid)")
    ui.console.print("""
[dim]To receive, sender needs your IP + must be trusted.[/dim]
[dim]Run 'ayova daemon' on a server for 24/7 mailbox (uses more RAM).[/dim]
    """)


@main.command()
def daemon():
    """Background listener (not in Light Hybrid)"""
    ui.show_splash(0.5)
    ui.warn("Daemon mode not in Light Hybrid (~120MB client-only).")
    ui.info("Use a VPS for full daemon mode (512MB+ RAM).")


@main.command()
def chat():
    """Interactive chat mode - runs until you type 'exit'"""
    interactive_chat()


def interactive_chat():
    """REPL loop - keeps running until exit"""
    ui.show_splash(0.5)
    
    identity = get_identity()
    if not identity.exists():
        ui.error("No identity! Run 'ayova setup' first.")
        return
    
    ui.info(f"Welcome [bold]{identity.username}[/bold]! Interactive mode started.")
    ui.console.print("Commands: send @user msg --host, trust, stats, inbox, help, exit")
    ui.console.print()
    
    while True:
        try:
            cmd = ui.console.input("[bold #9B8AE0]ayova> [/bold #9B8AE0]")
            cmd = cmd.strip()
            
            if not cmd:
                continue
            elif cmd.lower() in ['exit', 'quit', 'q']:
                ui.info("Goodbye! 👋")
                break
            elif cmd.lower() == 'help':
                ui.console.print("""
send @user "message" --host <ip>    Send message
trust @user --pubkey <key>          Trust someone
stats                                Show your info
trusted                              List trusted contacts
inbox                                Check messages
setup                                Create identity
exit                                 Quit
                """)
            elif cmd.lower() == 'stats':
                store = storage.MessageStore()
                local_count = store.count_messages()
                tm = get_trust_manager()
                ui.show_stats(local_count, len(tm.list_trusted()), True)
            elif cmd.lower().startswith('send '):
                ui.info("Use: send @user \"message\" --host <ip>")
            elif cmd.lower() == 'trusted':
                tm = get_trust_manager()
                ui.show_trusted(tm.list_trusted())
            elif cmd.lower() == 'inbox':
                ui.info("Inbox: Check ayova inbox (placeholder for listener)")
            elif cmd.lower() == 'setup':
                ui.info("Run 'ayova setup' (non-interactive)")
            else:
                ui.warn(f"Unknown: {cmd}. Type 'help' for commands.")
                
        except KeyboardInterrupt:
            ui.info("\nGoodbye! 👋")
            break
        except EOFError:
            break


# Legacy local vault commands
@main.command()
@click.argument("message", required=True)
@click.option("--tag", "-t", default="general")
@click.option("--password", "-p", help="Encryption password")
def write(message: str, tag: str, password: str):
    """Write local encrypted message"""
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
    """Initialize AYOVA"""
    ui.show_splash(1.5)
    
    identity = get_identity()
    if not identity.exists():
        ui.info("Welcome to AYOVA P2P!")
        ui.console.print("""
[bold]Quick start:[/bold]
  1. Create identity:    ayova setup
  2. Interactive mode:   ayova chat
  3. Show your ID:        ayova id --export
  4. Trust a contact:     ayova trust @bob --pubkey <key>
  5. Send message:        ayova send @bob "Hello" --host bob.com
  6. View stats:          ayova stats

[dim]Your data is in ~/.ayova/[/dim]
        """)
    else:
        stats()


if __name__ == "__main__":
    main()
