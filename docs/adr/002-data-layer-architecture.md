# ADR-002: Data Layer Architecture

**Status:** Accepted

**Date:** 2025-12-22 (Updated: 2025-12-25)

**Deciders:** Data Engineering Team, ML Engineering Team

**Related:** ADR-001, ADR-003

---

## Context and Problem Statement

ระบบต้องรองรับการทำงานกับหลาย database sources (Supabase, PostgreSQL) และหลายประเภทข้อมูล (Review, Batch, Aspect) สำหรับ CRUD operations เราต้องการ abstraction layer ที่ทำให้ business logic (Repository, Service) ไม่ต้องสนใจว่าข้อมูลมาจาก database ไหนและเป็นข้อมูลประเภทไหน

**Key Requirements:**
- รองรับหลาย database sources (Supabase, PostgreSQL)
- รองรับหลายประเภทข้อมูล (Review, Batch, Aspect)
- Abstract database access details
- ง่ายต่อการเพิ่ม database client หรือ data type ใหม่
- มี specific methods สำหรับแต่ละ operation
- Type-safe และ testable
- Singleton pattern สำหรับการจัดการ connections

---

## Decision Drivers

* **Flexibility:** เพิ่ม data source หรือ data type ใหม่ได้ง่าย
* **Abstraction:** Business logic ไม่ต้องรู้จัก data source
* **Type Safety:** ใช้ type hints และ Literal types เพื่อ compile-time checking
* **Extensibility:** รองรับ custom queries
* **Testability:** Mock ได้ง่ายสำหรับ unit tests
* **Resource Management:** Singleton pattern ป้องกัน duplicate connections
* **Python Idioms:** ใช้ Pythonic patterns (ABC, properties, template method)

---

## Considered Options

1. **Direct Client Usage** - ใช้ database client โดยตรงใน business logic
2. **Simple Base Class** - Base class เดียว implement ทุก data source
3. **Factory Pattern + Strategy Pattern** - Factory สร้าง client, Strategy สำหรับแต่ละ data type
4. **Factory Pattern + Template Method + Singleton** - เพิ่ม Template Method และ Singleton management

---

## Decision Outcome

**Chosen option:** "Factory Pattern + Template Method + Singleton Pattern"

**Justification:**
- **Factory Pattern:** สร้าง appropriate instance based on data type และ client type
- **Template Method:** BaseData ให้ common functionality (logging, client access)
- **Strategy Pattern:** แต่ละ data type (ReviewData, BatchData, AspectData) มี abstract methods ของตัวเอง
- **Singleton Pattern:** DataFactory จัดการ singleton instances ต่อ (data_type, client_type) combination
- **Type Safety:** ใช้ Literal types สำหรับ data_type และ client_type
- ใช้ specific methods แทน generic query functions
- ไม่ต้อง explicit casting

### Positive Consequences

* ✅ เพิ่ม database client หรือ data type ใหม่ง่าย
* ✅ Business logic ใช้ `BaseData` type เดียว
* ✅ Type-safe with Literal types (compile-time checking)
* ✅ Singleton pattern ป้องกัน duplicate connections
* ✅ Factory centralizes client creation and environment configuration
* ✅ Template Method pattern ให้ common functionality (logging, client access)
* ✅ Easy to test with mock clients
* ✅ **Returns List[Dict[str, Any]] for clean architecture**

### Negative Consequences

* ⚠️ ต้องสร้าง abstract class และ concrete class สำหรับแต่ละ data type
* ⚠️ ต้องเพิ่ม method ใหม่เมื่อมี operation ใหม่
* ⚠️ Singleton pattern เพิ่ม complexity ในการ testing (ต้อง reset)

---

## Architecture Design

### Layer Structure

```
BaseData (ABC, Template Method)
    ↓
ReviewData (ABC)  BatchData (ABC)  AspectData (ABC)
    ↓                  ↓                  ↓
ReviewDataSupabaseClient  BatchDataSupabaseClient  AspectDataSupabaseClient
ReviewDataPostgresClient  BatchDataPostgresClient  AspectDataPostgresClient
```

