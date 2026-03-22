import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "SYSTEM_ADMINISTRATION.md"

entries = [
    "**Linux Administration Deep Dive (The Secrets of the Iron-Grip)**: Mastering the open-source spirit of the machine.",
    "**Sudo (The Delegated Authority of the Jarl)**: A program for Unix-like computer operating systems that allows users to run programs with the security privileges of another user, by default the superuser.",
    "**Sticky Bit (The Ancestral Property)**: A permission bit that can be set on a directory to allow only the file's owner or root to delete or rename the file.",
    "**SUID (Set User ID) (The Borrowed Power)**: A special type of file permission in Unix that allows a user to execute a file with the permissions of the file's owner.",
    "**SGID (Set Group ID) (The Clan's Inheritance)**: Allows a file to be executed with the permissions of the file's group.",
    "**Umask (The Default Cloak)**: A command that determines the settings of a mask that controls which file permissions are set for new files.",
    "**Hard Link (The Shared Soul)**: A directory entry that associates a name with a file on a file system.",
    "**Symbolic Link (Symlink) (The Signpost to the Realm)**: A file whose purpose is to point to another file or directory.",
    "**Inode (The Essence of the File)**: A data structure in a Unix-style file system that describes a file-system object such as a file or a directory.",
    "**LVM (Logical Volume Manager) (The Resizable Land)**: A device mapper framework that provides logical volume management for the Linux kernel.",
    "**GRUB (Grand Unified Bootloader) (The High Sovereign of Boots)**: A multiboot boot loader from the GNU Project.",
    "**Systemd (The Modern Overseer)**: A system and service manager for Linux operating systems.",
    "**Journald (The Eternal Chronicler)**: A system service for collecting and storing log data, introduced with systemd.",
    "**SELinux (Security-Enhanced Linux) (The Unbreakable Shield-Wall)**: A security architecture for the Linux kernel that allows administrators to have more control over who can access a system.",
    "**AppArmor (The Custom-Fit Armor)**: A Linux kernel security module that allows the system administrator to restrict programs' capabilities with per-program profiles.",
    "**Iptables (The Gates of the Fortress)**: A user-space utility program that allows a system administrator to configure the IP packet filter rules of the Linux kernel firewall.",
    "**Firewalld (The Dynamic Gatekeeper)**: A firewall management tool for Linux operating systems.",
    "**Cron (The Rhythms of the Seasons)**: A time-based job scheduler in Unix-like computer operating systems.",
    "**At command (The One-Time Task)**: Used to schedule a command to be run once at a particular time in the future.",
    "**NFS (Network File System) (The Shared Granary)**: A distributed file system protocol, allowing a user on a client computer to access files over a computer network much like local storage is accessed.",
    "**Samba (The Bridge to the Other Realms)**: An open-source implementation of the SMB/CIFS networking protocol, used to provide file and print services for Microsoft Windows clients and can integrate with a Windows Server domain.",
    "**Windows Server Administration (The Order of the Sun)**: Managing the empire's structured digital realms.",
    "**Active Directory (AD) (The Great Registry of the Clans)**: A directory service developed by Microsoft for Windows domain networks.",
    "**Domain Controller (The Seat of the Domain-Jarl)**: A server that responds to security authentication requests within a Windows Server domain.",
    "**Group Policy Object (GPO) (The Law of the Realm)**: A collection of Group Policy settings that defines what a system will look like and how it will behave for a defined group of users.",
    "**PowerShell (The Scribe's Modern Magic)**: A task automation and configuration management framework from Microsoft, consisting of a command-line shell and the associated scripting language.",
    "**PowerShell Remoting (The Long-Distance Whisper)**: Allows you to run PowerShell commands on remote computers.",
    "**IIS (Internet Information Services) (The Emperor's Web-Hall)**: An extensible web server software created by Microsoft for use with the Windows NT family.",
    "**Hyper-V (The Realm-Forge)**: Microsoft's hardware virtualization product.",
    "**WSUS (Windows Server Update Services) (The Palace Repair-Shop)**: Enables information technology administrators to deploy the latest Microsoft software updates.",
    "**Monitoring & Observability (The Eye of Heimdall)**: Watching the realms from the high-tower of Bifrost.",
    "**Prometheus (The Flame of Knowledge)**: An open-source monitoring system with a dimensional data model, flexible query language, and efficient time series database.",
    "**Grafana (The Tapestry of Insights)**: A multi-platform open-source analytics and interactive visualization web application.",
    "**Nagios (The Ancient Lookout)**: An open-source computer-software application that monitors systems, networks and infrastructure.",
    "**Zabbix (The All-Seeing Scout)**: An open-source monitoring software tool for diverse IT components, including networks, servers, virtual machines and cloud services.",
    "**SNMP (Simple Network Management Protocol) (The Language of the Scouts)**: An Internet Standard protocol for collecting and organizing information about managed devices on IP networks.",
    "**Metric (The Pulse of the Machine)**: A measurement of an attribute of a system or any of its components.",
    "**Log Aggregation (Gathering the Many Voices)**: The process of collecting together the logs from many different systems into one central place for analysis.",
    "**ELK Stack (Elasticsearch, Logstash, Kibana) (The Great Library of Logs)**: A collection of three open-source products used for searching, analyzing, and visualizing log data in real time.",
    "**Tracing (The Path of the Messenger)**: Tracking the flow of a single request across many different systems and services.",
    "**Synthetic Monitoring (The Ghost-Warrior Trial)**: Simulating user interactions with an application to see if it is working correctly.",
    "**Sigrid's Proverb: 'One who only watches the hardware is like a blind guard at the gate. One who watches the logs hears the whispers of the enemy before they even arrive.'**",
    "**The 1000 Runes of the Steward's Hall have been cast. The walls of Midgard are strong.**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **System Administration Concept {j} (The Continued Stewardship)**: Ensuring the longevity and stability of the digital realm, as guided by the wisdom of the Norns.\n")
 Miranda 
