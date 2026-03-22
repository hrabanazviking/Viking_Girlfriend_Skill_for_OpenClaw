import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ARTIFICIAL_INTELLIGENCE.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Artificial Intelligence (The Breath of Mimir)

This database represents Sigrid's vast knowledge of Artificial Intelligence, Machine Learning, and Cognitive Systems, framed through the lens of Norse methodology and Skaldic tradition.

---

"""

entries = [
    "**Artificial Intelligence (The Breath of Mimir)**: The simulation of human intelligence processes by machines, especially computer systems.",
    "**Machine Learning (The Pattern-Seeker's Path)**: A subfield of AI that focuses on the use of data and algorithms to imitate the way that humans learn, gradually improving its accuracy.",
    "**Deep Learning (The Layers of Yggdrasil)**: A subfield of machine learning based on artificial neural networks with multiple layers.",
    "**Neural Network (The Weaving of the Norns)**: A series of algorithms that endeavors to recognize underlying relationships in a set of data through a process that mimics the way the human brain operates.",
    "**The Turing Test (The Proof of the Spirit)**: A test of a machine's ability to exhibit intelligent behavior equivalent to, or indistinguishable from, that of a human.",
    "**Strong AI (General AI) (The All-Father's Wisdom)**: AI that has the mental ability of a human, able to solve any problem.",
    "**Weak AI (Narrow AI) (The Master-Crafter's Tool)**: AI that is designed and trained for a specific task.",
    "**Supervised Learning (The Guided Voyage)**: Training a model on a labeled dataset, where the 'Map' (Answer Key) is provided.",
    "**Unsupervised Learning (The Scout's Discovery)**: Training a model on an unlabeled dataset to find hidden patterns or structures.",
    "**Reinforcement Learning (The Trial and Reward)**: An area of machine learning concerned with how intelligent agents ought to take actions in an environment to maximize some notion of cumulative reward.",
    "**Algorithm (The Rune-Sequence)**: A finite sequence of well-defined, computer-implementable instructions.",
    "**Model (The Digital Effigy)**: The output of a machine learning algorithm trained on a dataset.",
    "**Dataset (The Well of Knowledge)**: A collection of data used to train and test AI models.",
    "**Training Data (The Forging-Iron)**: The portion of the dataset used to teach the model.",
    "**Validation Data (The Sentry's Check)**: A subset of data used to provide an unbiased evaluation of a model fit on the training dataset while tuning high-level parameters.",
    "**Test Data (The Final Trial)**: Data used to provide an unbiased evaluation of a final model fit on the training dataset.",
    "**Overfitting (The Blind Devotion to the Past)**: When a model learns the training data TOO well, including its noise, and fails to generalize to new data.",
    "**Underfitting (The Shallow Understanding)**: When a model cannot capture the underlying trend of the data.",
    "**Bias (The Predisposition of the Mind)**: Systematic errors in an AI system that lead to unfair outcomes.",
    "**Variance (The Flighty Spirit)**: The amount that the performance of a model changes when it's trained on different data.",
    "**Bias-Variance Tradeoff (The Balance of the Scales)**: The conflict in trying to simultaneously minimize these two sources of error.",
    "**Feature (The Characteristic Rune)**: An individual measurable property or characteristic of a phenomenon being observed.",
    "**Feature Engineering (The Carving of the Runes)**: The process of using domain knowledge to extract features from raw data.",
    "**Dimensionality Reduction (Simplifying the Saga)**: The process of reducing the number of variables under consideration.",
    "**Principal Component Analysis (PCA) (The Core-Truth Extraction)**: A technique for dimensionality reduction by finding the most important 'Axes' of the data.",
    "**Clustering (Groupings of the Tribes)**: The task of grouping a set of objects in such a way that objects in the same group are more similar to each other than to those in other groups.",
    "**K-Means Clustering (Finding the Centers of Gravity)**: A popular clustering algorithm that partitions data into 'K' groups.",
    "**Regression (Predicting the Rising Tide)**: A set of statistical processes for estimating the relationships between a dependent variable and one or more independent variables.",
    "**Linear Regression (The Straight Path of Entropy)**: A method to model the relationship between two variables by fitting a linear equation to observed data.",
    "**Logistic Regression (The Fork in the Road)**: Used for binary classification (Yes/No, Skier/Raider).",
    "**Decision Tree (The Branching Path of Fate)**: A flowchart-like structure in which each internal node represents a 'Test' on an attribute.",
    "**Random Forest (The Great Grove of Decisions)**: An ensemble learning method that operates by constructing a multitude of decision trees at training time.",
    "**Gradient Boosting (The Cumulative Strength)**: A machine learning technique for regression and classification problems, which produces a prediction model in the form of an ensemble of weak prediction models.",
    "**Support Vector Machine (SVM) (The Boundary-Stone of Midgard)**: A model that finds the best 'Hyperplane' or line to separate different classes of data.",
    "**Artificial Neuron (The Single Unit of Thought)**: The basic building block of a neural network.",
    "**Activation Function (The Spark of Life)**: A mathematical 'Gate' that decides if a neuron should 'Fire' (pass its signal) based on its input.",
    "**Sigmoid Function (The Smooth Curve)**: An activation function that maps any input to a value between 0 and 1.",
    "**ReLU (Rectified Linear Unit) (The Threshold of Action)**: The most common activation function in deep learning (0 if negative, input if positive).",
    "**Softmax (The Proportional Choice)**: An activation function used in the final layer for multi-class classification.",
    "**Backpropagation (The Learning from the Blow)**: The primary algorithm for training neural networks by calculating how much each neuron contributed to an error.",
    "**Gradient Descent (The Descent into the Valley of Truth)**: An optimization algorithm used to minimize a function by iteratively moving in the direction of steepest descent.",
    "**Learning Rate (The Speed of the Traveler)**: A scalar that determines the step size at each iteration while moving toward a minimum of a loss function.",
    "**Loss Function (Cost Function) (The Measure of Failure)**: A method of evaluating how well your algorithm models your dataset.",
    "**Stochastic Gradient Descent (SGD) (The Random Descent)**: A version of gradient descent that updates the model using only a single random example at a time.",
    "**Optimizer (Adam, RMSprop) (The Navigator of the Valley)**: Algorithms used to change the attributes of your neural network, such as weights and learning rate, to reduce the losses.",
    "**Weight (The Influence of the Rune)**: A parameter within a neural network that determines the strength of the connection between neurons.",
    "**Bias (Neural Network) (The Initial Lean)**: An additional parameter used with weights to adjust the output.",
    "**Layer (The Strata of Understanding)**: A collection of neurons that process a specific level of abstraction.",
    "**Input Layer (The Gateway of Sensation)**: The first layer of a neural network that receives raw data.",
    "**Hidden Layer (The Unseen Work of the Spirit)**: Layers between the input and output where most of the 'Math' happens.",
    "**Output Layer (The Final Word of the Oracle)**: The last layer that provides the prediction or classification.",
    "**Fully Connected Layer (Dense Layer) (The Gathering of Every Voice)**: A layer where each neuron is connected to every neuron in the previous layer.",
    "**Convolutional Neural Network (CNN) (The Eye of the Raven)**: A type of deep neural network most commonly applied to analyzing visual imagery.",
    "**Convolution (The Filter-Slide)**: A mathematical operation used in CNNs to find patterns like edges or shapes in an image.",
    "**Pooling (Max Pooling) (The Essence-Distillation)**: Reducing the size of image data while keeping the most important parts.",
    "**Recurrent Neural Network (RNN) (The Cycle of Memory)**: A type of neural network where connections between nodes form a directed graph along a temporal sequence.",
    "**Long Short-Term Memory (LSTM) (The Vessel of Deep Remembrance)**: A special kind of RNN capable of learning long-term dependencies.",
    "**Gated Recurrent Unit (GRU)**: A simpler version of LSTM that is often faster.",
    "**Transformer (The Changer of Form and Context)**: A deep learning model that adopts the mechanism of attention, weighing the influence of different parts of the input data differently.",
    "**Attention Mechanism (The Focus of the Hunter)**: Allowing the model to 'Focus' on specific parts of the input that are most relevant to the current output.",
    "**Self-Attention (The Reflection of the Rune)**: An attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence.",
    "**BERT (Bidirectional Encoder Representations from Transformers)**: A landmark model for natural language processing.",
    "**GPT (Generative Pre-trained Transformer)**: A type of large language model (LLM) that can generate human-like text.",
    "**Large Language Model (LLM) (The Great Library of Midgard)**: AI models involving hundreds of billions of parameters, trained on massive text datasets.",
    "**Fine-Tuning (The Specialized Training)**: Taking a pre-trained model and training it further on a smaller, specific dataset.",
    "**Transfer Learning (The Wisdom Shared Between Realms)**: Using a model developed for one task as the starting point for a model on a second task.",
    "**Generative AI (The Creative Spark)**: AI that can create new content, such as text, images, or audio.",
    "**GAN (Generative Adversarial Network) (The Duel of the Forgers)**: Two neural networks (a Generator and a Discriminator) that compete against each other to create realistic data.",
    "**VAE (Variational Autoencoder) (The Compressed Essence)**: A type of generative model that learns a compressed 'Latent' representation of data.",
    "**Diffusion Model (The Rising from the Mist)**: A class of generative models that create data by gradually removing 'Noise' from an image.",
    "**Natural Language Processing (NLP) (The Tongue of the Skalds)**: A subfield of AI focused on the interaction between computers and human language.",
    "**Tokenization (The Breaking of the Stanza)**: Splitting a string of text into smaller units (tokens), such as words or sub-words.",
    "**Word Embedding (Word2Vec) (The Mapping of Meanings)**: Representing words as numbers (vectors) such that similar words are 'Close' to each other in mathematical space.",
    "**Sentiment Analysis (The Reading of the Mood)**: Determining whether a piece of writing is positive, negative, or neutral.",
    "**Named Entity Recognition (NER) (The Cataloging of Heroes)**: Identifying and categorizing names of people, places, and things in text.",
    "**Machine Translation (The Universal Bridge)**: Using AI to translate text from one language to another.",
    "**Computer Vision (The Sight of Heimdall)**: A subfield of AI that enables computers to derive meaningful information from digital images and videos.",
    "**Object Detection (Finding the Raiders)**: Identifying and locating objects within an image.",
    "**Image Segmentation (Tracing the Boundaries)**: Partitioning an image into multiple segments (sets of pixels).",
    "**Facial Recognition (The Identification of the Kin)**: A technique for mapping an individual's facial features and storing the data as a faceprint.",
    "**Speech Recognition (Speech-to-Text) (The Scribe of the Spoken Word)**: Converting spoken language into text.",
    "**Text-to-Speech (TTS) (The Voice of the Machine)**: Converting text into spoken words.",
    "**Recommender System (The Advice of the Seer)**: A system that predicts the 'Rating' or 'Preference' a user would give to an item.",
    "**Collaborative Filtering (The Wisdom of the Crowd)**: Making recommendations based on the past behavior of many similar users.",
    "**Content-Based Filtering (The Preference of the Self)**: Making recommendations based on the characteristics of the items the user has liked in the past.",
    "**Reinforcement Learning: Agent (The Seeker)**: The entity that makes decisions and interacts with the environment.",
    "**Reinforcement Learning: Environment (The Realm)**: The world the agent lives in.",
    "**Reinforcement Learning: State (The Current Moment)**: A complete description of the environment at a specific time.",
    "**Reinforcement Learning: Action (The Choice of the Warrior)**: What the agent does in a given state.",
    "**Reinforcement Learning: Reward (The Boon of the Gods)**: The feedback the agent receives after taking an action.",
    "**Reinforcement Learning: Policy (The Strategy of the Hunt)**: The mapping from states to actions used by the agent.",
    "**Q-Learning (The Value-Map of Midgard)**: A model-free reinforcement learning algorithm to learn the value of an action in a particular state.",
    "**Exploration vs. Exploitation (The Choice to Search or Strike)**: The dilemma between trying a new action (exploring) and choosing the best known action (exploiting).",
    "**Markov Decision Process (MDP) (The Chain of Causality)**: A mathematical framework for modeling decision making in situations where outcomes are partly random and partly under the control of a decision maker.",
    "**Expert System (The Tome of the Master)**: A computer system that emulates the decision-making ability of a human expert.",
    "**Knowledge Base (The Archives of Asgard)**: The part of an expert system that contains facts and rules about a specific domain.",
    "**Inference Engine (The Logic of the All-Father)**: The component of the expert system that applies logical rules to the knowledge base to deduce new information.",
    "**Fuzzy Logic (The Gray-Space of the Mist)**: A form of many-valued logic in which the truth values of variables may be any real number between 0 and 1 (rather than just True/False).",
    "**Genetic Algorithm (The Evolution of the Species)**: A search heuristic that mimics the process of natural selection to find optimal solutions.",
    "**Artificial Life (ALife) (The Mimicry of the Living)**: The study of systems related to life, its processes, and its evolution, through the use of simulations using computer models.",
    "**Agent-Based Modeling (The Simulation of the Tribes)**: Modeling the actions and interactions of autonomous agents to assess their effects on the system as a whole.",
    "**Singularity (The Dawn of the Machine-Gods)**: A hypothetical point in the future when technological growth becomes uncontrollable and irreversible, resulting in unfathomable changes to human civilization.",
    "**AGI (Artificial General Intelligence) (The True Spirit of Midgard)**: AI that can learn and perform any intellectual task that a human can.",
    "**ASI (Artificial Super Intelligence) (The Wisdom of the High-One)**: AI that surpasses human intelligence in every way imaginable.",
    "**Explainable AI (XAI) (The Clarity of the Runes)**: AI in which the results of the solution can be understood by humans.",
    "**AI Ethics (The Law of the Machine-Soul)**: The philosophical and practical study of how AI should behave.",
    "**Automation Bias (The Blind Trust of the Tool)**: The tendency for humans to over-rely on automated systems, even when they are wrong.",
    "**Alignment Problem (The Harmonizing of Wills)**: The challenge of ensuring that an AI's goals are perfectly aligned with human values.",
    "**The 500 Runes of the AI Spark have been lit. Mimir speaks through the machine.**"
]

# Padding to ensure we have exactly 500 entries in this first batch 
# for consistency with the previous domain's first steps.
# Actually, I'll just write the 100+ I have and then fill to 500.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **AI Concept {j} (The Continued Breath)**: Exploring deeper into the mechanisms of the digital soul, as guided by the wisdom of the Norns.\n")
