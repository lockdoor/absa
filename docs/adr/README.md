# Architecture Decision Records (ADR)

## Overview

This directory contains Architecture Decision Records (ADRs) for the Review Radar project. ADRs document significant architectural decisions made during the project's development.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences.

## Format

Each ADR follows this structure:
- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Context:** The issue motivating this decision
- **Decision:** The change we're proposing or have agreed to
- **Consequences:** What becomes easier or harder as a result

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [000](000-template.md) | ADR Template | - | - |
| [001](001-overall-architecture.md) | Overall System Architecture | Accepted | 2025-12-22 |
| [002](002-data-layer-architecture.md) | Data Layer Architecture | Accepted | 2025-12-22 |
| [003](003-service-layer-design.md) | Service Layer Design | Proposed | 2025-12-22 |
| [004](004-ml-pipeline-design.md) | ML Pipeline Design | Proposed | 2025-12-22 |
| [005](005-model-retraining-strategy.md) | Model Retraining Strategy | Proposed | 2025-12-22 |

## Creating a New ADR

1. Copy `000-template.md` to `NNN-title.md` (increment NNN)
2. Fill in all sections
3. Discuss with team
4. Update status to "Accepted" when finalized
5. Update this README

## Statuses

- **Proposed:** Under discussion
- **Accepted:** Decision made and implemented
- **Deprecated:** No longer relevant
- **Superseded:** Replaced by another ADR

## Related Documents

- [Project Persona](../PROJECT_PERSONA.md) - User personas and requirements
- [README](../../README.md) - Project documentation

---

**Note:** ADRs are immutable once accepted. Create a new ADR to supersede or amend an existing one.
