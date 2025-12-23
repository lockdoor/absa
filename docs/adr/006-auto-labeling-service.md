# ADR-006: Auto-Labeling Service Design

**Status:** Proposed

**Date:** 2025-12-23

**Deciders:** ML Engineering Team, Backend Team

**Related:** ADR-001, ADR-003

---

## Context and Problem Statement

ระบบต้องการ labels สำหรับ reviews เพื่อใช้ใน training และ validation แต่การ label ด้วยมนุษย์ใช้เวลานานและมีค่าใช้จ่ายสูง เราต้องการระบบ auto-labeling ที่ใช้ LLM (Gemini Flash) ช่วยในการ label reviews โดยอัตโนมัติ

**Requirements:**
- Fetch reviews ที่ยังไม่มี labels
- ส่ง review ไป LLM API (Gemini Flash) เพื่อ label aspects และ sentiments
- Update labels กลับไปที่ database
- รองรับการสลับ LLM providers (Gemini, GPT, Claude)
- จัดการ errors และ retries
- Track labeling quality และ cost

---

## Decision Drivers

* **Automation:** ลด manual labeling effort
* **Cost Efficiency:** ใช้ cheaper LLM (Flash models)
* **Flexibility:** สลับ LLM providers ได้
* **Quality Control:** Validate labels ก่อน save
* **Observability:** Track metrics และ costs
* **Scalability:** Process multiple reviews in batch

---

## Design: Service-First Approach

### Layer Architecture

```
┌──────────────────────────────────────┐
│     LabelingService (Orchestrator)   │ ← High-level workflow
├──────────────────────────────────────┤
│  - fetch_and_label_batch()           │
│  - validate_and_save()               │
│  - monitor_quality()                 │
└──────────────────────────────────────┘
           ↓              ↓
    ┌──────────┐    ┌────────────────┐
    │ Review   │    │ Labeling       │
    │Repository│    │ Provider       │
    └──────────┘    │ (Strategy)     │
           ↓        └────────────────┘
    ┌──────────┐           ↓
    │ Dataset  │    ┌────────────────┐
    │ (Factory)│    │ Gemini API     │
    └──────────┘    │ GPT API        │
           ↓        │ Claude API     │
    ┌──────────┐    └────────────────┘
    │ Database │
    └──────────┘
```

---

## Service Layer Design

### 1. LabelingService (Main Orchestrator)

**Responsibility:** Orchestrate the complete auto-labeling workflow

**Methods:**
```python
class LabelingService:
    def label_batch(batch_id: int, limit: int) -> LabelingResult
    def label_unlabeled_reviews(batch_size: int, max_batches: int)
    def validate_labels(labels: Dict) -> ValidationResult
    def save_labels(review_id: int, labels: Dict, metadata: Dict)
    def get_labeling_stats(batch_id: int) -> Stats
```

**Workflow:**
1. Fetch unlabeled reviews from repository
2. Send to LLM provider for labeling
3. Validate labels
4. Save to database
5. Track metrics and costs

---

### 2. LabelingProvider (Strategy Pattern)

**Responsibility:** Abstract LLM API calls

**Interface:**
```python
class BaseLabelingProvider(ABC):
    @abstractmethod
    def label_review(text: str, aspects: List[str]) -> LabelResult
    
    @abstractmethod
    def label_batch(texts: List[str], aspects: List[str]) -> List[LabelResult]
    
    def get_cost() -> float
    def get_model_info() -> ModelInfo
```

**Implementations:**
- GeminiLabelingProvider
- GPTLabelingProvider  
- ClaudeLabelingProvider
- HumanLabelingProvider (fallback)

---

### 3. ReviewRepository

**Responsibility:** Data access for reviews

**Methods:**
```python
class ReviewRepository:
    def get_unlabeled_reviews(batch_id: int, limit: int) -> DataFrame
    def get_review_by_id(review_id: int) -> Review
    def update_labels(review_id: int, labels: Dict, metadata: Dict)
    def get_labeling_progress(batch_id: int) -> Progress
    def get_reviews_for_validation(sample_size: int) -> DataFrame
```

---

## Data Flow

```
1. Service Request
   ↓
2. LabelingService.label_batch(batch_id=123, limit=100)
   ↓
3. ReviewRepository.get_unlabeled_reviews(batch_id, limit)
   ↓ Returns DataFrame
4. For each review:
   LabelingProvider.label_review(text, aspects)
   ↓ Returns LabelResult
5. ValidationService.validate(labels)
   ↓ Returns ValidationResult
6. If valid:
   ReviewRepository.update_labels(review_id, labels, metadata)
   ↓
7. Return LabelingResult (success, failed, costs)
```

---

## Label Schema

### Input to LLM
```json
{
  "text": "อาหารอร่อยมาก แต่บริการช้าไปหน่อย",
  "aspects": ["food", "service", "price", "ambiance"],
  "instructions": "Extract mentioned aspects and their sentiments"
}
```

### Output from LLM (labels field in DB)
```json
{
  "aspects": {
    "food": {
      "mentioned": true,
      "sentiment": "positive",
      "confidence": 0.95,
      "snippet": "อาหารอร่อยมาก"
    },
    "service": {
      "mentioned": true,
      "sentiment": "negative",
      "confidence": 0.88,
      "snippet": "บริการช้าไปหน่อย"
    },
    "price": {
      "mentioned": false,
      "sentiment": null,
      "confidence": null,
      "snippet": null
    }
  },
  "overall_sentiment": "neutral",
  "labeling_metadata": {
    "provider": "gemini-flash-2.0",
    "timestamp": "2025-12-23T10:00:00Z",
    "cost": 0.0001,
    "processing_time_ms": 150,
    "validation_passed": true
  }
}
```