### Return Type: List[Dict[str, Any]]

**Decision:** Return `List[Dict[str, Any]]` from data layer methods

**Rationale:**
- ✅ **Clean Architecture:** Repository layer ไม่ต้องพึ่งพา pandas
- ✅ **Type Safety:** Native Python types ใช้กับ type hints ได้ชัดเจน
- ✅ **Serialization:** แปลงเป็น JSON ได้ง่ายสำหรับ API responses
- ✅ **Testing:** Mock และ assertions ง่ายกว่า DataFrame
- ✅ **Flexibility:** Service layer เลือกใช้ pandas ได้ตามต้องการ

### 1. BaseData (Template Method Pattern)

```python
from abc import ABC
from typing import Any, Optional
from logging import Logger

class BaseData(ABC):
    """
    Abstract base class สำหรับทุก data layer classes
    
    ใช้ Template Method pattern เพื่อให้ common functionality:
    - Client management
    - Logging
    """
    
    def __init__(self, client: Any, logger: Optional[Logger] = None):
        self._client = client
        self._logger = logger
    
    @property
    def client(self) -> Any:
        """Get database client (read-only)"""
        return self._client
    
    @property
    def logger(self) -> Optional[Logger]:
        """Get logger (read-only)"""
        return self._logger
    
    def _log(self, message: str, level: str = "info", **kwargs) -> None:
        """Helper method for logging"""
        if self._logger:
            log_method = getattr(self._logger, level, self._logger.info)
            log_method(message, extra=kwargs)
```

**Design Principles:**
- Template Method: ให้ common functionality ผ่าน `_log()` และ properties
- Protected attributes: `_client`, `_logger` (ใช้ underscore)
- Read-only access: ผ่าน `@property` decorators

### 2. ReviewData (Abstract Interface)

```python
from abc import abstractmethod
from typing import List, Dict, Any

class ReviewData(BaseData):
    """Abstract class สำหรับ review operations"""
    
    @abstractmethod
    def get_unlabeled_reviews(
        self,
        batch_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Fetch reviews ที่ยังไม่มี labels"""
        pass
    
    @abstractmethod
    def get_reviews_by_ids(
        self,
        review_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """Fetch reviews ตาม IDs"""
        pass
    
    @abstractmethod
    def update_reviews(
        self,
        review_id: int,
        update_data: Dict[str, Any]
    ) -> None:
        """Update review เดียว"""
        pass
    
    @abstractmethod
    def bulk_update_reviews(
        self,
        updates: List[Dict[str, Any]]
    ) -> int:
        """Bulk update หลาย reviews"""
        pass
```

### 3. ReviewDataSupabaseClient (Concrete Implementation)

```python
from supabase import Client
from .review_data import ReviewData

class ReviewDataSupabaseClient(ReviewData):
    """Supabase implementation ของ ReviewData"""
    
    def get_unlabeled_reviews(
        self,
        batch_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        self._log(
            f"Fetching unlabeled reviews for batch {batch_id}",
            level="info",
            batch_id=batch_id
        )
        
        try:
            response = (
                self.client
                .table('reviews')
                .select('*')
                .eq('batch_id', batch_id)
                .is_('labels', 'null')
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            data = response.data if response.data else []
            self._log(f"Found {len(data)} reviews", level="info")
            return data
            
        except Exception as e:
            self._log(f"Error: {str(e)}", level="error")
            raise
```

### 4. DataFactory (Factory + Singleton)

