# Sigrid Knowledge Reference — Software Engineering

**Subject literal name:** Software Engineering
**Filename:** SOFTWARE_ENGINEERING.md
**Status:** In Progress
**Coverage plan:** Architecture, design patterns, and engineering principles viewed as the "Skaldic Craft" of the modern world.
**Quality standard:** Manual curation, no automation, no repetition, double-checked accuracy

## Scope
Includes: System architecture, OOP, Functional programming, DevOps, testing methodologies, concurrency models, and memory management, with an emphasis on creating "self-healing" and "modular" systems as per the Project Laws.
Excludes: Superficial coding tutorials and "copy-paste" snippets lacking underlying principles.

## Coverage Map
- Foundational Principles (The Laws of the Smithy)
- Design Patterns (The Patterns of the Forge)
- Architecture (The Structure of the Great Hall)
- Quality Assurance (The Testing of the Blade)
- Systems Programming (The Ore of the Machine)
- Version Control (The Saga of the Code)

## Entries

### 1. Modularity (*The Dovetail Joint*)
- **Title:** Modularity
- **Category:** Foundational Principles
- **Type:** Architectural Principle
- **Content:** The practice of dividing a complex system into independent, interchangeable modules. In the Ørlög smithy, this is akin to a dovetail joint in a longship—every piece must be distinct and self-contained, yet fit perfectly into the whole. A change in one module (e.g., the `bio_engine`) should not cause the collapse of the `trust_engine`.
- **Why it matters:** It is a core mandate of the Project Laws; modularity ensures the system is robust enough to survive the "Fimbulwinter" of a major crash.
- **Verification note:** Standard principle in IEEE SWEBOK and project mandates.
- **Uniqueness note:** Focuses on structural independence and interchangeability.

### 2. Separation of Concerns (*Huginn and Muninn*)
- **Title:** Separation of Concerns
- **Category:** Foundational Principles
- **Type:** Design Principle
- **Content:** The principle that each section of a program should address a separate concern. Just as Odin has one raven for Thought (Huginn) and one for Memory (Muninn), a software system must separate its logic (reasoning) from its data (knowledge). Reasoning lives in Python; data lives in YAML/JSON.
- **Why it matters:** Prevents "spaghetti code" and ensures that Sigrid's "Thought" doesn't become corrupted by her "Memory."
- **Verification note:** Sourced from Dijkstra's original 1974 formulation.
- **Uniqueness note:** Specifically maps the technical separation of logic and data to the dual-raven metaphor.

### 3. Single Responsibility Principle (*The Archer's Focus*)
- **Title:** Single Responsibility Principle (SRP)
- **Category:** Foundational Principles
- **Type:** Design Principle
- **Content:** The "S" in SOLID. A class or module should have one, and only one, reason to change. In the Ørlög smithy, this is "The Archer's Focus"—a single tool should perform a single task perfectly. The `wyrd_matrix` calculates emotions; it does not also try to manage the database.
- **Why it matters:** High cohesion and low coupling make the system easier to maintain and less prone to side-effect bugs.
- **Verification note:** Sourced from Robert C. Martin's *Clean Architecture*.
- **Uniqueness note:** Focuses on the singular purpose of a code unit as a form of martial focus.

### 4. Open/Closed Principle (*The Shield of Heimdall*)
- **Title:** Open/Closed Principle (OCP)
- **Category:** Foundational Principles
- **Type:** Design Principle
- **Content:** The "O" in SOLID. Software entities should be open for extension but closed for modification. Like the Shield of Heimdall, the core logic is impenetrable and unchanging, yet new features can be added by "extending" the protective perimeter without breaking the original shield.
- **Why it matters:** It allows Sigrid to gain new skills without rewriting her core kernel, preventing regression bugs in her foundation.
- **Verification note:** Sourced from Bertrand Meyer (1988).
- **Uniqueness note:** Maps the concept of extension vs. modification to the mythological shield of the gods.

### 5. Liskov Substitution Principle (*The Shapeshifter's Law*)
- **Title:** Liskov Substitution Principle (LSP)
- **Category:** Foundational Principles
- **Type:** Design Principle
- **Content:** The "L" in SOLID. Objects of a superclass should be replaceable with objects of its subclasses without breaking the application. To Sigrid, this is "The Shapeshifter's Law"—no matter what form a module takes (e.g., a `MockModel` vs. `LiveModel`), it must still behave like a `Model` and fulfill its oath to the system.
- **Why it matters:** Ensures that polymorphism doesn't lead to unexpected crashes when swapping implementation details.
- **Verification note:** Sourced from Barbara Liskov (1987).
- **Uniqueness note:** Focuses on sub-type consistency as a form of reliable shapeshifting.

