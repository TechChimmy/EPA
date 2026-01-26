from shared.db import get_conn
from datetime import datetime
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

def raise_alert(file, entropy, message, process_info=None):
    """
    Raise a ransomware alert with optional process attribution
    
    Args:
        file: File path that triggered the alert
        entropy: Entropy value of the file
        message: Alert message
        process_info: Optional dict with process details (pid, name, cmdline, parent)
    """
    # Extract process information
    process_id = None
    process_name = None
    process_cmdline = None
    process_parent = None
    
    if process_info:
        process_id = process_info.get("pid")
        process_name = process_info.get("name")
        process_cmdline = process_info.get("cmdline")
        process_parent = process_info.get("parent")
    
    # Store alert in database
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """INSERT INTO alerts 
               (file, entropy, message, process_id, process_name, process_cmdline, process_parent) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (file, entropy, message, process_id, process_name, process_cmdline, process_parent)
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️  Failed to store alert in database: {e}")
    
    # Print colored console alert
    print_console_alert(file, entropy, message, process_info)

def print_console_alert(file, entropy, message, process_info=None):
    """Print a colored alert to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if COLORS_AVAILABLE:
        print(f"\n{Fore.RED}{'=' * 70}")
        print(f"{Fore.RED}🚨 RANSOMWARE ALERT DETECTED 🚨")
        print(f"{Fore.RED}{'=' * 70}")
        print(f"{Fore.YELLOW}Time:     {Style.RESET_ALL}{timestamp}")
        print(f"{Fore.YELLOW}File:     {Style.RESET_ALL}{file}")
        print(f"{Fore.YELLOW}Entropy:  {Style.RESET_ALL}{entropy:.4f}")
        print(f"{Fore.YELLOW}Message:  {Style.RESET_ALL}{message}")
        
        if process_info:
            suspicious_marker = f" {Fore.RED}[SUSPICIOUS]" if process_info.get("suspicious") else ""
            print(f"{Fore.CYAN}Process:  {Style.RESET_ALL}PID {process_info.get('pid')} - {process_info.get('name')}{suspicious_marker}")
            if process_info.get('cmdline') and process_info.get('cmdline') != "N/A":
                print(f"{Fore.CYAN}Command:  {Style.RESET_ALL}{process_info.get('cmdline')}")
            if process_info.get('parent') and process_info.get('parent') != "N/A":
                print(f"{Fore.CYAN}Parent:   {Style.RESET_ALL}{process_info.get('parent')}")
        
        print(f"{Fore.RED}{'=' * 70}{Style.RESET_ALL}\n")
    else:
        # Fallback without colors
        print(f"\n{'=' * 70}")
        print(f"🚨 RANSOMWARE ALERT DETECTED 🚨")
        print(f"{'=' * 70}")
        print(f"Time:     {timestamp}")
        print(f"File:     {file}")
        print(f"Entropy:  {entropy:.4f}")
        print(f"Message:  {message}")
        
        if process_info:
            suspicious_marker = " [SUSPICIOUS]" if process_info.get("suspicious") else ""
            print(f"Process:  PID {process_info.get('pid')} - {process_info.get('name')}{suspicious_marker}")
            if process_info.get('cmdline') and process_info.get('cmdline') != "N/A":
                print(f"Command:  {process_info.get('cmdline')}")
            if process_info.get('parent') and process_info.get('parent') != "N/A":
                print(f"Parent:   {process_info.get('parent')}")
        
        print(f"{'=' * 70}\n")
