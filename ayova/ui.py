"""Terminal UI components with Rich - AYOVA Light Hybrid P2P"""
import time
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box
from datetime import datetime


console = Console()


# 🎨 AYOVA ASCII Art with periwinkle/lavender gradient (#9B8AE0 style)
AYOVA_ASCII = """
 ▄▄▄       ███▄    █  ▒█████   ██▒   █▓ ▄▄▄      
▒████▄     ██ ▀█   █ ▒██▒  ██▒▓██░   █▒▒████▄    
▒██  ▀█▄  ▓██  ▀█ ██▒▒██░  ██▒ ▓██  █▒░▒██  ▀█▄  
░██▄▄▄▄██ ▓██▒  ▐▌██▒▒██   ██░  ▒██ █░░░██▄▄▄▄██ 
 ▓█   ▓██▒▒██░   ▓██░░ ████▓▒░   ▒▀█░   ▓█   ▓██▒
 ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░ ▒░▒░▒░    ░ ▐░   ▒▒   ▓▒█░
  ▒   ▒▒ ░░ ░░   ░ ▒░  ░ ▒ ▒░    ░ ░░    ▒   ▒▒ ░
  ░   ▒      ░   ░ ░ ░ ░ ░ ▒       ░░    ░   ▒   
  ░   ░           ░     ░ ░         ░      ░   ░   
"""


def show_splash(duration: float = 1.5):
    """Display animated splash screen with purple/lavender theme"""
    # Periwinkle/lavender gradient colors
    logo_text = Text(AYOVA_ASCII.strip())
    logo_text.stylize("bold #9B8AE0")  # Periwinkle/light purple from image
    
    # Subtitle with glow effect
    subtitle = Text("◉ P2P SECURE MESSENGER ◉", style="bold #B8B0E0")
    
    # Author
    author = Text("by Ayogwokhai Jose Maria", style="dim #8A7BC0")
    
    # Version
    version = Text("v2.0 Light Hybrid • Ed25519 • NaCl E2E", style="dim #7A6BB0")
    
    # Combine all elements
    content = Group(
        logo_text,
        Text(),  # Spacer
        Align.center(subtitle),
        Align.center(author),
        Text(),  # Spacer
        Align.center(version)
    )
    
    # Elegant double border with purple theme
    panel = Panel(
        Align.center(content),
        border_style="#9B8AE0",  # Periwinkle border
        box=box.DOUBLE,
        padding=(1, 4),
        title="[bold #9B8AE0]◉ A Y O V A ◉[/bold #9B8AE0]",
        title_align="center",
    )
    
    # Show with loading effect
    with console.screen():
        with Live(panel, refresh_per_second=15, screen=False) as live:
            for i in range(int(duration * 15)):
                live.update(panel)
                time.sleep(0.066)
    
    # Print final static version
    console.print(panel)
    console.print()


def show_loading(message: str = "Processing..."):
    """Show spinner with purple styling"""
    spinner = Spinner("dots12", text=message, style="bold #9B8AE0")
    return Live(spinner, refresh_per_second=15, transient=True)


def success(message: str):
    """Success message with green"""
    console.print(f"[bold bright_green]✓[/bold bright_green] {message}")


def error(message: str):
    """Error message with red"""
    console.print(f"[bold bright_red]✗[/bold bright_red] {message}")


def warn(message: str):
    """Warning with yellow"""
    console.print(f"[bold bright_yellow]⚠[/bold bright_yellow] {message}")


def info(message: str):
    """Info with purple"""
    console.print(f"[bold #9B8AE0]ℹ[/bold #9B8AE0] {message}")


