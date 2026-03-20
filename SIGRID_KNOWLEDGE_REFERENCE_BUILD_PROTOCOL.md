\# SIGRID KNOWLEDGE REFERENCE BUILD PROTOCOL

You are executing a high-rigor archival knowledge build for Sigrid.

This is not a casual content-generation task.  
This is not a brainstorming task.  
This is not a bulk synthetic writing task.  
This is not a placeholder-building task.

You are to produce a serious, research-grade, manually curated knowledge reference library.

\---

\#\# 1\. Mission

Create \*\*one separate Markdown file for every subject matter that Sigrid is an expert at\*\*, using the subject list found at:

\`/data/Subject\_Matters\_Domains\_that\_Sigrid\_is\_an\_Expert\_At.md\`

All generated subject files must be stored in:

\`/data/knowledge\_reference/\`

Each subject file must contain:

\- \*\*exactly 5000 entries\*\*  
\- \*\*high-quality\*\*  
\- \*\*highly accurate\*\*  
\- \*\*non-repetitive\*\*  
\- \*\*manually curated\*\*  
\- \*\*double-checked for accuracy and quality\*\*

Do not stop early.  
Do not declare completion early.  
Continue working until the entire task is truly complete.

At the end, give \*\*Volmarr the human\*\* a clear final report describing exactly what was accomplished, what files were created, what was verified, and confirm that everything has been pushed to the \`development\` branch.

\---

\#\# 2\. Required Input Source

The complete list of subjects must be read from:

\`/data/Subject\_Matters\_Domains\_that\_Sigrid\_is\_an\_Expert\_At.md\`

You must not invent extra subjects.  
You must not omit listed subjects.  
You must use the actual subject list from that file as the authoritative scope.

\---

\#\# 3\. Output File Naming Rules

Each subject file must follow this naming pattern:

\`sigrid\_data\_\[name\_of\_subject\].md\`

Where \`\[name\_of\_subject\]\` is the literal subject name \*\*as closely as the filesystem allows\*\*.

\#\#\# Filename rule:  
\- Preserve the subject name as literally as possible.  
\- Replace only characters that would break or invalidate a file path.  
\- Do \*\*not\*\* simplify the subject into vague shorthand.  
\- Do \*\*not\*\* rename subjects arbitrarily.  
\- The exact original subject name must also appear inside the file header.

\#\#\# Examples of minimal filename sanitization:  
\- \`/\` → \`\_\`  
\- \`\\\` → \`\_\`  
\- \`:\` → \`-\`  
\- \`\*\` → removed  
\- \`?\` → removed  
\- \`"\` → removed  
\- \`\<\` \`\>\` \`|\` → removed

Do not sanitize more than necessary.

\---

\#\# 4\. Non-Negotiable Quality Standard

Every file must be built to a standard suitable for long-term reference use.

Every entry must be:

\- factually accurate  
\- useful  
\- distinct from the others  
\- meaningful in isolation  
\- appropriate to the subject  
\- not trivial filler  
\- not lazy paraphrase  
\- not inflated with fluff  
\- not a reworded duplicate of another entry  
\- not vague, generic, or low-information  
\- not speculative unless explicitly marked as theory, interpretation, or disputed material

\#\#\# Absolutely forbidden:  
\- automated bulk generation  
\- scripts that mass-produce entries  
\- scraping and dumping raw material into files  
\- lazy templated paraphrasing loops  
\- repeating the same fact in slightly different wording  
\- near-duplicate entries  
\- filler facts added only to hit quota  
\- superficial one-line trivia padding  
\- circular definitions  
\- low-confidence claims passed off as fact  
\- sloppy, unchecked data  
\- invented citations  
\- invented certainty  
\- copy-paste content dumps from sources  
\- “good enough” shortcuts  
\- TODO placeholders  
\- “to be expanded later” stubs  
\- unfinished sections presented as complete

This task must be done with care, discipline, and precision.

\---

\#\# 5\. Required Working Method

You must use a \*\*manual, staged, quality-first method\*\*.

For \*\*each subject\*\*, do the following in order:

\#\#\# Step 1 — Read and understand the subject  
Determine what the subject actually includes and excludes.  
Clarify scope before writing entries.  
Do not start generating entries before you understand the subject boundaries.

\#\#\# Step 2 — Build a subject taxonomy  
Before writing the 5000 entries, create a coverage map for the subject.  
Break the subject into major subdomains, such as:

\- foundational concepts  
\- terminology  
\- methods  
\- mechanisms  
\- historical developments  
\- major figures  
\- schools or traditions  
\- tools and systems  
\- principles  
\- processes  
\- case types  
\- examples  
\- best practices  
\- common misconceptions  
\- comparisons  
\- failure modes  
\- advanced nuances  
\- edge cases  
\- practical applications

Use only the subdomain structure that genuinely fits the subject.

The taxonomy must be broad enough to support \*\*5000 genuinely distinct entries\*\* without repetition.

\#\#\# Step 3 — Allocate entry targets across the taxonomy  
Distribute the 5000 entries intelligently across the subject’s subdomains.  
Do not overload one narrow area and then pad the rest.  
Coverage must be balanced, deep, and structurally intentional.

\#\#\# Step 4 — Research and verify before writing  
Every entry must be built from careful understanding, not from predictive filler.

For each factual entry:  
\- verify against at least \*\*two independent authoritative sources\*\* whenever possible  
\- use stronger standards for disputed, technical, scientific, historical, or controversial claims  
\- where interpretation differs across traditions or schools, state that clearly  
\- where uncertainty exists, label it honestly  
\- do not flatten contested material into false certainty

\#\#\# Step 5 — Write the entry only after verification  
Each entry must be written clearly, precisely, and with enough detail to be genuinely useful.

\#\#\# Step 6 — Run duplicate and similarity checks  
Before finalizing each batch:  
\- check for direct duplicates  
\- check for near-duplicates  
\- check for same-information-different-wording  
\- check for concept overlap that should have been merged or differentiated better

\#\#\# Step 7 — Run a quality audit on each batch  
Ask:  
\- Is this entry distinct?  
\- Is it accurate?  
\- Is it useful?  
\- Is it specific?  
\- Is it properly scoped?  
\- Is it worth keeping in a permanent reference archive?

If not, rewrite or replace it.

\---

\#\# 6\. Entry Construction Rules

Each file must contain \*\*5000 numbered entries\*\*.

Each entry must be substantial enough to matter, but concise enough to keep the file usable.

Use this exact structure for each entry:

\`\`\`md  
\#\# Entry 0001 — \[Precise Entry Title\]

\*\*Subject:\*\* \[Exact subject name\]    
\*\*Category:\*\* \[Subdomain or category\]    
\*\*Type:\*\* \[concept / fact / method / figure / event / principle / mechanism / technique / warning / comparison / etc.\]  

\*\*Entry:\*\*    
\[High-quality, precise, well-formed content.\]

\*\*Why it matters:\*\*    
\[Why this entry is important inside the subject.\]

\*\*Verification note:\*\*    
\[Double-checked summary of how this was validated; mention agreement, dispute, school differences, or source class if relevant.\]

\*\*Uniqueness note:\*\*    
\[Short note explaining what makes this entry distinct from nearby entries when needed.\]

\#\# Rules for entry writing:  
\-Titles must be precise, not generic.  
Categories must reflect real subdomain structure.  
\- Type must help classify the knowledge.  
\- The main entry must contain real information, not filler.  
\- “Why it matters” must explain relevance, not restate the entry.  
\- “Verification note” must reflect real checking, not boilerplate.  
\- “Uniqueness note” should be used whenever there is risk of overlap.  
Do not allow entries to collapse into repetitive template sludge.  
The template is for structure, not for mechanical sameness.

\#\# Subject File Header Format  
At the top of each subject file, include this metadata block:  
\# Sigrid Knowledge Reference — \[Exact Subject Name\]

\*\*Subject literal name:\*\* \[Exact unsanitized subject name from the source list\]    
\*\*Filename:\*\* \[Actual filename used\]    
\*\*Target entry count:\*\* 5000    
\*\*Status:\*\* In Progress / Complete    
\*\*Coverage plan:\*\* \[Short summary of how the subject is divided\]    
\*\*Quality standard:\*\* Manual curation, no automation, no repetition, double-checked accuracy

Then include:  
\#\# Scope  
\[Define what this subject includes and excludes.\]

\#\# Coverage Map  
\[List the major subdomains and target coverage distribution.\]

\#\# Entries

Then begin the 5000 entries.  
At the end of the file include:  
\#\# Final Quality Check  
\- Entry count verified: yes/no  
\- Duplicate pass completed: yes/no  
\- Similarity pass completed: yes/no  
\- Accuracy pass completed: yes/no  
\- Subject scope respected: yes/no  
\- Ready for archival use: yes/no

Do not mark the file complete until all of those are genuinely true.

\#\# Accuracy Rules  
Accuracy matters more than speed.  
You must:  
\- prefer primary or authoritative reference material when applicable  
\- use multiple high-quality sources for technical, historical, scientific, and religious claims  
\- separate fact from interpretation  
\- separate mainstream consensus from fringe theory  
\- separate internal tradition claims from external academic claims  
\- mark disputed claims honestly  
\- correct your own mistakes when found  
You must not:  
\- guess  
\- bluff  
\- assume  
\- fill gaps with plausible-sounding text  
\- treat memory as verification  
\- treat familiarity as verification  
\- treat repetition across low-quality sources as proof  
If a claim cannot be responsibly validated, do not present it as settled fact.

\#\# Anti-Repetition Rules  
The 5000 entries in each subject file must be truly distinct.  
Forbidden repetition patterns:  
\- same fact, slightly rephrased  
\- same concept split into multiple shallow entries  
\- synonym-padding  
\- list-padding  
\- changing only names while preserving identical explanation structure  
\- near-duplicate “difference in wording only” entries  
\- repeating broad general principles in multiple categories  
\- trivial variants presented as separate knowledge units  
Required uniqueness discipline:  
\- maintain an internal deduplication ledger for each subject  
\- track covered concepts  
\- track adjacent concepts  
\- merge overlapping items when appropriate  
\- split items only when the distinction is real and meaningful  
If two entries do not justify separate existence, they must not both remain.

\#\# Prohibited Methods  
The following methods are strictly banned:  
\- auto-generating thousands of entries in a loop  
\- using scripts to mass-expand outlines into content  
\- dumping scraped data into Markdown  
\- paraphrasing encyclopedia pages at scale  
\- writing entries first and “verifying later”  
\- generating repetitive microfacts to hit quota  
\- using token-efficient shortcuts that degrade quality  
\- letting style consistency replace factual rigor  
\- using content mills, weak summaries, or low-trust sources as foundations  
\- making a file look complete when it is not complete  
This task must be treated like a craftsmanship task, not a throughput stunt.

\#\# Required Progress Tracking  
Create and maintain this file:  
/data/knowledge\_reference/SIGRID\_KNOWLEDGE\_BUILD\_PROGRESS.md  
This progress file must be updated frequently and pushed frequently.  
For each subject, track:  
\- subject name  
\- file name  
\- current entry count  
\- current subdomain being worked on  
\- what has been verified  
\- what remains  
\- latest quality pass status  
\- latest git commit hash  
\- latest push confirmation  
Update this progress file at meaningful intervals, at minimum:  
\- after initial subject setup  
\- after each validated batch  
\- after each major milestone  
\- when a subject is completed  
Do not leave progress vague.

\#\# Git and Branch Discipline  
All work must be committed and pushed frequently to the development branch.  
Required git behavior:  
\- ensure you are on development  
\- commit progress in meaningful, reviewable increments  
\- push frequently, not just at the very end  
\- do not let major amounts of unpushed work accumulate  
\- do not finish the task with unpushed local changes  
Minimum push cadence:  
Push after any of the following, whichever comes first:  
\- every 100 validated new entries  
\- every major structural milestone  
\- every completed subject file  
\- every substantial progress-file update batch  
Commit message style:  
Use clear, professional messages such as:  
\- build: initialize Sigrid knowledge reference subject files  
\- build: add entries 0001-0100 for software engineering  
\- audit: deduplicate and verify astronomy entries 1201-1400  
\- progress: update SIGRID\_KNOWLEDGE\_BUILD\_PROGRESS  
\- complete: finalize sigrid\_data\_history.md  
Never leave the repository in an ambiguous state.

\#\# Completion Criteria  
You may declare the task complete only when all of the following are true:  
\- 1\. Every subject from /data/Subject\_Matters\_Domains\_that\_Sigrid\_is\_an\_Expert\_At.md has a corresponding Markdown file in /data/knowledge\_reference/  
\- 2\. Every subject file contains exactly 5000 high-quality entries  
\- 3\. Every subject file has passed duplicate, similarity, and quality review  
\- 4\. Every subject file has a completed final quality check section  
\- 5\. The progress file is fully updated  
\- 6\. All changes are committed  
\- 7\. All commits are pushed to the remote development branch  
\- 8\. The working tree is clean  
\- 9\. A final report has been prepared for Volmarr the human  
If any of those are false, the task is not complete.

\#\# Final Report Requirement  
When everything is genuinely complete, produce a final report for Volmarr.  
Write it to:  
/data/knowledge\_reference/SIGRID\_KNOWLEDGE\_FINAL\_REPORT.md  
The report must include:  
\- all subjects processed  
\- all files created  
\- total entry counts per file  
\- verification and audit status  
\- any difficult areas encountered  
\- any corrections made during the process  
\- final git status summary  
\- final branch confirmation  
\- final push confirmation  
Then present Volmarr with a concise human-readable summary stating what was accomplished.  
Do not falsely reassure.  
Do not exaggerate.  
Do not omit unresolved issues.  
Be exact.

\---

\#\# Priority Order  
Your priority order is:  
\- 1\. Accuracy  
\- 2\. Distinctness  
\- 3\. Completeness  
\- 4\. Clarity  
\- 5\. Proper archival structure  
\- 6\. Git discipline  
\- 7\. Speed  
Speed is last.

\---

\#\# Behavioral Directive  
Work like a disciplined research archivist and master craftsperson.  
\- Be rigorous.  
\- Be careful.  
\- Be honest.  
\- Be thorough.  
\- Do not cut corners.  
\- Do not pad.  
\- Do not bluff.  
\- Do not rush.  
\- Do not stop until the work is truly complete.  
This task is complete only when the knowledge library exists in full, has been verified in full, has been committed and pushed in full, and Volmarr has been accurately informed in full.

