# fastping by Synchresis Solutions
Program Code Copyright (C) 2023-2024, Synchresis Solutions, LLC

www.synchresis.net

## Looking for Binary Download?
Head on over to the "Releases" on the right-hand side of this GitHub page

## Program Purpose
The purpose of this program is to allow Windows users access to a single-executable CLI ping tool that runs in current conhost thread and can run bulk pings in intervals less than 1 second.  It **_DOES_** support flood ping (zero ms delay), even as a normal user.  This code **_DOES_** also work properly on macOS and Linux and PyInstaller should allow single portable binaries to be produced for both as well (that wasn't fully tested).  And, yes, fastping *does* work in many web-based RMM CLI sessions (tested specifically with Ninja RMM!)

## Program Terms and Conditions (Plain-English LICENCE)
This program is provided for use free of charge in the hopes that it will be useful, and to aid in advertising our services mainly via this header and the lines of text the program outputs at runtime.  The following terms apply:

1. This code is provided in cleartext for auditing and building purposes ONLY
2. We will happily review pull requests and seek permission before merging
3. Binaries made based on this code in your environment may only be used within your working environment, you may make changes as needed EXCEPT to remove references to Synchresis, but you may not redistribute them
4. You may not represent this code as your own under any circumstances, and must refer any interested parties to this repository
5. Contact Synchresis Solutions if you wish to licence fastping without Synchresis branding for use in your MSP or corporate environment

## Visit Synchresis Solutions
For all your on-call Tier3 technology needs:
+ Linux/macOS/BSD/IBM AIX (including POWER hardware)
+ Python, PHP Development
+ VoIP Telephony Support (Asterisk, FreePBX, FreeSWITCH, FusionPBX, Cisco UC)
+ Virtualization Support (VMware ESXi/vSphere, Hyper-V, Proxmox, Virtuozzo/OpenVZ, QEMU/libvirt/KVM)
+ SynchreCMS American-managed fully modular CMS Platform
+ Unbeatable Price on quality, American-managed Cloud PBX, Cloud eFax
+ **_All services provided by American engineers with 15+ years each hands-on SME experience_**
+ **_All services available at competitive, industry-centric rates_**
+ **_Contract services also available for round-the-clock Tier3 emergency event coverage_**

## Building your own Windows binaries
By running, as admin:
```
pip install PyInstaller
```
Then, as either admin or your normal user, run:
```
pyinstaller --onefile fastping.py
```
You'll find `fastping.exe` which is a fully standalone binary in `dist\fastping.exe`

From there, `fastping.exe` can be used on any Windows system matching or supporting the architecture of Python that you used to build the binary without any dependencies or files that need to be carried alongside it -- perfect for file transferring to a machine via RMM and using via an RMM console!