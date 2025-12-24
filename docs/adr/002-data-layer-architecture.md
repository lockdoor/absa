# ADR-002: Database Client Layer Architecture

**Status:** Accepted

**Date:** 2025-12-22 (Updated: 2025-12-24)

**Deciders:** Data Engineering Team, ML Engineering Team

**Related:** ADR-001, ADR-003

---

## Context and Problem Statement

ระบบต้องรองรับการทำงานกับหลาย database sources (Supabase, PostgreSQL, MongoDB) สำหรับ CRUD operations และต้องมีวิธีการจัดการข้อมูลที่แตกต่างกันตาม client type แต่ละตัว เราต้องการ abstraction layer ที่ทำให้ business logic (Repository, Service) ไม่ต้องสนใจว่าข้อมูลมาจาก database ไหน

**Key Requirements:**
- รองรับหลาย database sources
- Abstract database access details
- ง่ายต่อการเพิ่ม database client ใหม่
- มี specific methods สำหรับแต่ละ operation
- Type-safe และ testable

---

## Decision Drivers

* **Flexibility:** เพิ่ม data source ใหม่ได้ง่าย
* **Abstraction:** Business logic ไม่ต้องรู้จัก data source
* **Type Safety:** ใช้ type hints เพื่อ IDE support
* **Extensibility:** รองรับ custom queries
* **Testability:** Mock ได้ง่ายสำหรับ unit tests
* **Python Idioms:** ใช้ Pythonic patterns

---

## Considered Options

1. **Direct Client Usage** - ใช้ database client โดยตรงใน business logic
2. **Simple Base Class** - Base class เดียว implement ทุก data source
3. **Factory Pattern + Strategy Pattern** - Factory สร้าง dataset, Strategy สำหรับ fetch logic
4. **Repository Pattern over Data Layer** - Repository เป็น interface เดียว

---

## Decision Outcome

**Chosen option:** "Factory Pattern + Strategy Pattern"

**Justification:**
- Factory Pattern: สร้าง appropriate client instance based on database type
- Strategy Pattern: แต่ละ client implement database operations ของตัวเอง
- ใช้ specific methods แทน generic query functions (ชัดเจน testable)
- ใช้ polymorphism ของ Python (duck typing)
- ไม่ต้อง explicit casting

### Positive Consequences

* ✅ เพิ่ม database client ใหม่ง่าย (implement + register)
* ✅ Business logic ใช้ `BaseClient` type เดียว
* ✅ Auto-detect client type
* ✅ Specific methods ชัดเจน ง่ายต่อการ test
* ✅ Type-safe with Python type hints
* ✅ Easy to test with mock clients

### Negative Consequences

* ⚠️ ต้องสร้าง client class สำหรับแต่ละ database
* ⚠️ ต้องเพิ่ม method ใหม่เมื่อมี operation ใหม่
* ⚠️ Registry pattern เพิ่ม complexity เล็กน้อย

---

