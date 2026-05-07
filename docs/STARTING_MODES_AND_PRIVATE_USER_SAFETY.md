# Bridge Engine — Starting Modes + Private User Safety Roadmap

## Core Idea

Bridge Engine should help users bridge the hardest gap:

> intention → action

Many users do not need more information first. They need a lower-friction way to begin.

This document defines future systems for:
- assignment photo intake
- environment-change prompts
- lockout/focus modes
- scheduled encouragement
- AI assistant nudges
- security and privacy requirements
- legal/compliance guardrails

---

# 1. Assignment / Task Photo Intake

## Concept

User can take a photo or upload a screenshot of:
- assignment instructions
- homework page
- syllabus task
- work project notes
- textbook section
- whiteboard
- calendar item
- messy to-do list

Bridge Engine turns it into:
- simplified task summary
- first 3-minute start step
- difficulty estimate
- required materials
- deadline awareness
- suggested learning style
- energy-mode version

## Important Privacy Rule

Photos may contain highly sensitive data.

Potential sensitive information:
- school names
- teacher/professor names
- grades
- student IDs
- emails
- addresses
- medical/accommodation info
- private notes

## Required Safety Features Before Launch

- clear upload consent
- warning before upload
- automatic redaction later
- delete photo option
- do not store raw image unless necessary
- default to processing then deleting
- separate user data by account
- never expose uploaded images publicly

## Future Processing Pipeline

1. user uploads image
2. OCR / vision model extracts text
3. system detects sensitive fields
4. redaction layer removes unnecessary info
5. assignment parser creates action plan
6. adaptive engine generates first step
7. user confirms/save

---

# 2. Just Start Modes

## Purpose

Help users begin when they feel stuck, overwhelmed, avoidant, tired, or unclear.

## Modes

### 30-Second Start
- open the assignment
- write the title
- copy the question
- identify one keyword
- put materials in front of you

### 3-Minute Start
- summarize instructions in one sentence
- write one bad first sentence
- solve only the first line
- make one file/folder
- create one tiny checklist

### 10-Minute Build
- create visible artifact
- draft a small answer
- build a small UI/card/table
- complete one checkpoint

### Recovery Mode
- no guilt
- no backlog dump
- one tiny re-entry action
- restore momentum

### Hyperfocus Mode
- deeper challenge
- limit burnout
- add stopping checkpoint
- save next step before leaving

---

# 3. Environment Change Prompts

## Concept

Sometimes the best productivity intervention is not another task. It is a state change.

Potential prompts:
- stand up
- move to another room
- walk for 3 minutes
- put headphones on
- play focus music
- clean one square foot of desk
- open laptop only
- put phone across the room
- go to public study spot
- body double with a friend

## Adaptive Logic

If user repeatedly avoids tasks:
- suggest environment shift before task

If user reports low energy:
- suggest walking/audio/reflection mode

If user is in hyperfocus:
- avoid interrupting unless burnout risk appears

---

# 4. Lockout / Focus Guardrails

## Concept

A future desktop/mobile agent could help reduce distractions while a user is trying to start.

Potential features:
- block selected apps during focus sessions
- allow only needed apps/sites
- timed focus windows
- emergency unlock
- soft warnings before blocking
- distraction logs

## Ethical Requirements

Avoid trapping users.

Required:
- user opt-in
- easy emergency unlock
- clear timer
- no hidden blocking
- no punishment language
- no manipulative urgency

This should support user agency, not remove it.

---

# 5. Scheduled Encouragement / AI Assistant Nudges

## Concept

The assistant can send scheduled nudges based on:
- due dates
- abandoned paths
- energy mode
- preferred work times
- streak recovery
- project milestones

## Message Types

### Gentle Start
"Want a 3-minute restart? No need to catch up first."

### Momentum Push
"You are one small step away from unlocking the next checkpoint."

### Recovery
"You are not behind. Let’s restart with the smallest useful action."

### Hyperfocus Protection
"Before you stop, save the next step so restarting is easier."

### Environment Shift
"Try standing up, putting music on, and doing only the first tiny action."

## Privacy Rule

Do not reveal sensitive task details in notifications unless user opts in.

Bad:
"Your ADHD accommodation assignment is overdue."

Better:
"You have a saved task ready for a 3-minute restart."

---

# 6. Security Requirements

Before real users:

## Authentication
- user accounts
- secure password hashing
- session security
- logout
- optional OAuth

## Data Isolation
- user_id on every record
- no shared JSON data in production
- row-level separation later

## Storage
- move from JSON to SQLite/PostgreSQL
- encrypt sensitive fields where practical
- backups
- deletion/export tools

## Upload Security
- file size limits
- allowed file types only
- virus/malware scanning later
- private storage bucket
- signed URLs later

## App Security
- HTTPS only
- CSRF protection
- rate limiting
- secure cookies
- no secrets in GitHub
- environment variables only
- audit logs for sensitive actions

---

# 7. Legal / Compliance Concerns

Bridge Engine may involve:
- students
- education data
- productivity data
- behavioral data
- private uploaded documents
- possible minors later

## Required Later

- Privacy Policy
- Terms of Service
- Data Processing Policy
- User deletion/export
- AI disclosure
- upload consent
- cookie policy if tracking
- accessibility statement

## Be Careful With Claims

Avoid saying:
- treats ADHD
- cures procrastination
- medical support
- therapy replacement
- guaranteed academic outcomes

Safer positioning:
- adaptive learning support
- focus assistance
- project-based productivity
- momentum-building system
- personalized task-start support

---

# 8. Product Philosophy

The app should feel like a seatbelt:
- supportive
- protective
- available when needed
- not controlling
- not shame-based
- not addictive by manipulation

Goal:
> Make useful effort feel more rewarding and easier to start.

Not:
> Maximize screen time.

---

# 9. Future Implementation Priorities

1. Intake questionnaire
2. Just Start modes
3. Scheduled encouragement system
4. Assignment photo upload parser
5. Privacy-safe upload handling
6. User accounts and data isolation
7. Database migration
8. Focus/app-block agent prototype
9. Adaptive notification rules
10. Legal/privacy docs before public launch