def prompt_input(prompt_text: str, password: bool = False) -> str:
    """Secure input prompt"""
    console.print(Panel(
        f"[bold #9B8AE0]{prompt_text}[/bold #9B8AE0]",
        border_style="#9B8AE0",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    return console.input("[dim #7A6BB0]▶ [/dim #7A6BB0]", password=password)


def show_identity(identity: dict):
    """Display identity info beautifully"""
    grid = Table(
        title="[bold #9B8AE0]◉ Your AYOVA Identity ◉[/bold #9B8AE0]",
        box=box.DOUBLE,
        border_style="#9B8AE0",
        show_header=False,
        padding=(1, 2)
    )
    grid.add_column("Field", style="dim #B8B0E0")
    grid.add_column("Value", style="bold #E8E0F0")
    
    grid.add_row("Username", identity.get('username', 'N/A'))
    grid.add_row("Device ID", identity.get('device_id', 'N/A')[:16] + "...")
    grid.add_row("Fingerprint", identity.get('fingerprint', 'N/A'))
    grid.add_row("Public Key", identity.get('public_key', 'N/A')[:32] + "...")
    
    console.print(grid)
    console.print("\n[dim]Share your public key with friends so they can trust you.[/dim]\n")


def show_trusted(contacts: list):
    """Display trusted contacts"""
    if not contacts:
        warn("No trusted contacts yet. Use 'ayova trust add @username --pubkey ...'")
        return
    
    table = Table(
        title="[bold #9B8AE0]🔐 Trusted Contacts[/bold #9B8AE0]",
        box=box.ROUNDED,
        border_style="#9B8AE0",
        show_header=True,
        header_style="bold #B8B0E0"
    )
    table.add_column("Username", style="bold #E8E0F0")
    table.add_column("Fingerprint", style="#B8B0E0")
    table.add_column("Trusted Since", style="dim #8A7BC0")
    
    for contact in contacts:
        table.add_row(
            contact.get('username', 'N/A'),
            contact.get('fingerprint', 'N/A')[:20],
            contact.get('trusted_at', 'N/A')
        )
    
    console.print(table)
    console.print()


def show_inbox(messages: list):
    """Display P2P inbox"""
    if not messages:
        info("No messages in inbox.")
        return
    
    panel = Panel(
        f"[bold #9B8AE0]📨 Inbox ({len(messages)} messages)[/bold #9B8AE0]",
        border_style="#9B8AE0",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(panel)
    
    for msg in messages:
        msg_panel = Panel(
            f"[bold #E8E0F0]From:[/bold #E8E0F0] [dim]{msg.get('sender', 'Unknown')}[/dim]\n"
            f"[bold #E8E0F0]Content:[/bold #E8E0F0] {msg.get('content', '[encrypted]')[:100]}...\n"
            f"[dim #8A7BC0]{msg.get('timestamp', 'Unknown time')}[/dim #8A7BC0]",
            border_style="#8A7BC0",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(msg_panel)
    console.print()


def show_send_success(recipient: str):
    """Show successful send"""
    success(f"Message securely delivered to [bold #9B8AE0]@{recipient}[/bold #9B8AE0] ✨")


def show_stats(local_count: int, trusted_count: int, identity_exists: bool):
    """Display vault statistics"""
    stats = Table(
        title="[bold #9B8AE0]◉ AYOVA Statistics ◉[/bold #9B8AE0]",
        box=box.DOUBLE,
        border_style="#9B8AE0",
        show_header=False,
        padding=(1, 2)
    )
    stats.add_column("Metric", style="dim #B8B0E0")
    stats.add_column("Value", style="bold #E8E0F0")
    
    stats.add_row("📝 Local Messages", str(local_count))
    stats.add_row("🔐 Trusted Contacts", str(trusted_count))
    stats.add_row("👤 Identity", "✓ Created" if identity_exists else "✗ Not set up")
    stats.add_row("💾 Storage", "~/.ayova/")
    stats.add_row("🔒 E2E Encryption", "NaCl Box (Curve25519)")
    stats.add_row("🌐 P2P Mode", "Light Hybrid (Client-only)")
    
    console.print(stats)
    console.print()