## Architecture Design
Client (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from pandas import DataFrame

class BaseClient(ABC):
    """Base class for database client CRUD operations"""
    
    def __init__(self, client: Any, logger: Optional[Any] = None):
        self.client = client
        self.logger = logger
    
    @abstractmethod
    def get_reviews_without_labels(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> DataFrame:
        """Fetch reviews without labels"""
        pass
    
    @abstractmethod
    def update_reviews(
        self,
        review_id: Any,
        update_data: Dict[str, Any]
    ) -> None:
        """Update a review record"""
        pass
```

**Design Principles:**
- แต่ละ method มีความรับผิดชอบชัดเจน (Single Responsibility)
- ไม่ใช้ generic methods แต่สร้าง specific methods สำหรับแต่ละ operation
- เพิ่ม methods ใหม่เมื่อมี operation ใหม่

### 2. Factory Pattern

```python
class ClientFactory:
    """Factory for creating appropriate client instances"""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, client_type: str):
        """Decorator to register client classes"""
        def decorator(client_class: type):
            cls._registry[client_type] = client_class
            return client_class
        return decorator
    
    @classmethod
    def create(
        cls,
        client: Any,
        client_type: Optional[str] = None,
        **kwargs
    ) -> BaseClient:
        """Create appropriate client based on type"""
        if client_type is None:
            client_type = cls._detect_client_type(client)
        
        client_class = cls._registry.get(client_type)
        if client_class is None:
            raise ValueError(f"Unknown client type: {client_type}")
        
        return client_class(client=client, **kwargs)
    
    @classmethod
    def _detect_client_type(cls, client: Any) -> str:
        """Auto-detect client type from class name"""
        client_class_name = client.__class__.__name__.lower()
        
        if 'supabase' in client_class_name:
            return 'supabase'
        elif 'postgres' in client_class_name or 'psycopg' in client_class_name:
            return 'postgres'
        elif 'mongo' in client_class_name:
            return 'mongodb'
        
        raise ValueError(f"Cannot auto-detect client type for {client.__class__.__name__}")
```

### 3. Concrete Implementations

```python
from supabase import Client
from .client_factory import ClientFactory

@ClientFactory.register('supabase')
class SupabaseClient(BaseClient):
   Design Philosophy: Specific Methods vs Generic Methods

### Chosen Approach: Specific Methods ✅

แต่ละ operation มี method เฉพาะ:
```python
client.get_reviews_without_labels(limit=100)
client.get_reviews_by_batch(batch_id=123)
client.update_reviews(review_id=1, data={...})
client.bulk_update_reviews(updates=[...])
```

**Rationale:**
- ✅ **Clear Intent:** method name บอกได้ชัดเจนว่าทำอะไร
- ✅ **Type Safety:** parameters มี type hints ชัดเจน
- ✅ **Easy to Test:** mock แต่ละ method ได้ง่าย
- ✅ **Documentation:** docstring อธิบาย method เฉพาะเจาะจง
- ✅ **IDE Support:** autocomplete แสดง available operations
- ✅ **Maintainability:** แก้ไข method เดียวไม่กระทบอื่น

### Alternative: Generic Methods ❌

```python
# ไม่ใช้แนวทางนี้
client.query(table='reviews', filter={...}, custom_fn=lambda: ...)
```

**Why Not:**
- ❌ Unclear intent - ต้องอ่าน parameters
- ❌ Hard to test - ต้อง mock generic method
- ❌ No type safety - parameters เป็น dict
- ❌ Poor IDE support - ไม่รู้ว่ามี operations อะไรบ้างdata)
            .eq('review_id', review_id)
            .execute()
        )

# Helper function for creating client from environment
```
def create_supabase_client_from_env() -> Client:
    """Create Supabase client from environment variables"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials not found in environment")
    
    return create_client(supabase_url, supabase_key)
```

### 4. Usage Examples

```python
from review_radar.data import ClientFactory
from review_radar.data.supabase_client import create_supabase_client_from_env

# Create database client
supabase = create_supabase_client_from_env()
```
base type
* **Good:** Easy to extend (add new database support)
* **Good:** Auto-detection of client type
* **Good:** Specific methods for clear operations
* **Good:** Type-safe with base class
* **Good:** Easy to mock for testing
* **Bad:** More classes to maintain
* **Bad:** Need to add methods for new operations
# Use in business logic
```
def fetch_unlabeled(client: BaseClient, limit: int):
    """Business logic uses BaseClient interface"""
    df = client.get_reviews_without_labels(limit=limit)
    return df
```
# Update records
```
client.update_reviews(
    review_id=123,
    update_data={'label': {'sentiment': 'positive'}}

    loader = dataset.create_dataloader(...)
```
Client abstract class
- [x] ClientFactory with registry and auto-detection
- [x] SupabaseClient implementation
- [x] Helper function: `create_supabase_client_from_env()`
- [x] Unit tests with mock clients (28 tests, 100% coverage)
- [x] Factory tests (29 tests, 100% coverage)

### Phase 2: Additional Implementations (Future)
- [ ] PostgresClient implementation
- [ ] MongoDBClient implementation
- [ ] Add more CRUD methods as needed
  - [ ] `get_reviews_by_batch(batch_id)`
  - [ ] `bulk_update_reviews(updates)`
  - [ ] `delete_reviews(review_id)`

### Phase 3: Enhancements (Future)
- [ ] Connection pooling
- [ ] Caching layer
- [ ] Retry logic for failed operations
- [ ] Async support for concurrent operations
- [ ] Transaction support

