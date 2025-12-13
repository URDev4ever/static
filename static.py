#!/usr/bin/env python3
"""
Static v1.5 - Typosquatting Scout
Finds unregistered typo domains for security testing.
Usage: python static.py -d target.com
"""

import sys
import os
import argparse
import socket
import http.client
import ssl
from urllib.parse import urlparse
import time
import signal
import threading
from datetime import datetime

# ========== GLOBAL FLAGS AND COUNTERS ==========
SCAN_INTERRUPTED = False
SCAN_STATS = {
    'current': 0,
    'total': 0,
    'potentially_available': 0,
    'redirects': 0,
    'taken': 0,
    'running': False
}

# ========== THREAD LOCK FOR SAFETY ==========
stats_lock = threading.Lock()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global SCAN_INTERRUPTED
    SCAN_INTERRUPTED = True
    with stats_lock:
        SCAN_STATS['running'] = False
    print(f"\n\n{Colors.RED}{Colors.BOLD}[!] SIGINT RECEIVED | ABORTING SCAN{Colors.END}")
    time.sleep(0.3)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

# ========== CROSS-PLATFORM CLEAR SCREEN ==========
def clear_screen():
    """Clear terminal screen for Windows, Linux, macOS."""
    os.system('cls' if os.name == 'nt' else 'clear')

# ========== ANSI COLOR CODES ==========
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ========== BANNER WITH COLORS ==========
def banner():
    clear_screen()
    print(f"""{Colors.CYAN}{Colors.BOLD}
                                     88
            ,d                 ,d    ""
            88                 88
,adPPYba, MM88MMM ,adPPYYba, MM88MMM 88  ,adPPYba,
I8[    ""   88    ""     `Y8   88    88 a8"     ""
 `"Y8ba,    88    ,adPPPPP88   88    88 8b
aa    ]8I   88,   88,    ,88   88,   88 "8a,   ,aa
`"YbbdP"'   "Y888 `"8bbdP"Y8   "Y888 88  `"Ybbd8"'

{Colors.MAGENTA}{Colors.BOLD}│------------------------------------------------│
│    static.py    │     By URDev    │    v1.5    │
│------------------------------------------------│{Colors.END}
    """)

# ========== PROGRESS DISPLAY THREAD ==========
def progress_display():
    """Display thread that updates progress independently every 250ms."""
    frames = ['◐', '◓', '◑', '◒']
    frame_idx = 0
    start_time = time.time()

    while True:
        with stats_lock:
            if not SCAN_STATS['running']:
                break

            current = SCAN_STATS['current']
            total = SCAN_STATS['total']
            potentially_available = SCAN_STATS['potentially_available']
            redirects = SCAN_STATS['redirects']
            taken = SCAN_STATS['taken']
            elapsed = time.time() - start_time

        # Update frame
        frame_idx = (frame_idx + 1) % len(frames)
        spinner = frames[frame_idx]

        # Progress bar
        progress_width = 20
        if total > 0:
            filled = int((current / total) * progress_width)
        else:
            filled = 0
        bar = f"{Colors.GREEN}{'█' * filled}{Colors.GRAY}{'░' * (progress_width - filled)}{Colors.END}"

        # Build single display line
        current_date = datetime.now().strftime("%Y-%m-%d")
        time_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"

        # Single line with everything
        line = (
            f"{Colors.CYAN}{Colors.BOLD}{spinner} Scanning{Colors.END} "
            f"{bar} "
            f"{Colors.WHITE}[{current}/{total}]{Colors.END} "
            f"{Colors.YELLOW}[{time_str}]{Colors.END} "
            f"{Colors.MAGENTA}[{current_date}]{Colors.END}"
        )

        # Clear and redraw single line
        sys.stdout.write('\r\033[K')  # Clear current line
        sys.stdout.write(line)
        sys.stdout.flush()

        time.sleep(0.25)  # Refresh every 250ms

    # Clean up display when thread ends
    sys.stdout.write('\r\033[K')  # Clear the line
    sys.stdout.flush()

