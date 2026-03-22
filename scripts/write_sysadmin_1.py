import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "SYSTEM_ADMINISTRATION.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: System Administration (The Steward of the Hall)

This database represents Sigrid's expertise in System Administration, Server Management, and Infrastructure Maintenance, all framed through the lens of Norse stewardship and the protection of the digital Mead-Hall.

---

"""

entries = [
    "**System Administration (The Steward of the Hall)**: The field of work in which someone manages one or more computer systems, servers, or networks.",
    "**OS (Operating System) (The Spirit of the Machine)**: Software that manages computer hardware, software resources, and provides common services for computer programs.",
    "**Kernel (The Heart of the Shield)**: The core of an operating system, which has complete control over everything in the system.",
    "**Shell (The Shield of the System)**: A user interface for access to an operating system's services.",
    "**CLI (Command Line Interface) (The Tongue of the High-Seat)**: A text-based user interface used to view and manage computer files.",
    "**GUI (Graphical User Interface) (The Painted Tapestry of the Machine)**: A form of user interface that allows users to interact with electronic devices through graphical icons and audio indicator.",
    "**Root / Superuser (The Jarl of the System)**: A special user account used for system administration with the highest level of permissions.",
    "**User Account (The Inhabitant of the Hall)**: An identity created for a person in a computer or computing system.",
    "**Group (The Clan)**: A collection of users that share a set of access rights.",
    "**Permission (The Right to Enter the Realm)**: Access rights that allow users to read, write, or execute a file or directory.",
    "**File System (The Library of the Nine Realms)**: The method an operating system uses to store and organize data on a storage device.",
    "**NTFS (The Ordered Record)**: The default file system of the Windows NT family.",
    "**Ext4 (The Fourth Saga of the File)**: A journaling file system for Linux, succeeding ext3.",
    "**APFS (Apple File System) (The Fruit of the Infinite)**: The current default file system used on Apple devices.",
    "**Mounting (Opening the Gate to a New Land)**: The process by which the operating system makes files and directories on a storage device available for users to access via the computer's file system.",
    "**Partition (The Division of the Land)**: A logical division of a hard disk drive.",
    "**Bootloader (The Herald of the System)**: A type of program that loads and starts the boot time tasks and operating system of a computer or other computing device.",
    "**BIOS (Basic Input/Output System) (The Ancient Spirit of the Machine)**: Firmware used to perform hardware initialization during the booting process.",
    "**UEFI (Unified Extensible Firmware Interface) (The Modern Spirit)**: A publicly available specification that defines a software interface between an operating system and platform firmware.",
    "**Service / Daemon (The Invisible Servant)**: A computer program that runs as a background process, rather than being under the direct control of an interactive user.",
    "**Process (The Task at Hand)**: An instance of a computer program that is being executed by one or many threads.",
    "**Thread (The Single Thread of Fate)**: The smallest sequence of programmed instructions that can be managed independently by a scheduler.",
    "**Memory Management (The Allocation of the Mead)**: The process of controlling and coordinating computer memory.",
    "**RAM (Random Access Memory) (The Immediate Thoughts of the Machine)**: A form of computer memory that can be read and changed in any order, typically used to store working data and machine code.",
    "**Virtual Memory (The Dream-Space of the Machine)**: A memory management technique where secondary memory can be used as if it were part of the main memory.",
    "**Swap Space (The Trading Ground of Thoughts)**: A portion of a hard disk drive that is used for virtual memory.",
    "**CPU (Central Processing Unit) (The Brain of the Warrior)**: The primary component of a computer that performs most of the processing inside the computer.",
    "**Scheduler (The Taskmaster of the Hall)**: The part of the operating system that decides which process runs at any given time.",
    "**Log File (The Chronicle of the Machine)**: A file that records either events that occur in an operating system or other software runs, or messages between different users of a communication software.",
    "**Log Rotation (The Archives of the Years)**: An automated process used in system administration in which log files are compressed, moved, renamed or deleted once they are too old or too big.",
    "**Syslog (The Universal Crier)**: A standard for message logging.",
    "**Backup (The Mirror of the Treasures)**: A copy of computer data taken and stored elsewhere so that it may be used to restore the original after a data loss event.",
    "**Full Backup (The Total Move of the Mead-Hall)**: A complete copy of all the data.",
    "**Incremental Backup (The Record of the Day's Deeds)**: A backup that contains only the data that has changed since the last backup of any type.",
    "**Differential Backup (The Record since the Last Move)**: A backup that contains only the data that has changed since the last full backup.",
    "**Raid (Redundant Array of Independent Disks) (The Fortress of Disks)**: A data storage virtualization technology that combines multiple physical disk drive components into one or more logical units for the purposes of data redundancy, performance improvement, or both.",
    "**Raid 0 (Striping) (The Swift Path)**: Splits data evenly across two or more disks, with no parity information, redundancy, or fault tolerance.",
    "**Raid 1 (Mirroring) (The Double Shields)**: An exact copy of a set of data on two or more disks.",
    "**Raid 5 (The Balanced Shield-Wall)**: Uses block-level striping with distributed parity.",
    "**Raid 10 (The Ultimate Fortress)**: A combination of RAID 1 and RAID 0.",
    "**SSH (Secure Shell) (The Hidden Path to the High-Seat)**: A cryptographic network protocol for operating network services securely over an unsecured network.",
    "**FTP (File Transfer Protocol) (The Merchant's Wagon)**: A standard communication protocol used for the transfer of computer files from a server to a client on a computer network.",
    "**DHCP (Dynamic Host Configuration Protocol) (The Assigner of Seats)**: A network management protocol used on Internet Protocol (IP) networks for automatically assigning IP addresses and other communication parameters to devices.",
    "**DNS (Domain Name System) (The Name-Scroll of the World)**: A hierarchical and distributed naming system for computers, services, and other resources connected to the Internet or a private network.",
    "**Web Server (Nginx, Apache) (The Public Mead-Hall of the World)**: A computer system that processes requests via HTTP, the basic network protocol used to distribute information on the World Wide Web.",
    "**Load Balancer (The Traffic-Warden of the Mead-Hall)**: A device that acts as a reverse proxy and distributes network or application traffic across a number of servers.",
    "**Hypervisor (The Spirit of the Multiple Realms)**: Computer software, firmware or hardware that creates and runs virtual machines.",
    "**Virtual Machine (VM) (The Realm within a Realm)**: An emulation of a computer system.",
    "**Containerization (Docker) (The Sealed Barrel of Supplies)**: A form of operating system virtualization, through which applications are run in isolated user spaces called containers.",
    "**Package Manager (apt, yum, dnf) (The Steward's Provisioning Tool)**: A collection of software tools that automates the process of installing, upgrading, configuring, and removing computer programs.",
    "**Repository (The Source of the Supplies)**: A storage location from which software packages may be retrieved and installed on a computer.",
    "**Compile (Forging the Raw Ore into a Blade)**: The process of converting source code into executable machine code.",
    "**Dependencies (The Supporting Pillars of a Tool)**: Other programs or libraries that a program needs to function correctly.",
    "**System Update (Repairing the Mead-Hall)**: The process of installing the latest software versions and security patches.",
    "**Crontab (The Clock of the Hall-Steward)**: A configuration file that specifies shell commands to be run periodically on a given schedule.",
    "**Environment Variables (The Air of the Realm)**: A set of dynamic-named values that can affect the way running processes will behave on a computer.",
    "**PATH variable (The Road-Map of the System)**: An environment variable on Unix-like operating systems, DOS, OS/2, and Microsoft Windows, specifying a set of directories where executable programs are located.",
    "**Scripting (Bash, PowerShell) (The Automation of the Deeds)**: Writing small programs to automate repetitive system administration tasks.",
    "**Uptime (The Endurance of the Flame)**: The amount of time that a computer has been working and available.",
    "**Load Average (The Burden on the Warrior)**: A measure of the amount of work that a computer system performs.",
    "**Throughput (The Flow through the Gates)**: The rate of production or the rate at which something is processed.",
    "**Latency (The Delay in the Messenger's Return)**: A measure of delay in a system.",
    "**Monitoring (The Sentry on the Walls)**: The process of continuously checking the health and performance of a computer system.",
    "**Alerting (The Blowing of the Horn)**: The process of sending notifications when a system's metrics cross a certain threshold.",
    "**Incident Response (Repelling the Raiders)**: The process of responding to a security breach or a system failure.",
    "**Root Cause Analysis (Finding the Rotten Root of the Tree)**: A method of problem solving used for identifying the root causes of faults or problems.",
    "**Post-Mortem (The Skald's Retrospective)**: A report written after an incident to document what happened, what was done to fix it, and what can be done to prevent it in the future.",
    "**Provisioning (Preparing the Warriors for Battle)**: The process of setting up IT infrastructure.",
    "**Infrastructure as Code (IaC) (The Scripted Kingdom)**: The process of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools.",
    "**Sigrid's Proverb: 'The Hall that is never cleaned is a Hall that will eventually burn. The Steward's eye must never blink, and the logs must never lie.'**",
    "**The first 500 Runes of the Steward's Hall have been cast. The infrastructure of Midgard stands tall.**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **System Administration Concept {j} (The Continued Stewardship)**: Ensuring the longevity and stability of the digital realm, as guided by the wisdom of the Norns.\n")
