# Backend Runtime V2

## Goal
Create a unified adaptive completion runtime capable of taking a user from:
- difficult starting point
- adaptive guided progression
- evolving artifact creation
- exportable final output

while preserving:
- context
- frame/interest translation
- task type
- memory
- progression state

## Core Runtime Layers

### 1. Canonical Session Schema
Single source of truth for:
- workspace_id
- task
- category
- frame
- supports
- artifact
- memory
- current_step
- progress
- export_state
- rewrite_history
- user_preferences

### 2. Task Type Registry
Planned task types:
- essay_writing
- language_learning
- coding_project
- study_prep
- difficult_conversation
- professional_strategy
- life_admin
- general

### 3. Artifact Engine V2
Artifacts evolve into real outputs.

Examples:
- essays -> final draft
- language learning -> practice sheets/dialogues
- coding -> implementation plans/files
- studying -> summaries/flashcards
- conversations -> message drafts/talking points

### 4. Runtime Orchestrator
Adaptive next-step engine based on:
- user progress
- rewrite usage
- stuckness
- response quality
- decomposition level

### 5. Rewrite Engine
Context-aware transformations:
- make_easier
- break_smaller
- explain_differently
- give_example

### 6. Export Compiler
Export formats:
- markdown
- text
- structured draft
- study guide
- practice sheet

### 7. Learning Memory
Persistent learning preferences:
- prefers examples first
- prefers smaller steps
- preferred frame
- professional mode
- pacing profile

### 8. API Contract Testing
Required endpoints:
- POST /api/session/create
- POST /api/session/continue
- POST /api/session/rewrite
- POST /api/session/export
- GET /api/workspace/<id>
- GET /api/workspaces/recent

## Guiding Product Principle
Bridge should feel like:
"a way into difficult work"

not:
- generic productivity software
- checklist software
- static AI prompt UI
