# ADR-002: Data Layer Architecture

**Status:** Accepted

**Date:** 2025-12-22

**Deciders:** Data Engineering Team, ML Engineering Team

**Related:** ADR-001

---

## Context and Problem Statement

ระบบต้องรองรับการเก็บข้อมูลจากหลาย data sources (Supabase, PostgreSQL, MongoDB, CSV files) และต้องมีวิธีการ fetch ข้อมูลที่แตกต่างกันตาม client type แต่ละตัว เราต้องการ abstraction ที่ทำให้ business logic ไม่ต้องสนใจว่าข้อมูลมาจากไหน

**Key Requirements:**
- รองรับหลาย data sources
- Abstract data access details
- ง่ายต่อการเพิ่ม data source ใหม่
- รองรับ custom query logic
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
- Factory Pattern: สร้าง appropriate dataset instance based on client type
- Strategy Pattern: แต่ละ dataset implement fetch logic ของตัวเอง
- รองรับ custom query functions สำหรับ complex queries
- ใช้ polymorphism ของ Python (duck typing)
- ไม่ต้อง explicit casting

### Positive Consequences

* ✅ เพิ่ม data source ใหม่ง่าย (implement + register)
* ✅ Business logic ใช้ `BaseDataset` type เดียว
* ✅ Auto-detect client type
* ✅ รองรับ default และ custom queries
* ✅ Type-safe with Python type hints
* ✅ Easy to test with mock datasets

### Negative Consequences

* ⚠️ ต้องสร้าง dataset class สำหรับแต่ละ data source
* ⚠️ Registry pattern เพิ่ม complexity เล็กน้อย

---

## Architecture Design

### 1. Base Dataset (Abstract Base Class)

```python
class BaseDataset(ABC):
    """Base class for all datasets"""
    
    def __init__(self, client: Any):
        self.client = client
        self.df: DataFrame | None = None
    
    @abstractmethod
    def fetch_all_features(
        self,
        table_name: str,
        batch_size: int,
        max_batches: int,
        query_filter: Optional[Dict] = None,
        query_fn: Optional[Callable] = None,
        verbose: bool = False
    ) -> DataFrame:
        pass
    
    @abstractmethod
    def create_dataset(self) -> Dataset:
        pass
    
    @abstractmethod
    def create_dataloader(
        self, 
        batch_size: int, 
        shuffle: bool
    ) -> DataLoader:
        pass
```

### 2. Factory Pattern

```python
class DatasetFactory:
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, client_type: str):
        """Decorator to register dataset classes"""
        def decorator(dataset_class: type):
            cls._registry[client_type] = dataset_class
            return dataset_class
        return decorator
    
    @classmethod
    def create(cls, client: Any, client_type: str = None) -> BaseDataset:
        """Create appropriate dataset based on client type"""
        if client_type is None:
            client_type = cls._detect_client_type(client)
        
        dataset_class = cls._registry.get(client_type)
        return dataset_class(client=client)
```

### 3. Concrete Implementations

```python
@DatasetFactory.register('supabase')
class SupabaseDataset(BaseDataset):
    """Dataset for Supabase client"""
    
    def fetch_all_features(self, ...) -> DataFrame:
        # Supabase-specific fetch logic
        pass

@DatasetFactory.register('postgres')
class PostgresDataset(BaseDataset):
    """Dataset for PostgreSQL client"""
    
    def fetch_all_features(self, ...) -> DataFrame:
        # PostgreSQL-specific fetch logic
        pass
```

### 4. Usage

```python
# Factory creates appropriate dataset
dataset = create_dataset(supabase_client)  # auto-detect

# Business logic uses BaseDataset type
def process(dataset: BaseDataset):
    df = dataset.fetch_all_features(...)
    dataset.create_dataset()
    loader = dataset.create_dataloader(...)
```

---

## Fetch Strategy

### Default Behavior
Each dataset implements standard fetch with filters:
```python
df = dataset.fetch_all_features(
    table_name="reviews",
    query_filter={"rating": 5},
    batch_size=100,
    max_batches=10
)
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
- [ ] Connection pooling
- [ ] Caching layer
- [ ] Retry logic for failed fetches
- [ ] Async support for concurrent fetches

### Phase 3: Testing
- [ ] Unit tests with mock clients
- [ ] Integration tests with test databases
- [ ] Performance benchmarks

---

## Related Patterns

**Next Layer:** Repository Pattern
- Repository will use BaseDataset
- Repository adds domain-specific logic
- Repository handles transactions

```python
class ReviewRepository:
    def __init__(self, dataset: BaseDataset):
        self.dataset = dataset
    
    def get_unlabeled_reviews(self):
        return self.dataset.fetch_all_features(
            query_filter={"is_labeled": False}
        )
```

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
