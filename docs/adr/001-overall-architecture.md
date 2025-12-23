# ADR-001: Overall System Architecture

**Status:** Accepted

**Date:** 2025-12-22

**Deciders:** ML Engineering Team, System Architects

**Technical Story:** Review Radar - ABSA Social Media Sentiment Analysis System

---

## Context and Problem Statement

Review Radar ต้องการสถาปัตยกรรมที่รองรับ workflow ตั้งแต่การเก็บข้อมูล, inference, validation, model monitoring, และ retraining อย่างมีประสิทธิภาพ ระบบต้องจัดการกับข้อมูลจากหลาย social media platforms และต้องสามารถ scale ได้ตามจำนวนงาน

**Key Requirements:**
- รองรับ multiple data sources (Supabase, PostgreSQL, MongoDB)
- แยก concerns ระหว่าง data access, business logic, และ ML operations
- ง่ายต่อการ test, maintain, และ extend
- รองรับ model retraining pipeline
- Monitoring และ observability

---

## Decision Drivers

* **Maintainability:** โค้ดต้องง่ายต่อการดูแลและขยายขนาย
* **Testability:** แต่ละ component ต้อง testable แยกส่วนได้
* **Flexibility:** เปลี่ยน data source หรือ ML model ได้ง่าย
* **Separation of Concerns:** แยก data, business logic, และ ML operations
* **Python Best Practices:** ใช้ patterns ที่เหมาะกับ Python ecosystem
* **ML Operations:** รองรับ MLOps practices (monitoring, retraining, versioning)

---

## Considered Options

1. **Monolithic Architecture** - ทุกอย่างอยู่ใน module เดียว
2. **Layered Architecture with Design Patterns** - แบ่ง layers ชัดเจนพร้อม design patterns
3. **Microservices Architecture** - แยกเป็น services อิสระ

---

## Decision Outcome

**Chosen option:** "Layered Architecture with Design Patterns"

**Justification:** 
- เหมาะกับขนาดของโปรเจค (ไม่ซับซ้อนเกินไปแต่ไม่ oversimplify)
- ใช้ design patterns ที่เหมาะกับ ML/AI projects
- ง่ายต่อการ deploy และ maintain
- สามารถ scale to microservices ในอนาคตได้
- รองรับ MLOps practices

### Positive Consequences

* ✅ Code structure ชัดเจน แยก concerns ดี
* ✅ ง่ายต่อการ test แต่ละ layer
* ✅ Reusable components
* ✅ เปลี่ยน implementation ได้ง่าย (e.g., เปลี่ยน database)
* ✅ Team members เข้าใจ architecture ได้ง่าย
* ✅ รองรับ CI/CD และ automated testing

### Negative Consequences

* ⚠️ มี boilerplate code มากกว่า monolithic
* ⚠️ ต้องเรียนรู้ design patterns
* ⚠️ การ refactor ต้องทำหลาย layers

---

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│           Client/API Layer                  │
│     (FastAPI, CLI, Notebooks)               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Service Layer                      │
│   - TrainingService                         │
│   - EvaluationService                       │
│   - PredictionService                       │
│   - MonitoringService                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Pipeline Layer                      │
│   - TrainingPipeline                        │
│   - InferencePipeline                       │
│   - PreprocessingPipeline                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        Repository Layer                     │
│   - ReviewRepository                        │
│   - ModelRepository                         │
│   - MetricsRepository                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Data Layer                         │
│   - BaseDataset (Factory Pattern)           │
│   - SupabaseDataset                         │
│   - PostgresDataset                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        Infrastructure                       │
│   (Supabase, PostgreSQL, S3, MLflow)        │
└─────────────────────────────────────────────┘
```

---

## Design Patterns Applied

### 1. **Repository Pattern** (Data Access Layer)
- Abstracts data access logic
- Easy to mock for testing
- Switch data sources without affecting business logic

### 2. **Service Layer Pattern** (Business Logic Layer)
- Orchestrates business workflows
- Coordinates between repositories and models
- Transaction boundaries

### 3. **Pipeline Pattern** (ML Operations)
- Composable ML workflows
- Reusable steps
- Easy to test individual steps

### 4. **Factory Pattern** (Object Creation)
- Create appropriate dataset based on client type
- Centralized object creation logic

### 5. **Strategy Pattern** (Algorithm Selection)
- Switch preprocessing strategies
- Different loss functions
- Pluggable augmentation strategies

### 6. **Observer Pattern** (Monitoring & Callbacks)
- Training callbacks
- Model monitoring
- Event notification

---

## Pros and Cons of the Options

### Monolithic Architecture

* **Good:** Simple to start, less overhead
* **Good:** Easy deployment (single package)
* **Bad:** Hard to test individual components
* **Bad:** Tight coupling
* **Bad:** Difficult to scale specific parts
* **Bad:** Hard to maintain as project grows

### Layered Architecture with Design Patterns ✅

* **Good:** Clear separation of concerns
* **Good:** Testable components
* **Good:** Flexible and extensible
* **Good:** Follows SOLID principles
* **Good:** Good for medium-sized ML projects
* **Bad:** More initial setup
* **Bad:** Requires understanding of patterns
* **Bad:** More files/modules to manage

### Microservices Architecture

* **Good:** Highly scalable
* **Good:** Independent deployment
* **Good:** Technology diversity
* **Bad:** Over-engineering for current scale
* **Bad:** Complex infrastructure
* **Bad:** Network latency between services
* **Bad:** Distributed system challenges

---

## Implementation Guidelines

### Module Structure
```
review_radar/
├── data/              # Data Layer (Factory Pattern)
├── repositories/      # Repository Pattern
├── services/          # Service Layer Pattern
├── pipelines/         # Pipeline Pattern
├── strategies/        # Strategy Pattern
├── models/            # ML Models
├── training/          # Training (Observer Pattern)
├── evaluation/        # Evaluation
├── inference/         # Inference
└── utils/             # Utilities
```

### Key Principles
1. **Dependency Inversion:** Depend on abstractions (base classes) not concretions
2. **Single Responsibility:** Each class/module has one job
3. **Open-Closed:** Open for extension, closed for modification
4. **Interface Segregation:** Small, focused interfaces
5. **Liskov Substitution:** Subclasses can replace parent classes

---

## Links

* [ADR-002: Data Layer Architecture](002-data-layer-architecture.md)
* [ADR-003: Service Layer Design](003-service-layer-design.md)
* [ADR-004: ML Pipeline Design](004-ml-pipeline-design.md)
* [ADR-005: Model Retraining Strategy](005-model-retraining-strategy.md)
* [Project Persona](../PROJECT_PERSONA.md)

---

## Notes

- This architecture allows us to start simple and evolve to microservices if needed
- Focus on Python best practices and ML-specific patterns
- All layers should be testable with mock data
- Consider adding API layer (FastAPI) in future for REST endpoints