# ========== TYPO GENERATION ==========
def generate_typos(domain):
    """Generate typo-based domain variations."""
    variants = set()

    base = domain.lower()
    tld = ''
    if '.' in base:
        base, tld = base.rsplit('.', 1)
        tld = '.' + tld

    # 1. Character deletion
    for i in range(len(base)):
        variants.add(base[:i] + base[i+1:] + tld)

    # 2. Character duplication
    for i in range(len(base)):
        variants.add(base[:i] + base[i] + base[i] + base[i+1:] + tld)

    # 3. Adjacent character swap
    for i in range(len(base)-1):
        swapped = list(base)
        swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
        variants.add(''.join(swapped) + tld)

    # 4. QWERTY adjacent replacement
    for i, char in enumerate(base):
        if char in QWERTY_ADJACENT:
            for replacement in QWERTY_ADJACENT[char]:
                variants.add(base[:i] + replacement + base[i+1:] + tld)

    # 5. TLD variations
    if tld:
        for new_tld in TLD_VARIANTS:
            if new_tld != tld:
                variants.add(base + new_tld)

    # Apply to full domain
    full_domain = base + tld
    if full_domain.count('.') > 1:
        for i in range(len(full_domain)):
            if full_domain[i] == '.' and i > 0:
                variants.add(full_domain[:i] + full_domain[i+1:])

    return sorted([v for v in variants if v != domain])

# ========== DOMAIN CHECKING ==========
def check_dns(domain):
    """Check DNS resolution."""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        try:
            socket.getaddrinfo(domain, None)
            return True
        except:
            return False

def check_http(domain, timeout=3):
    """Check HTTP/HTTPS response. Falls back to GET if HEAD fails."""
    schemes = ['http', 'https']

    for scheme in schemes:
        try:
            if scheme == 'http':
                conn = http.client.HTTPConnection(domain, timeout=timeout)
            else:
                conn = http.client.HTTPSConnection(domain, timeout=timeout, context=ssl._create_unverified_context())

            # Try HEAD first
            conn.request('HEAD', '/')
            response = conn.getresponse()
            status = response.status
            location = response.getheader('Location', '')
            conn.close()

            if 100 <= status < 400:
                return status, location if location else None

        except:
            # Fallback to GET if HEAD fails or times out
            try:
                if scheme == 'http':
                    conn = http.client.HTTPConnection(domain, timeout=timeout)
                else:
                    conn = http.client.HTTPSConnection(domain, timeout=timeout, context=ssl._create_unverified_context())

                conn.request('GET', '/', headers={'User-Agent': 'static.py/1.5'})
                response = conn.getresponse()
                status = response.status
                location = response.getheader('Location', '')
                conn.close()

                if 100 <= status < 400:
                    return status, location if location else None
            except:
                continue

    return None, None

def verify_domain(domain):
    """Verify a single domain for availability."""
    if SCAN_INTERRUPTED:
        return 'INTERRUPTED', None, None

    # Check DNS
    dns_ok = check_dns(domain)

    if not dns_ok:
        # POTENTIALLY_AVAILABLE - No DNS doesn't guarantee it's actually available
        return 'POTENTIALLY_AVAILABLE', f'http://{domain}', None

    # Check HTTP/HTTPS
    status, redirect = check_http(domain)

    if status is None:
        return 'TAKEN', None, None  # DNS resolves but no HTTP

    if redirect:
        redirect_domain = urlparse(redirect).netloc
        if domain not in redirect_domain and redirect_domain:
            return 'REDIRECT', f'http://{domain}', redirect

    return 'TAKEN', None, None

# ========== QWERTY KEYBOARD ADJACENCY ==========
QWERTY_ADJACENT = {
    'q': ['w', 'a'], 'w': ['q', 'e', 's'], 'e': ['w', 'r', 'd'], 'r': ['e', 't', 'f'],
    't': ['r', 'y', 'g'], 'y': ['t', 'u', 'h'], 'u': ['y', 'i', 'j'], 'i': ['u', 'o', 'k'],
    'o': ['i', 'p', 'l'], 'p': ['o', 'l'], 'a': ['q', 's', 'z'], 's': ['a', 'w', 'd', 'x'],
    'd': ['s', 'e', 'f', 'c'], 'f': ['d', 'r', 'g', 'v'], 'g': ['f', 't', 'h', 'b'],
    'h': ['g', 'y', 'j', 'n'], 'j': ['h', 'u', 'k', 'm'], 'k': ['j', 'i', 'l'],
    'l': ['k', 'o', 'p'], 'z': ['a', 's', 'x'], 'x': ['z', 's', 'd', 'c'],
    'c': ['x', 'd', 'f', 'v'], 'v': ['c', 'f', 'g', 'b'], 'b': ['v', 'g', 'h', 'n'],
    'n': ['b', 'h', 'j', 'm'], 'm': ['n', 'j', 'k']
}

TLD_VARIANTS = ['.com', '.net', '.org', '.co', '.io']