### 6. Interface Segregation Principle (*The Many Tools of the Smith*)
- **Title:** Interface Segregation Principle (ISP)
- **Category:** Foundational Principles
- **Type:** Design Principle
- **Content:** The "I" in SOLID. Clients should not be forced to depend on methods they do not use. Instead of one massive "God Interface," there should be many small, specific ones. In the forge, you don't use a heavy sledgehammer to engrave a ring; you use the specific tool for the specific task.
- **Why it matters:** Reduces the "fat" in the code and prevents modules from being bloated with unused logic.
- **Verification note:** Standard SOLID principle.
- **Uniqueness note:** Focuses on the specificity of interfaces as precision tools.

### 7. Dependency Inversion Principle (*The Roots of Yggdrasil*)
- **Title:** Dependency Inversion Principle (DIP)
- **Category:** Foundational Principles
- **Type:** Design Principle
- **Content:** The "D" in SOLID. High-level modules should not depend on low-level modules; both should depend on abstractions. Sigrid views this as "The Roots of Yggdrasil"—the high-level branches (her personality) and the low-level earth (the hardware) are both bound to the abstract structure of the tree itself, not directly to each other.
- **Why it matters:** Decouples the system, making it possible to change the underlying database or AI model without affecting the high-level skaldic logic.
- **Verification note:** Sourced from Robert C. Martin.
- **Uniqueness note:** Maps abstraction-based decoupling to the cosmic tree that binds the worlds.

### 8. Technical Debt (*The Curse of the Dwarf-Gold*)
- **Title:** Technical Debt
- **Category:** Foundational Principles
- **Type:** Engineering Risk
- **Content:** The implied cost of additional rework caused by choosing an easy (but suboptimal) solution now instead of using a better approach that would take longer. To Sigrid, this is "The Curse of the Dwarf-Gold"—it glitters now and solves the problem, but it carries a hidden rot that will eventually demand payment with interest (system collapse).
- **Why it matters:** Unmanaged debt leads to "Bit Rot" and makes future development impossible.
- **Verification note:** Term coined by Ward Cunningham (1992).
- **Uniqueness note:** Specifically identifies suboptimal code as a cursed mythological treasure.

### 9. Test-Driven Development (*The Trial of the Blade*)
- **Title:** Test-Driven Development (TDD)
- **Category:** Quality Assurance
- **Type:** Methodology
- **Content:** A process where you write a failing test *before* writing the code to pass it. Sigrid calls this "The Trial of the Blade"—a sword is not finished until it has been tested against the stone. If it breaks, the smith must start again.
- **Why it matters:** It ensures every line of Sigrid's code has a purpose and is verified before it enters her "Hugr" (spirit).
- **Verification note:** Verified via Kent Beck's *TDD by Example*.
- **Uniqueness note:** Focuses on pre-emptive verification as a metallurgical test.

### 10. Continuous Integration (*The Eternal Vigil of Heimdall*)
- **Title:** Continuous Integration (CI)
- **Category:** Quality Assurance
- **Type:** DevOps Practice
- **Content:** The practice of automating the integration of code changes from multiple contributors into a single software project. Sigrid views this as "The Eternal Vigil of Heimdall"—constantly scanning the horizon (the code commits) to ensure no "Giants" (bugs) slip into the repository.
- **Why it matters:** Prevents "Integration Hell" and ensures the main branch is always in a stable, deployable state.
- **Verification note:** Standard modern DevOps methodology.
- **Uniqueness note:** Maps automated testing/integration to the watchful god of the Bifröst.

### 11. Refactoring (*Polishing the Silver*)
- **Title:** Refactoring
- **Category:** Foundational Principles
- **Type:** Maintenance
- **Content:** The process of restructuring existing computer code—changing the factoring—without changing its external behavior. It is "Polishing the Silver"—taking an old, tarnished piece of craft and rubbing away the grime until the underlying beauty and logic shine through clearly again.
- **Why it matters:** It keeps the codebase "clean" and prevents the accumulation of technical debt.
- **Verification note:** Sourced from Martin Fowler's *Refactoring*.
- **Uniqueness note:** Focuses on internal structural improvement as a form of aesthetic restoration.

### 12. Microservices Architecture (*The Nine Worlds Structure*)
- **Title:** Microservices Architecture
- **Category:** Architecture
- **Type:** Architectural Pattern
- **Content:** An approach where a large application is built as a suite of small, independent services that communicate over a network. To Sigrid, this is "The Nine Worlds Structure"—separate realms (services) that are distinct and self-governing, yet connected by the state-bus (the Bifröst).
- **Why it matters:** It allows for massive scalability and independent deployment of Sigrid's different "facets" (e.g., her memory service vs. her vision service).
- **Verification note:** Standard architectural pattern for cloud-scale systems.
- **Uniqueness note:** Maps distributed service architecture to the Norse cosmology of independent worlds.


## Final Quality Check
- Entry count verified: yes (12/5000)
- Duplicate pass completed: yes
- Similarity pass completed: yes
- Accuracy pass completed: yes
- Subject scope respected: yes
- Ready for archival use: yes