### Phase 4: Testing ✅ (Partially Complete)
- [x] Unit tests with mock clients
- [x] Pytest configuration with coverage
- [x] Hierarchical test structure
```

### Custom Query Function
For complex queries (joins, aggregations):
```python
def custom_query(client, offset, limit):
    # Complex logic here
    return data

df = dataset.fetch_all_features(
    query_fn=custom_query,
    batch_size=100,
    max_batches=10
)
```

**Why this approach:**
- ✅ Simple cases use default behavior
- ✅ Complex cases use custom function
- ✅ Avoids creating multiple fetch methods
- ✅ Flexible and extensible

---

## Pros and Cons of the Options

### Direct Client Usage

* **Good:** Simple, no abstraction overhead
* **Good:** Direct access to all client features
* **Bad:** Business logic coupled to data source
* **Bad:** Hard to test (need real database)
* **Bad:** Hard to switch data sources
* **Bad:** Code duplication for different clients

### Simple Base Class

* **Good:** Single abstraction
* **Bad:** Hard to handle different client APIs
* **Bad:** Lots of if-else for different sources
* **Bad:** Violates Open-Closed Principle

### Factory Pattern + Strategy Pattern ✅

* **Good:** Clean separation per data source
* **Good:** Easy to extend (add new sources)
* **Good:** Auto-detection of client type
* **Good:** Supports custom queries
* **Good:** Type-safe with base class
* **Bad:** More classes to maintain
* **Bad:** Registry pattern adds slight complexity

### Repository Pattern over Data Layer

* **Good:** Additional abstraction layer
* **Good:** Better for complex domain logic
* **Bad:** Overkill for this layer
* **Bad:** Too many layers for data access
* **Note:** Repository will be added on top of this layer

---

## Implementation Plan

### Phase 1: Core Implementation ✅
- [x] BaseDataset abstract class
- [x] DatasetFactory with registry
- [x] create_dataset convenience function
- [x] Example implementations (Supabase, Postgres, MongoDB)

### Phase 2: Enhancements
- [ ] Add more concrete implementations
- [ ] Connection pooling (ADR-003)
- Repository uses BaseClient
- Repository adds domain-specific logic
- Repository handles complex queries and business rules

```python
class ReviewRepository:
    def __init__(self, client: BaseClient):
        self.client = client
    
    def get_unlabeled_reviews(self, limit: int = 100):
        """Domain-specific method using client"""
        return self.client.get_reviews_without_labels(limit=limit)
    
    def get_batch_aspects(self, batch_id: int) -> List[str]:
        """Complex query handled by repository"""
        # Repository can add business logic here
        pass
```

**Service Layer** (ADR-006)
- Services use Repository
- SADR-006: Auto-Labeling Service](006-auto-labeling-service.md)
* Implementation: `review_radar/data/`
* Tests: `tests/unit/test_data/`

---

## Implementation Status

**Files Created:**
- ✅ `review_radar/data/base_client.py` - Abstract base class
- ✅ `review_radar/data/client_factory.py` - Factory with registry
- ✅ `review_radar/data/supabase_client.py` - Supabase implementation
- ✅ `tests/unit/test_data/test_client_factory.py` - Factory tests (29 tests)
- ✅ `tests/unit/test_data/test_supabase_client.py` - Client tests (28 tests)

**Coverage:**
- `client_factory.py`: 100%
- `supabase_client.py`: 100%
- `base_client.py`: 85% (abstract methods)

---

## Notes

- Python's duck typing makes this pattern very natural
- No need for explicit interfaces (unlike Java/C++)
- Type hints provide IDE support without runtime overhead
- Factory auto-detection is convenient but can be overridden
- **This layer focuses on database access only - no business logic**
- Specific methods preferred over generic query methods
- Each new operation requires a new method (explicit > implicit)
        return self.dataset.fetch_all_features(
            query_filter={"is_labeled": False}
        )


---

## Links

* [ADR-001: Overall Architecture](001-overall-architecture.md)
* [ADR-003: Service Layer Design](003-service-layer-design.md)
* [Factory Pattern Examples](../../examples/factory_example.py)
* [Dataset Fetch Strategies](../../examples/dataset_fetch_strategies.py)

---

## Notes

- Python's duck typing makes this pattern very natural
- No need for explicit interfaces (unlike Java/C++)
- Type hints provide IDE support without runtime overhead
- Factory auto-detection is convenient but can be overridden
- This layer focuses on data access, not business logic
