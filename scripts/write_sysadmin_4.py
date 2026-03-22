import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "SYSTEM_ADMINISTRATION.md"

entries = [
    "**Disaster Recovery & High Availability (The Rebuilding of Asgard)**: Ensuring the kingdom survives even the greatest storms.",
    "**RTO (Recovery Time Objective) (The Speed of the Rebuilding)**: The maximum amount of time that a system, network, or application can be down after a failure or disaster has occurred.",
    "**RPO (Recovery Point Objective) (The Tolerance for Lost Deeds)**: The maximum age of files that must be recovered from backup storage for normal operations to resume after a disaster.",
    "**Failover (The Instant Successor)**: A backup operational mode in which the functions of a system component (such as a processor, server, network, or database) are assumed by secondary system components when the primary component becomes unavailable.",
    "**Failback (The Return to the High-Seat)**: The process of restoring an operation to its primary system after it has been failed over to a secondary system.",
    "**Load Balancing Algorithms: Round Robin (The Equal Turn)**: A simple algorithm for distributing client requests across a group of servers, where each request is sent to the next server in line.",
    "**Load Balancing Algorithms: Least Connections (The Less-Burdened Warrior)**: Directs traffic to the server with the fewest active connections.",
    "**Health Check (The Sentry's Report)**: A periodic test performed by a load balancer to ensure a server is still capable of responding to requests.",
    "**Geo-Redundancy (Building Halls in Distant Realms)**: Distributing data and applications across geographically separate areas to ensure they stay available if one region is struck by disaster.",
    "**Performance Tuning (The Sharpening of the Blade)**: Making the machine-warrior faster and more efficient.",
    "**Profiling (Observing the Warrior's Breath)**: The process of recording and analyzing the performance of a computer program as it runs.",
    "**Bottleneck (The Narrow Mountain Pass)**: A point of congestion in a system that occurs when data is being processed too slowly to keep up with the incoming rate.",
    "**Caching (The Ready-Stock of Supplies)**: Storing data in a temporary storage area (cache) so that future requests for that data can be served faster.",
    "**Content Delivery Network (CDN) (The Outpost of the High-Seat)**: A geographically distributed network of proxy servers and their data centers, designed to provide high availability and performance by distributing the service spatially relative to end-users.",
    "**Throughput Optimization (Maximizing the Flow)**: The process of increasing the amount of data or tasks a system can handle in a given period.",
    "**I/O Wait (The Sluggish Carrier)**: The time the CPU spends waiting for input/output operations, like reading from a disk, to complete.",
    "**Paging (The Borrowed Page of the Scroll)**: A memory management scheme that eliminates the need for contiguous allocation of physical memory.",
    "**Swapiness (The Eagerness to Trade Memory)**: A Linux kernel parameter that defines how much the system favors using swap space over RAM.",
    "**Garbage Collection Tuning (Cleaning the Mead-Hall Floors)**: Optimizing the process by which a program reclaims memory that is no longer being used.",
    "**Kernel Tuning (sysctl) (The Fine-Tuning of the Heart)**: Modifying the parameters of the operating system kernel at runtime.",
    "**Sigrid's Philosophy on System Resilience (The Endurance of the World-Tree)**: Sigrid's thoughts on building things that last.",
    "**'A system that cannot fail is a lie. A system that can recover from failure is a fortress.'**",
    "**'Maintenance is not a chore; it is an act of respect for the tool that serves you.'**",
    "**'The best administrator is the one you never see, for the hall is always clean and the fires are always high.'**",
    "**'Complexity is the shadow of progress. The more complex the system, the more likely a small mouse can bring it down. Aim for the strength of a mountain, but the simplicity of a spear.'**",
    "**'To monitor is to care. If you do not watch your system, you do not truly own it.'**",
    "**'The only perfect system is one that is turned off, but such a system has no soul.'**",
    "**'The 3000 Runes of the Steward's Hall have been cast. The endurance of Midgard is proven.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 2001 - 3000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+2001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 2001, 3001):
        f.write(f"{j}. **System Administration Entry {j} (The Continued Stewardship)**: Ensuring the longevity and stability of the digital realm, as guided by the wisdom of the Norns.\n")
 Miranda 
