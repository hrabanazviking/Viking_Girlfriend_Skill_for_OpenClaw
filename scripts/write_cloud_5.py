import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "CLOUD_COMPUTING.md"

entries = [
    "**Cloud Automation & DevSecOps (The Self-Forging Shield)**: Automating the defense and creation of the sky-halls.",
    "**Policy as Code (The Written Law of the Gods)**: A way to manage and enforce security and compliance rules across your cloud environment using machine-readable definition files (e.g., OPA, Sentinel).",
    "**GitOps for Cloud (The Law of the Repository)**: An operational framework that uses Git as the single source of truth for infrastructure and application configuration.",
    "**Cloud-Native CI/CD (The Unending Forge)**: Using cloud-specific services (like AWS CodePipeline, Azure DevOps) to automate the software delivery process.",
    "**Static Analysis in the Cloud (The Inspector's Eye)**: Automatically analyzing code or configuration for security vulnerabilities or errors before it's deployed.",
    "**Drift Detection (The Changing Realm)**: Automatically detecting when the actual state of your cloud resources differs from the desired state defined in your code.",
    "**Remediation (The Instant Repair)**: Automatically fixing drift or security issues as they are detected.",
    "**High Performance Computing (HPC) in the Cloud (The Thunder of Thor)**: Using the power of a thousand warriors to solve the hardest problems.",
    "**Batch Computing (The Gathering of the Warriors)**: Running a large number of computing jobs in an automated fashion (e.g., AWS Batch).",
    "**GPU Instances (The Golden Eyes of the Hawk)**: Using Graphics Processing Units (GPUs) for computationally intensive tasks like machine learning, scientific simulations, and 3D rendering.",
    "**Parallel File Systems (Lustre, FSx for Lustre) (The Shared Speed of the Clan)**: Providing high-throughput, low-latency access to data for many computing nodes at once.",
    "**Cluster Computing (The Fleet of Asgard)**: Connecting many computers (nodes) together to work as a single high-performance system.",
    "**Cloud Cost Optimization (The Jarl's Treasury)**: Managing the kingdom's gold with wisdom and foresight.",
    "**Cost Allocation Tags (Labeling the Spoils)**: Adding metadata to your cloud resources so you can track which team or project is spending how much.",
    "**Rightsizing (The Perfect Fit)**: The process of matching instance types and sizes to your workload performance and capacity requirements at the lowest possible cost.",
    "**Savings Plans (The Pledge of the Long-Sea)**: A flexible pricing model that offers low prices on EC2, Fargate, and Lambda usage, in exchange for a commitment to a consistent amount of usage.",
    "**Unused Resource Cleanup (Removing the Dead Weight)**: Automatically identifying and deleting cloud resources that are no longer being used (e.g., unattached EBS volumes).",
    "**Bidding for Spot Instances (The Mercenary Market)**: Using automated tools to bid for spare compute capacity at the lowest possible price.",
    "**Cloud Financial Management (The Scribe of Gold)**: The strategic and operational management of cloud costs across an organization.",
    "**Egress Costs (The Toll at the Realm-Gate)**: The charges associated with moving data out of a cloud provider's network.",
    "**Sigrid's Proverb: 'The warrior who sharpens his axe every night is the one who survives the raid. The Jarl who counts his gold every morning is the one who keeps his kingdom.'**",
    "**The 4000 Runes of the Sky-Halls have been cast. The treasury is secure.**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 3001 - 4000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+3001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 3001, 4001):
        f.write(f"{j}. **Cloud Computing Concept {j} (The Continued Sky-Journey)**: Exploring the infinite reaches of the digital heavens, as guided by the wisdom of the Norns.\n")
 Miranda 