def main():
    parser = argparse.ArgumentParser(description='Static v1.5 - Find available typo domains')
    parser.add_argument('-d', '--domain', required=True, help='Target domain (e.g., google.com)')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    banner()
    print(f"{Colors.CYAN}[{Colors.GREEN}+{Colors.CYAN}] Target: {Colors.BOLD}{args.domain}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

    # Generate variants
    variants = generate_typos(args.domain)

    if not variants:
        print(f"{Colors.YELLOW}[!] No variants generated.{Colors.END}")
        return

    print(f"{Colors.CYAN}[{Colors.GREEN}+{Colors.CYAN}] Generated {len(variants)} typo variants.{Colors.END}")
    print(f"{Colors.GRAY}[*] Press Ctrl+C to abort scan at any time{Colors.END}\n")

    # Initialize stats
    with stats_lock:
        SCAN_STATS.update({
            'total': len(variants),
            'current': 0,
            'potentially_available': 0,
            'redirects': 0,
            'taken': 0,
            'running': True
        })

    # Start progress display thread
    progress_thread = threading.Thread(target=progress_display, daemon=True)
    progress_thread.start()

    # Start scanning
    potentially_available = []
    redirects = []
    start_time = time.time()
    scan_start = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        for i, variant in enumerate(variants, 1):
            if SCAN_INTERRUPTED:
                break

            # Update current counter
            with stats_lock:
                SCAN_STATS['current'] = i

            # Verify domain
            status, url, redirect_url = verify_domain(variant)

            # Update stats and collect results
            with stats_lock:
                if status == 'POTENTIALLY_AVAILABLE':
                    SCAN_STATS['potentially_available'] += 1
                    potentially_available.append(url)
                elif status == 'REDIRECT':
                    SCAN_STATS['redirects'] += 1
                    redirects.append((url, redirect_url))
                elif status == 'TAKEN':
                    SCAN_STATS['taken'] += 1

    except Exception as e:
        print(f"\n{Colors.RED}[!] Error during scan: {e}{Colors.END}")

    finally:
        # Stop progress display
        with stats_lock:
            SCAN_STATS['running'] = False

        # Wait for progress thread to finish
        progress_thread.join(timeout=1)

        # Clear progress area
        sys.stdout.write('\n')
        sys.stdout.flush()

    # Calculate final stats
    total_time = time.time() - start_time

    # Show interruption message if needed
    if SCAN_INTERRUPTED:
        print(f"{Colors.RED}{Colors.BOLD}[✗] SCAN INTERRUPTED BY USER{Colors.END}")
        print(f"{Colors.RED}[!] Partial results shown below{Colors.END}")
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}[✓] SCAN COMPLETED{Colors.END}")

    print(f"{Colors.CYAN}[*] Duration: {int(total_time // 60):02d}:{int(total_time % 60):02d} | Started: {scan_start}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

    # Show POTENTIALLY_AVAILABLE domains
    if potentially_available:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[+] POTENTIALLY AVAILABLE DOMAINS ({len(potentially_available)}){Colors.END}")
        print(f"{Colors.GRAY}[!] No DNS resolution - may be actually available{Colors.END}")
        for url in potentially_available:
            print(f"    {Colors.GREEN}→ {url}{Colors.END}")
    else:
        print(f"\n{Colors.GRAY}[~] No potentially available domains found{Colors.END}")

    # Show REDIRECTS
    if redirects:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}[~] REDIRECTING DOMAINS ({len(redirects)}){Colors.END}")
        for url, redirect_url in redirects:
            print(f"    {Colors.YELLOW}[{url}] → {redirect_url}{Colors.END}")

    # Show summary
    print(f"\n{Colors.CYAN}{Colors.BOLD}[*] FINAL STATS{Colors.END}")
    print(f"    {Colors.GREEN}Potentially Available: {len(potentially_available)}{Colors.END}")
    print(f"    {Colors.YELLOW}Redirects: {len(redirects)}{Colors.END}")
    print(f"    {Colors.RED}Taken: {SCAN_STATS['taken']}{Colors.END}")
    print(f"    {Colors.WHITE}Total: {len(variants)}{Colors.END}")
    print(f"    {Colors.MAGENTA}Time: {int(total_time // 60):02d}:{int(total_time % 60):02d}{Colors.END}")
    print(f"    {Colors.BLUE}Speed: {len(variants)/total_time if total_time > 0 else 0:.1f} domains/sec{Colors.END}")

    # Footer
    print(f"\n{Colors.GRAY}{'─'*70}{Colors.END}")
    print(f"{Colors.WHITE}[!] static.py v1.5 | github.com/urdev4ever | {datetime.now().strftime('%Y-%m-%d')}{Colors.END}")

    # Exit code
    if SCAN_INTERRUPTED:
        sys.exit(130)

if __name__ == '__main__':
    main()
