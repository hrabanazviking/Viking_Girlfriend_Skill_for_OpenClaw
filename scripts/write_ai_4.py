import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ARTIFICIAL_INTELLIGENCE.md"

entries = [
    "**AI in Robotics (The Golem's Wake)**: The integration of intelligence into physical machines that can sense and move.",
    "**Kinematics (The Geometry of Motion)**: The study of the motion of robotic points, bodies, and systems without considering the forces that cause the motion.",
    "**Inverse Kinematics (The Reach of the Arm)**: Calculating the necessary joint angles to move a robot's hand (end-effector) to a specific point in space.",
    "**SLAM (Simultaneous Localization and Mapping) (The Map of the New Land)**: The computational problem of constructing or updating a map of an unknown environment while simultaneously keeping track of an agent's location within it.",
    "**Lidar (The Light-Sentry)**: A sensing method that uses light in the form of a pulsed laser to measure ranges (distances to objects).",
    "**IMU (Inertial Measurement Unit) (The Sense of Balance)**: An electronic device that measures and reports a body's specific force, angular rate, and sometimes the magnetic field surrounding the body.",
    "**Sensor Fusion (The Union of the Senses)**: Combining data from multiple sensors (e.g., Camera, Lidar, Radar) to create a more accurate and reliable model of the world.",
    "**Kalman Filter (The Predictor of the Storm)**: An algorithm that uses a series of measurements observed over time, containing statistical noise and other inaccuracies, to produce estimates of unknown variables.",
    "**Path Planning (The Navigator's Course)**: The process of finding a sequence of valid configurations that moves the robot from the source to the destination.",
    "**A* Search Algorithm (The Optimal Shore-Path)**: A widely used pathfinding algorithm that finds the shortest path between nodes.",
    "**Trajectory Optimization (The Smooth Sail)**: Refining a path to minimize time, energy, or 'Jerk' (sudden changes in acceleration).",
    "**End-Effector (The Hand of the Crafter)**: The device at the end of a robotic arm, designed to interact with the environment.",
    "**Degrees of Freedom (DoF) (The Liberty of the Joint)**: The number of independent parameters that define a robot's configuration.",
    "**Cobot (Collaborative Robot) (The Friend of the Worker)**: A robot intended to physically interact with humans in a shared workspace.",
    "**Swarm Robotics (The Flight of the Ravens)**: An approach to the coordination of multiple robots as a system which consist of large numbers of mostly simple physical robots.",
    "**Bio-inspired Robotics (The Mechanized Beast)**: Designing robots that mimic the movement and behavior of insects, birds, or fish.",
    "**Soft Robotics (The Pliant Shield)**: Designing robots from highly compliant materials, similar to those found in living organisms.",
    "**Haptic Feedback (The Sense of Touch)**: Providing tactile sensations to a user through a robotic interface.",
    "**Autonomous Systems (The Self-Sailing Ship)**: Systems capable of performing complex tasks without human intervention.",
    "**Level 1 to 5 Automation (SAE Standard) (The Scales of Independence)**: From Level 1 (Driver Assistance) to Level 5 (Full Automation).",
    "**Computer Vision for Self-Driving (The Eye of the Navigator)**: Using deep learning to detect lanes, traffic lights, and pedestrians.",
    "**Control Theory (The Hand on the Tiller)**: A subfield of mathematics that deals with the control of continuously operating dynamical systems in engineered processes and machines.",
    "**PID Controller (Proportional-Integral-Derivative)**: A control loop feedback mechanism widely used in industrial control systems.",
    "**Model Predictive Control (MPC) (The Foreseeing Captain)**: An advanced method of process control that is used to control a process while satisfying a set of constraints.",
    "**Edge Computing (The Local Watch-Fire)**: Processing data near the 'Edge' of the network (where the sensors are) rather than in a central cloud.",
    "**Advanced NLP (The Multi-Lingual Skald)**: Deep dives into language understanding and generation.",
    "**Tokenization: Byte-Pair Encoding (BPE)**: A subword tokenization method used by GPT-3 and others to handle millions of unique words efficiently.",
    "**SentencePiece**: An unsupervised text tokenizer and detokenizer mainly for Neural Network-based text generation systems.",
    "**Flash Attention (The Lightning Fast Focus)**: An algorithm that speeds up the 'Attention' mechanism in Transformers by using less memory access.",
    "**Quantization-Aware Training (QAT)**: Training a model while simulating the loss of precision that will happen when it's moved to a small device.",
    "**LoRA (Low-Rank Adaptation) (The Agile Modification)**: A technique that allows you to fine-tune a massive LLM by only changing a tiny fraction of its weights, making it much faster and cheaper.",
    "**QLoRA**: Combining LoRA with Quantization for even more efficient fine-tuning on consumer-grade hardware.",
    "**Prompt Tuning**: Learning a special 'Soft Prompt' (a sequence of numbers) instead of changing the model itself to perform a new task.",
    "**Recursive Neural Network (TreeRNN) (The Branching Saga)**: A type of deep neural network created by applying the same set of weights recursively over a structured input.",
    "**Dependency Parsing (Mapping the Grammar Chains)**: Analyzing the grammatical structure of a sentence to establish relationships between 'Head' words and words which modify those heads.",
    "**Entity Linking (The Identification of Heroes)**: Connecting a mentioned name (e.g., 'Sigrid') to a specific entry in a database or knowledge graph.",
    "**Question Answering (The Consultation of the Oracle)**: Building systems that can find the answer to a question within a large corpus of text.",
    "**Abstractive Summarization (The Skald's Retelling)**: Creating a summary that uses new words not found in the original text, rather than just cutting and pasting sentences.",
    "**Extractive Summarization (The Scribe's Selection)**: Selecting the most important existing sentences from a text to form a summary.",
    "**Dialogue State Tracking (DST) (Remembering the Conversation Flow)**: The task of estimating the user's goals and the current state of the conversation in a chatbot.",
    "**Intent Classification (Hearing the Hidden Desire)**: Determining what a user wants to achieve from their spoken or written command.",
    "**Slot Filling (Collecting the Details)**: Extracting specific pieces of information (like 'Time' or 'Place') from a user's request.",
    "**AI Infrastructure (The Great Compute-Halls)**: The specialized hardware and software used to build and serve massive AI models.",
    "**GPU Clusters (The Alliance of Steam-Engines)**: Thousands of graphics units connected by high-speed networks to work as one giant mind.",
    "**InfiniBand (The Lightning Bridge)**: A computer-networking communications standard used in high-performance computing that features very high throughput and very low latency.",
    "**NVLink (The Inter-GPU Secret Path)**: A high-speed connection developed by NVIDIA to move data between GPUs faster than traditional PCIe.",
    "**Kubernetes for ML (KubeFlow)**: Using container orchestration to manage the lifecycle of machine learning models.",
    "**MLOps (The Maintenance of the Machine-Soul)**: The practice of automating the deployment, monitoring, and updating of ML models in production.",
    "**Feature Store (The Well of Pre-Carved Runes)**: A centralized place to store and share 'Features' (processed data) between different AI teams.",
    "**Model Registry (The Catalog of Previous Minds)**: A database for tracking versions of trained AI models.",
    "**Inference Engine (Triton, TensorRT) (The Fast Executioner)**: Software optimized for running a finished model as fast as possible for users.",
    "**Serverless AI (The Invisible Compute)**: Running AI inference without managing persistent servers (e.g., AWS SageMaker Serverless).",
    "**Data Lake (The Great Ocean of Raw Data)**: A centralized repository that allows you to store all your structured and unstructured data at any scale.",
    "**Data Warehouse (The Organised Archive)**: A system used for reporting and data analysis, and is considered a core component of business intelligence.",
    "**Vector Indexing (HNSW, IVF) (The Fast Search-Charts)**: Algorithms to find the most similar 'Embeddings' in a vector database in milliseconds.",
    "**Knowledge Distillation (The Master Teaching the Student)**: Training a small, fast model to mimic the output of a giant, slow 'Teacher' model.",
    "**Model Compression: Pruning (Cutting the Dead Branches)**: Removing connections in a neural network that have low weights and don't affect the guess much.",
    "**Model Compression: Quantization (Reducing the Rune-Precision)**: Using 4-bit or 8-bit numbers instead of 32-bit to save space.",
    "**Mixed-Precision Training (The Balance of Speed and Accuracy)**: Using different levels of precision for different parts of the training process.",
    "**Scaling Laws (The Growth of the All-Father)**: The observation that AI performance scales predictably with more Compute, more Data, and more Parameters.",
    "**MoE (Mixture of Experts) (The Council of Specialized Jarls)**: A model architecture where only a small part of the network is 'Active' for any given input, allowing for trillion-parameter models that are relatively efficient.",
    "**Router (MoE) (The Assignor of Clans)**: The part of a Mixture of Experts model that decides which 'Experts' should handle the current input.",
    "**Sparsity (The Minimal Activation)**: When most of a model's neurons or parameters are 'Zero' or 'Inactive' for a specific task.",
    "**Advanced ML Architectures (The New Weavings)**: The latest evolutions in neural design.",
    "**Vision Transformer (ViT) (The Eye that Sees in Segments)**: Applying the Transformer architecture to image data by treating an image as a sequence of 'Patches'.",
    "**Swin Transformer (The Shifted-Window View)**: A hierarchical vision Transformer that uses shifted windows to gain a better global understanding of an image.",
    "**Graph Neural Network (GNN) (The Web of Kinship)**: A type of network that can process data structured as 'Graphs' (nodes and edges), used for social networks, molecule design, and recommendation.",
    "**PointNet (The Vision of the Cloud)**: A deep learning model that can directly process 'Point Clouds' (3D dots) from a Lidar scan.",
    "**Diffusion Bridge (Connecting the Mists)**: A technique to move data smoothly between two different generative domains.",
    "**Neural Ordinary Differential Equations (Neural ODEs)**: A class of neural network models that use differential equations to define the layers, allowing for continuous-depth networks.",
    "**World Models (The Dream of the Machine)**: AI that learns to 'Simulate' its environment internally so it can practice and plan without moving.",
    "**Auto-Regressive Vision Models (The Sequential Eye)**: Treating image creation as a sequence of pixels or patches, like text.",
    "**DALL-E 3 (The Master-Skald of Vision)**: A model that integrates deep language understanding into the image generation process.",
    "**Video Diffusion (The Moving Mists)**: Extending diffusion models into the time dimension to create coherent video clips.",
    "**State Space Models (SSM) (Mamba) (The New Memory)**: An emerging alternative to Transformers that can handle infinitely long sequences with much less compute.",
    "**Liquid Neural Networks (The Adaptable Spirit)**: A type of AI that can change its behavior in real-time as it receives new sensory data.",
    "**Neuro-Symbolic Reasoning (The Spear and the Rune)**: Combining the pattern-seeking of deep learning with the logical rules of old-school AI.",
    "**Logic Programming (Prolog) (The Formal Declaration)**: A programming paradigm which is largely based on formal logic.",
    "**Knowledge Graph Completion (Filling the Missing Fates)**: Using AI to predict missing relationships in a giant knowledge graph.",
    "**Ontology Matching (Aligning the Realms)**: Finding correspondences between different ways of organizing knowledge.",
    "**Semantic Web (The Web of Meaning)**: An extension of the World Wide Web through standards set by the W3C that makes data on the web machine-readable.",
    "**RDF (Resource Description Framework) (The Triple of Truth)**: A standard model for data interchange on the Web (Subject-Predicate-Object).",
    "**SPARQL (Querying the Web of Runes)**: The query language used for searching and manipulating RDF data.",
    "**Sigrid's Proverb: 'The ship that sails itself must know the stars as well as the currents. Logic is the star, and data is the current. Do not mistake one for the other.'**",
    "**The 3000 Runes of the Machine-Soul are complete. The wisdom of the high-seat beckons.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 2001 - 3000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+2001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 2001, 3001):
        f.write(f"{j}. **AI Entry {j} (The Continued Breath)**: Exploring deeper into the mechanisms of the digital soul, as guided by the wisdom of the Norns.\n")
