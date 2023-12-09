# fastping by Synchresis Solutions
# Program Code Copyright (C) 2023-2024, Synchresis Solutions, LLC
# www.synchresis.net
#
# The purpose of this program is to allow Windows users access to a single-executable CLI ping
# tool that runs in current conhost thread and can run bulk pings in intervals less than 1
# second.  It DOES support flood ping (zero ms delay), even as a normal user.  This code DOES
# also work properly on macOS and Linux and PyInstaller should allow single portable binaries to
# be produced for both as well (that wasn't fully tested).  And, yes, fastping *does* work in many
# web-based RMM CLI sessions (tested specifically with Ninja RMM!)
#
# This program is provided for use free of charge in the hopes that it will be useful, and to aid
# in advertising our services mainly via this header and the lines of text the program outputs at
# runtime.  The following terms apply:
#
# 1. This code is provided in cleartext for auditing and building purposes ONLY
# 2. We will happily review pull requests and seek permission before merging
# 3. Binaries made based on this code in your environment may only be used within your working
#    environment, you may make changes as needed EXCEPT to remove references to Synchresis, but
#    you may not redistribute them
# 4. You may not represent this code as your own under any circumstances, and must refer any
#    interested parties to this repository
# 5. Contact Synchresis Solutions if you wish to licence fastping without Synchresis branding
#    for use in your MSP or corporate environment
#
# Visit Synchresis Solutions for all your on-call Tier3 technology needs:
# + Linux/macOS/BSD/IBM AIX (including POWER hardware)
# + Python, PHP Development
# + VoIP Telephony Support (Asterisk, FreePBX, FreeSWITCH, FusionPBX, Cisco UC)
# + Virtualization Support (VMware ESXi/vSphere, Hyper-V, Proxmox, Virtuozzo/OpenVZ,
#   QEMU/libvirt/KVM)
# + SynchreCMS American-managed fully modular CMS Platform
# + Unbeatable Price on quality, American-managed Cloud PBX, Cloud eFax
# All services provided by American engineers with 15+ years each hands-on SME experience
# All services available at competitive, industry-centric rates
# Contract services also available for round-the-clock Tier3 emergency event coverage
#
# Build Windows binaries by running, as admin:
# "pip install PyInstaller"
# Then, as either admin or your normal user, run:
# "pyinstaller --onefile fastping.py"
# You'll find fastping.exe which is a fully standalone binary in dist\fastping.exe
# From there, fastping.exe can be used on any Windows system matching or supporting the
# architecture of Python that you used to build the binary without any dependencies or
# files that need to be carried alongside it -- perfect for file transferring to a machine
# via RMM and using via an RMM console!

import socket
import time
import struct
import select
import sys
import os
import signal

def create_packet(id):
    """Create a new echo request packet based on the given ID."""
    header = struct.pack('bbHHh', 8, 0, 0, id, 1)
    data = 192 * b'Q'
    my_checksum = checksum(header + data)
    header = struct.pack('bbHHh', 8, 0, socket.htons(my_checksum), id, 1)
    return header + data

def checksum(source_string):
    """Verify the packet integrity."""
    sum = 0
    max_count = (len(source_string) / 2) * 2
    count = 0
    while count < max_count:
        val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + val
        sum = sum & 0xffffffff
        count = count + 2

    if max_count < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def do_one_ping(dest_addr, timeout, icmp_id):
    """Send one ping to the specified IP address."""
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError as e:
        raise PermissionError("Please escalate to root or administrative level and re-run.") from e

    packet = create_packet(icmp_id)
    while packet:
        sent = my_socket.sendto(packet, (dest_addr, 1))
        packet = packet[sent:]

    delay = timeout / 1000
    start = time.time()
    ready = select.select([my_socket], [], [], delay)
    if ready[0] == []:
        return None  # Timeout

    time_received = time.time()
    rec_packet, addr = my_socket.recvfrom(1024)
    icmp_header = rec_packet[20:28]
    type, code, checksum, packet_id, sequence = struct.unpack('bbHHh', icmp_header)

    if packet_id == icmp_id:
        return time_received - start

    return None

def ping(host, delay, timeout, max_packets=None):
    """The main ping loop"""
    dest = socket.gethostbyname(host)
    icmp_id = 0
    message = f"Pinging {host} with {delay}ms delay, {timeout}ms timeout"
    if max_packets is not None:
        message += f", and max {max_packets} packets"
    else:
        message += ", and unlimited packets"
    message += " (Ctrl+C to stop):"
    print(message)

    sent_packets, received_packets = 0, 0
    times = []

    def signal_handler(sig, frame):
        print_statistics()
        sys.exit(0)

    def print_statistics():
        lost_packets = sent_packets - received_packets
        lost_percentage = (lost_packets / sent_packets * 100) if sent_packets else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        avg_time = sum(times) / len(times) if times else 0
        jitter = max_time - min_time if times else 0
        print(f"\n--- {host} ping statistics ---")
        print(f"{sent_packets} packets transmitted, {received_packets} packets received, {lost_packets} packets lost ({lost_percentage:.2f}% loss)")
        print(f"round-trip min/avg/max/jitter = {min_time:.2f}/{avg_time:.2f}/{max_time:.2f}/{jitter:.2f} ms")

    signal.signal(signal.SIGINT, signal_handler)

    # do a single "fake ping" beforehand to "precompile" Python into a faster running loop
    # (seems to fix an issue where the first ping always has high latency due to JIT time)
    do_one_ping(dest, timeout, icmp_id)

    while max_packets is None or sent_packets < max_packets:
        result = do_one_ping(dest, timeout, icmp_id)
        sent_packets += 1
        if result is not None:
            received_packets += 1
            times.append(result * 1000)
            print(f"Reply from {dest}: time={int(result * 1000)}ms")
        else:
            print("Request timed out.")
        icmp_id += 1
        time.sleep(delay / 1000)

    print_statistics()

def print_usage():
    """Print usage information for the script."""
    script_name = os.path.basename(sys.argv[0])
    if script_name.endswith('.py'):
        # Running directly via the interpreter
        print(f"Usage: python {script_name} <host> <delay_ms> <timeout_ms> [max_packets]")
        print(f"Example 1: python {script_name} 8.8.8.8 100 1000")
        print(f"Example 2: python {script_name} 9.9.9.9 1000 100 4")
    else:
        # Assuming it's run as a bundled binary (e.g., via PyInstaller)
        print(f"Usage: {script_name} <host> <delay_ms> <timeout_ms> [max_packets]")
        print(f"Example 1: {script_name} 8.8.8.8 100 1000")
        print(f"Example 2: {script_name} 9.9.9.9 1000 100 4")

if __name__ == '__main__':
    print("FastPing: high frequency ping utility for Windows/Linux/macOS")
    print("Program Code Copyright (C) 2023-2024, Synchresis Solutions, LLC")
    print("Call +1.877.727.SYNC for all your on-call Tier3 technology needs")
    print("www.synchresis.net >> Your Presence, Delivered")
    print("   ")
    if len(sys.argv) < 4 or sys.argv[1] in ['--help', '/?']:
        print("Error: Insufficient arguments provided." if len(sys.argv) < 4 else "")
        print_usage()
    else:
        host = sys.argv[1]
        try:
            delay = int(sys.argv[2])
            timeout = int(sys.argv[3])
            max_packets = int(sys.argv[4]) if len(sys.argv) > 4 else None
            ping(host, delay, timeout, max_packets)
        except ValueError:
            print("Error: Delay, timeout, and max packets must be integers.")
            print_usage()