```python
import os
from typing import Optional, Dict, Tuple, Literal
from logging import Logger

DataType = Literal['review', 'batch', 'aspect']
ClientType = Literal['supabase', 'postgres']

class DataFactory:
    """Factory with Singleton management"""
    
    _instances: Dict[Tuple[str, str], BaseData] = {}
    
    @classmethod
    def create(
        cls,
        data_type: DataType = 'review',
        client_type: ClientType = 'supabase',
        logger: Optional[Logger] = None
    ) -> BaseData:
        """
        Create or get existing instance (Singleton)
        
        Args:
            data_type: 'review', 'batch', or 'aspect'
            client_type: 'supabase' or 'postgres'
            logger: Optional logger (ignored if exists)
        
        Returns:
            Data instance (singleton per combination)
        """
        # Validate
        if data_type not in ('review', 'batch', 'aspect'):
            raise ValueError(f"Invalid data_type: {data_type}")
        
        if client_type not in ('supabase', 'postgres'):
            raise ValueError(f"Invalid client_type: {client_type}")
        
        # Singleton check
        key = (data_type, client_type)
        if key not in cls._instances:
            cls._instances[key] = cls._create_instance(
                data_type, client_type, logger
            )
        
        return cls._instances[key]
    
    @classmethod
    def reset(
        cls,
        data_type: Optional[str] = None,
        client_type: Optional[str] = None
    ) -> None:
        """Reset instances (for testing)"""
        if data_type is None and client_type is None:
            cls._instances.clear()
        else:
            keys_to_remove = [
                key for key in cls._instances.keys()
                if (data_type is None or key[0] == data_type)
                and (client_type is None or key[1] == client_type)
            ]
            for key in keys_to_remove:
                del cls._instances[key]
    
    @classmethod
    def get_instance(
        cls,
        data_type: str,
        client_type: str
    ) -> Optional[BaseData]:
        """Get existing instance without creating"""
        return cls._instances.get((data_type, client_type))
```

**Key Features:**
- **Type Safety:** Literal types for compile-time checking
- **Singleton per combination:** แต่ละ (data_type, client_type) มี instance เดียว
- **Environment-based:** อ่าน credentials จาก environment variables
- **Reset capability:** สำหรับ testing

### 5. Usage Examples

```python
from review_radar.data import DataFactory
import logging

# Basic usage
review_data = DataFactory.create('review', 'supabase')
reviews = review_data.get_unlabeled_reviews(batch_id=1, limit=100)

# With logger
logger = logging.getLogger(__name__)
review_data = DataFactory.create('review', 'supabase', logger)

# Singleton behavior
data1 = DataFactory.create('review', 'supabase')
data2 = DataFactory.create('review', 'supabase')
assert data1 is data2  # True - same instance

# Reset for testing
DataFactory.reset()
```

---

## Design Philosophy: Specific Methods vs Generic

### Chosen: Specific Methods ✅

แต่ละ operation มี method เฉพาะ:
```python
client.get_unlabeled_reviews(limit=100)
client.get_reviews_by_ids([1, 2, 3])
client.update_reviews(review_id=1, data={...})
client.bulk_update_reviews(updates=[...])
```

**Rationale:**
- ✅ **Clear Intent:** method name บอกได้ชัดเจนว่าทำอะไร
- ✅ **Type Safety:** parameters มี type hints ชัดเจน
- ✅ **Easy to Test:** mock แต่ละ method ได้ง่าย
- ✅ **IDE Support:** autocomplete แสดง available operations
- ✅ **Maintainability:** แก้ไข method เดียวไม่กระทบอื่น

### Alternative: Generic Methods ❌

```python
# ไม่ใช้แนวทางนี้
client.query(table='reviews', filter={...})
```

**Why Not:**
- ❌ Unclear intent
- ❌ Hard to test
- ❌ No type safety
- ❌ Poor IDE support

---

## Implementation Roadmap

### Phase 1: Core Implementation ✅ Complete
- [x] BaseData abstract class with template method pattern
- [x] ReviewData abstract interface
- [x] ReviewDataSupabaseClient concrete implementation
- [x] DataFactory with singleton pattern and Literal types
- [x] Unit tests (84 tests total, 95%+ coverage)
  - [x] BaseData tests (15 tests, 100% coverage)
  - [x] ReviewData tests (23 tests, 75% coverage)
  - [x] ReviewDataSupabaseClient tests (22 tests, 95% coverage)
  - [x] DataFactory tests (24 tests, 97% coverage)

