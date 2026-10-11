# 🏁 Project: Middara Helper App — Sprint File

## 📊 Sprint 2: Ingestion Pipeline & Layout Scaffolding
**Status:** 🏃‍♂️ Active
**Timeline:** Oct 11, 2026 – TBD

---

### 🏃‍♂️ Active Task Board

```unset
[📜 Todo] ➔➔➔➔➔➔➔➔➔➔➔➔➔➔➔ [⚡ In Progress] ➔➔➔➔➔➔➔➔➔➔➔➔➔➔➔ [✅ Done]
Task 2: Raw Rulebook Data     Task 1: JSON Schema Integration
        Ingestion                     (Code Generator)
        (Editor Assistant)
Task 3: Core App Layout 
        Scaffolding
        (Architect)
```

---

### 📋 Active Task Specifications

#### 🦾 Task 1: JSON Schema Integration
* **Assignee:** Code Generator
* **Status:** ⚡ In Progress
* **Specs:** Implement the official rulebook data JSON schema structure directly into the core file-parsing logic. The schema must cleanly organize page numbers, chapter headings, core rules, keywords, and verbatim text tracking.

#### 📖 Task 2: Raw Rulebook Data Ingestion
* **Assignee:** Editor Assistant & Architect
* **Status:** 📜 Todo
* **Specs:** Execute the newly built Python Ingestion Linter over the raw rulebook text files. Validate the parsed text against the Task 1 JSON schema and push the resulting structured data into the local database pipeline.

#### 🎛️ Task 3: Core App Layout Scaffolding
* **Assignee:** Architect
* **Status:** 📜 Todo
* **Specs:** Build out the structural layout foundation of the application codebase (e.g., establishing a resizable multi-panel layout layout or basic screen navigation tree) to prepare for displaying the ingested rulebook data.

---

## 🏛️ Project History & Archive

### ✅ Sprint 1: Foundation & Automated Validation
**Status:** Completed (Oct 11, 2026)

*   **Task 1: Project Setup & Repo** `[✅ Done]`
    * *Achievements:* Initial repository structured. Roles and core execution scopes mapped.
*   **Task 2: Basic Chatbot Persona** `[✅ Done]`
    * *Achievements:* Established guidelines for rule-delivery tone and narrative assistance.
*   **Task 3: Ingestion Linter & Validation Verification** `[✅ Done]`
    * *Achievements:* Built a robust text-token validation engine in Python. Successfully automated the validation workflow with a GitHub Actions CI pipeline located at `.github/workflows/python-linter-ci.yml`.
