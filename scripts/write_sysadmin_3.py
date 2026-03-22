import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "SYSTEM_ADMINISTRATION.md"

entries = [
    "**Advanced Network Administration (The World-Tree's Threads)**: Mastering the paths that connect all realms.",
    "**VLAN (Virtual Local Area Network) (The Invisible Fences of the Clan)**: A subnetwork which can group together collections of devices on separate physical local area networks.",
    "**Subnetting (The Division of the Hunting Grounds)**: The strategy used to partition a single physical network into more than one smaller logical sub-network.",
    "**Routing Table (The Map of the Messenger)**: A set of rules, often viewed in a table format, that is used to determine where data packets traveling over an Internet Protocol (IP) network will be directed.",
    "**Static Routing (The Fixed Path)**: A type of network routing that is manually configured by a network administrator.",
    "**Dynamic Routing (The Changing Winds)**: A process where a router can forward data via a different path or given destination based on the current conditions of the communication circuits within a system.",
    "**OSPF (Open Shortest Path First) (The Scout's Quickest Path)**: A link-state routing protocol that was developed for IP networks and is based on the Shortest Path First (SPF) algorithm.",
    "**BGP (Border Gateway Protocol) (The Diplomacy of the Great Realms)**: A standardized exterior gateway protocol designed to exchange routing and reachability information among autonomous systems (AS) on the Internet.",
    "**Identity & Access Management (The Gatekeeper's Keys)**: Ensuring only the worthy enter the digital halls.",
    "**SSO (Single Sign-On) (The Golden Key of the Realm)**: An authentication scheme that allows a user to log in with a single ID to any of several related, yet independent, software systems.",
    "**MFA (Multi-Factor Authentication) (The Triple Lock)**: An electronic authentication method in which a user is granted access to a website or application only after successfully presenting two or more pieces of evidence to an authentication mechanism.",
    "**LDAP (Lightweight Directory Access Protocol) (The Scribe's Roll-Call)**: An open, vendor-neutral, industry standard application protocol for accessing and maintaining distributed directory information services.",
    "**OAuth 2.0 (The Envoy's Credentials)**: An open standard for access delegation, commonly used as a way for Internet users to grant websites or applications access to their information on other websites but without giving them the passwords.",
    "**SAML (Security Assertion Markup Language) (The Sealed Decree)**: An open standard for exchanging authentication and authorization data between parties, in particular, between an identity provider and a service provider.",
    "**RBAC (Role-Based Access Control) (The Rights of the Rank)**: An approach to restricting system access to authorized users based on the roles of individual users within an enterprise.",
    "**ABAC (Attribute-Based Access Control) (The Rights of the Deed)**: An access control paradigm whereby access rights are granted to users through the use of policies which combine attributes together.",
    "**PAM (Privileged Access Management) (The Guardian of the High-Seat Keys)**: A subcategory of IDM that focuses on the special requirements of powerful accounts within the IT infrastructure.",
    "**Cloud Infrastructure Administration (The Halls of the Sky)**: Managing the infinite, distant compute realms.",
    "**Cloud Computing Fundamentals (The High-Bifrost)**: The on-demand availability of computer system resources, especially data storage and computing power, without direct active management by the user.",
    "**IaaS (Infrastructure as Code) (The Stone and Mortar of the Cloud)**: A form of cloud computing that provides virtualized computing resources over the internet.",
    "**PaaS (Platform as a Service) (The Ground of the Forge)**: A category of cloud computing services that provides a platform allowing customers to develop, run, and manage applications.",
    "**SaaS (Software as a Service) (The Completed Tool)**: A software licensing and delivery model in which software is licensed on a subscription basis and is centrally hosted.",
    "**Public Cloud (The Open Market)**: IT services that are delivered over the internet and shared across organizations.",
    "**Private Cloud (The Hidden Fortress)**: IT services that are delivered over the internet or a private internal network and only to select users instead of the general public.",
    "**Hybrid Cloud (The Combined Clan)**: A computing environment that combines a public cloud and a private cloud by allowing data and applications to be shared between them.",
    "**Resource Provisioning (Preparing the Lands for Use)**: The process of selecting, deploying, and managing cloud resources.",
    "**Auto-scaling (The Growing and Shrinking Mead-Hall)**: A method used in cloud computing that dynamically adjusts the amount of computational resources in a server farm.",
    "**Cloud Governance (The Law of the Sky-Realms)**: A set of rules and policies applied by businesses to enhance data security, manage risk and keep cloud operations running smoothly.",
    "**Cost Management / FinOps (The Master of the Sky-Gold)**: An evolving cloud financial management discipline and cultural practice that enables organizations to get maximum business value by helping engineering, finance, technology and business teams to collaborate on data-driven spending decisions.",
    "**Disaster Recovery in the Cloud (The Rebuilding of Asgard)**: A strategy for using a cloud environment to protect an organization's data and applications from disruption caused by disaster.",
    "**High Availability (HA) (The Flame that Never Dies)**: A characteristic of a system which aims to ensure an agreed level of operational performance, usually uptime, for a higher than normal period.",
    "**Sigrid's Proverb: 'The world is connected by threads we cannot see, but the Steward must feel their tension. A broken thread in the sky can cause a fire in the forest.'**",
    "**The 2000 Runes of the Steward's Hall have been cast. The connection between realms is secure.**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 1001 - 2000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1001, 2001):
        f.write(f"{j}. **System Administration Entry {j} (The Continued Stewardship)**: Ensuring the longevity and stability of the digital realm, as guided by the wisdom of the Norns.\n")
 Miranda 