---

## Implementation Priority

### Phase 1: Core Service (Week 1)
```python
services/
└── labeling/
    ├── __init__.py
    ├── labeling_service.py      # Main orchestrator
    ├── validation_service.py     # Label validation
    └── providers/
        ├── __init__.py
        ├── base_provider.py      # Abstract base
        └── gemini_provider.py    # Gemini implementation
```

### Phase 2: Repository Layer (Week 1)
```python
repositories/
├── __init__.py
├── base_repository.py
└── review_repository.py         # CRUD for reviews
```

### Phase 3: Additional Providers (Week 2)
```python
services/labeling/providers/
├── gpt_provider.py
├── claude_provider.py
└── human_provider.py            # Manual labeling interface
```

### Phase 4: Monitoring & Analytics (Week 2)
```python
services/labeling/
├── monitoring_service.py        # Track metrics
└── cost_tracking_service.py     # Cost analysis
```

---

## Example Usage

### Simple Labeling
```python
# Setup
gemini_provider = GeminiLabelingProvider(api_key="...")
review_repo = ReviewRepository(dataset=create_dataset(client))
labeling_service = LabelingService(
    repository=review_repo,
    provider=gemini_provider
)

# Label a batch
result = labeling_service.label_batch(
    batch_id=123,
    limit=100
)

print(f"Labeled: {result.success_count}")
print(f"Failed: {result.failed_count}")
print(f"Total cost: ${result.total_cost}")
```

### Batch Processing
```python
# Label all unlabeled reviews
stats = labeling_service.label_unlabeled_reviews(
    batch_size=50,
    max_batches=20
)
```

### Switch Provider
```python
# Switch to GPT for comparison
gpt_provider = GPTLabelingProvider(api_key="...")
labeling_service.set_provider(gpt_provider)
```

---

## Error Handling Strategy

### Retry Logic
```python
@retry(max_attempts=3, backoff=exponential)
def label_review(text: str):
    # API call
    pass
```

### Fallback Strategy
1. Primary: Gemini Flash (cheap, fast)
2. Fallback 1: GPT-4o-mini
3. Fallback 2: Flag for human labeling

### Error Types
- **API Error:** Retry with backoff
- **Rate Limit:** Queue and process later
- **Invalid Response:** Log and flag for review
- **Validation Failed:** Save with warning flag

---

## Cost Management

### Cost Tracking
```python
class CostTracker:
    def track_call(provider: str, tokens: int, cost: float)
    def get_daily_cost() -> float
    def get_cost_per_review() -> float
    def alert_if_budget_exceeded(threshold: float)
```

### Budget Limits
```python
labeling_service.set_daily_budget(max_usd=10.0)
labeling_service.set_cost_alert(threshold=0.80)  # 80% of budget
```

---

## Quality Control

### Validation Rules
```python
class LabelValidator:
    def validate_label(label: Dict) -> ValidationResult:
        # 1. Check required fields
        # 2. Validate sentiment values
        # 3. Check confidence thresholds
        # 4. Verify aspect mentions
        # 5. Detect inconsistencies
```

### Human Review Triggers
- Confidence < 0.70
- Contradictory sentiments
- Unusual aspect combinations
- First N samples of each batch (for quality check)

---

## Monitoring Metrics

### Key Metrics
- **Throughput:** Reviews labeled per hour
- **Cost:** USD per review
- **Quality:** Validation pass rate
- **Latency:** API response time
- **Error Rate:** Failed labeling attempts

### Dashboards
```python
monitoring_service.get_metrics(batch_id) → {
    "total_reviews": 1000,
    "labeled": 950,
    "failed": 50,
    "avg_confidence": 0.87,
    "total_cost": 2.50,
    "avg_latency_ms": 180
}
```

---

## Security & Privacy

### API Key Management
```python
# Use environment variables
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

# Or secret manager
from cloud_secrets import get_secret
api_key = get_secret("gemini-api-key")
```

### Data Privacy
- ✅ Reviews sent to LLM are public data only
- ✅ No PII in prompts
- ✅ Comply with LLM provider ToS
- ✅ Optional: Self-hosted LLM for sensitive data

---

## Future Enhancements

1. **Active Learning:** Prioritize uncertain samples for human review
2. **Multi-Model Ensemble:** Combine predictions from multiple LLMs
3. **Fine-tuned Models:** Train custom models on labeled data
4. **Real-time Labeling:** Stream processing for live data
5. **Feedback Loop:** Learn from human corrections

---

## Decision Outcome

**Chosen Approach:** Service-First Design with Strategy Pattern

**Justification:**
- ✅ Clean separation: Service orchestrates, Repository accesses data
- ✅ Flexible: Easy to switch LLM providers
- ✅ Testable: Mock providers and repositories
- ✅ Scalable: Process in batches
- ✅ Observable: Built-in monitoring and cost tracking

### Next Steps
1. ✅ Design service interfaces (this document)
2. 🔄 Implement LabelingService skeleton
3. 🔄 Implement GeminiLabelingProvider
4. 🔄 Implement ReviewRepository
5. ⏳ Add validation and error handling
6. ⏳ Add monitoring and cost tracking
7. ⏳ Integration testing
8. ⏳ Production deployment

---

## Links

* [ADR-001: Overall Architecture](001-overall-architecture.md)
* [ADR-003: Service Layer Design](003-service-layer-design.md)
* [ERD Documentation](../ERD.md)

---

## Notes

- Start with Gemini Flash (cheapest for testing)
- Monitor costs closely in initial phase
- Human validation for first 100 labels to establish baseline
- Consider rate limits and quotas
- Keep fallback to manual labeling always available