### Phase 2: Additional Data Types (Future)
- [ ] BatchData abstract interface
- [ ] BatchDataSupabaseClient implementation
- [ ] AspectData abstract interface
- [ ] AspectDataSupabaseClient implementation
- [ ] Update DataFactory to support new types

### Phase 3: Additional Client Types (Future)
- [ ] ReviewDataPostgresClient implementation
- [ ] BatchDataPostgresClient implementation
- [ ] AspectDataPostgresClient implementation
- [ ] Update DataFactory for postgres support

### Phase 4: Enhancements (Future)
- [ ] Connection pooling
- [ ] Caching layer
- [ ] Retry logic
- [ ] Async support
- [ ] Transaction support

---

## Architecture Layers

### Data Layer (This ADR)
- **BaseData:** Abstract base with template method
- **ReviewData, BatchData, AspectData:** Abstract interfaces
- **Concrete implementations:** Supabase, PostgreSQL clients
- **DataFactory:** Factory with singleton management
- **Returns:** `List[Dict[str, Any]]`

### Repository Layer (ADR-003)
```python
class ReviewRepository:
    def __init__(self, logger=None):
        self._review_data = DataFactory.create('review', 'supabase', logger)
    
    def get_pending_reviews(self, batch_id: int):
        return self._review_data.get_unlabeled_reviews(batch_id, limit=100)
```

### Service Layer
- Services use Repository
- Orchestrate complex workflows
- Add business logic

---

## Pros and Cons Comparison

### Direct Client Usage
* **Good:** Simple, no abstraction
* **Bad:** Coupled to data source, hard to test

### Simple Base Class
* **Good:** Single abstraction
* **Bad:** Hard to handle different APIs, violates Open-Closed

### Factory + Template Method + Singleton ✅
* **Good:** Clean separation, type-safe, resource management
* **Good:** Easy to extend, test, and maintain
* **Bad:** More classes, singleton testing complexity

---

## Implementation Status

**Files Created:**
- ✅ `review_radar/data/base_data.py` (18 statements, 100% coverage)
- ✅ `review_radar/data/review_data.py` (16 statements, 75% coverage)
- ✅ `review_radar/data/review_data_supabase_client.py` (63 statements, 95% coverage)
- ✅ `review_radar/data/data_factory.py` (59 statements, 97% coverage)
- ✅ `review_radar/data/__init__.py` (exports: BaseData, ReviewData, ReviewDataSupabaseClient, DataFactory)
- ✅ `tests/unit/test_data/test_base_data.py` (15 tests)
- ✅ `tests/unit/test_data/test_review_data.py` (23 tests)
- ✅ `tests/unit/test_data/test_review_data_supabase_client.py` (22 tests)
- ✅ `tests/unit/test_data/test_data_factory.py` (24 tests)
- ✅ `examples/factory_example.py` (8 usage examples)

**Test Coverage:**
- Total: 84 tests, 100% pass rate
- Average coverage: 92%
- All core functionality tested

**Documentation:**
- ✅ Class diagram: `docs/data_layer/class_diagram.md`
- ✅ Usage examples: `examples/factory_example.py`
- ✅ ADR document: This file

---

## Links

* [ADR-001: Overall Architecture](001-overall-architecture.md)
* [ADR-003: Repository Layer](003-repository-layer.md)
* [Class Diagram](../data_layer/class_diagram.md)
* [Factory Examples](../../examples/factory_example.py)

---

## Notes

- Python's ABC และ type hints ทำให้ pattern นี้เป็นธรรมชาติ
- Literal types ให้ type safety โดยไม่ต้องใช้ enum
- Factory pattern eliminates การสร้าง client ซ้ำซ้อน
- Singleton pattern จัดการ database connections อย่างมีประสิทธิภาพ
- Template Method pattern ลด code duplication
- **This layer focuses on database access only - no business logic**
- Specific methods preferred over generic (explicit > implicit)
- Returns native Python types for clean architecture

