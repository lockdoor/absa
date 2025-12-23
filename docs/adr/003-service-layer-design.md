# ADR-003: Service Layer Design

**Status:** Proposed

**Date:** 2025-12-22

**Deciders:** Backend Team, ML Engineering Team

**Related:** ADR-001, ADR-002

---

## Context and Problem Statement

ระบบมี business logic ที่ซับซ้อนหลายอย่าง เช่น training workflow, evaluation pipeline, prediction service, และ model monitoring เราต้องการ layer ที่ orchestrate logic เหล่านี้และประสานงานระหว่าง repositories, models, และ pipelines

**Key Requirements:**
- Orchestrate complex workflows
- Coordinate between multiple components
- Handle transactions and error recovery
- Reusable business logic
- Easy to test with mocks

---

## Decision Drivers

* **Separation of Concerns:** แยก business logic จาก data access
* **Reusability:** Logic ใช้ซ้ำได้ใน contexts ต่างๆ
* **Testability:** Test ได้โดยไม่ต้อง database จริง
* **Transaction Management:** Handle success/failure scenarios
* **Maintainability:** Easy to understand and modify
* **Single Responsibility:** Each service has one clear purpose

---

## Considered Options

1. **No Service Layer** - Business logic อยู่ใน API handlers/notebooks โดยตรง
2. **Fat Models** - Business logic อยู่ใน model classes
3. **Service Layer Pattern** - Dedicated service classes for business logic
4. **CQRS Pattern** - Separate read and write services

---

## Decision Outcome

**Chosen option:** "Service Layer Pattern"

**Justification:**
- แยก business logic ออกจาก API/UI layer
- ง่ายต่อการ reuse logic ใน contexts ต่างๆ
- Test ได้ง่ายด้วย mock repositories
- เหมาะกับขนาดและความซับซ้อนของโปรเจค
- รองรับ dependency injection

### Positive Consequences

* ✅ Business logic อยู่ที่เดียว (single source of truth)
* ✅ Reusable across API, CLI, notebooks
* ✅ Easy to test with dependency injection
* ✅ Clear transaction boundaries
* ✅ Orchestrate complex workflows
* ✅ Handle cross-cutting concerns (logging, monitoring)

### Negative Consequences

* ⚠️ เพิ่ม layer และ complexity
* ⚠️ ต้องระวังไม่ให้ service ทำงานมากเกินไป (God object)

---

## Service Architecture

### Service Categories

```
services/
├── data_services/
│   ├── collection_service.py     # Data collection workflows
│   └── labeling_service.py       # Labeling workflows
├── ml_services/
│   ├── training_service.py       # Training orchestration
│   ├── evaluation_service.py     # Model evaluation
│   ├── prediction_service.py     # Inference workflows
│   └── monitoring_service.py     # Model monitoring
└── reporting_services/
    ├── report_service.py          # Report generation
    └── dashboard_service.py       # Dashboard data prep
```

---

## Service Design Pattern

### Base Service Structure

```python
class BaseService(ABC):
    """Base class for all services"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or get_logger(self.__class__.__name__)
    
    def _log_operation(self, operation: str, **kwargs):
        """Log service operations"""
        self.logger.info(f"{operation}", extra=kwargs)
    
    def _handle_error(self, error: Exception, context: str):
        """Centralized error handling"""
        self.logger.error(f"Error in {context}: {error}")
        raise
```

---

## Example Services

### 1. TrainingService

```python
class TrainingService(BaseService):
    """Service for orchestrating model training"""
    
    def __init__(
        self,
        review_repository: ReviewRepository,
        model_repository: ModelRepository,
        training_pipeline: TrainingPipeline,
        logger: Optional[Logger] = None
    ):
        super().__init__(logger)
        self.review_repo = review_repository
        self.model_repo = model_repository
        self.pipeline = training_pipeline
    
    def train_new_model(
        self,
        config: TrainingConfig
    ) -> TrainingResult:
        """
        Complete training workflow:
        1. Fetch labeled data
        2. Prepare training data
        3. Train model
        4. Validate model
        5. Save model if successful
        """
        self._log_operation("Starting training", config=config.dict())
        
        try:
            # 1. Fetch data
            data = self.review_repo.get_labeled_data(
                min_samples=config.min_samples
            )
            
            # 2. Prepare data
            train_data, val_data, test_data = self.pipeline.prepare_data(
                data, config
            )
            
            # 3. Train
            model, history = self.pipeline.train(
                train_data, val_data, config
            )
            
            # 4. Validate
            metrics = self.pipeline.evaluate(model, test_data)
            
            if metrics['f1_score'] < config.min_f1_threshold:
                raise ValueError(f"Model F1 too low: {metrics['f1_score']}")
            
            # 5. Save
            model_id = self.model_repo.save_model(
                model, metrics, config
            )
            
            self._log_operation("Training completed", model_id=model_id)
            
            return TrainingResult(
                model_id=model_id,
                metrics=metrics,
                history=history
            )
            
        except Exception as e:
            self._handle_error(e, "train_new_model")
    
    def retrain_existing_model(
        self,
        model_id: str,
        additional_data: Optional[DataFrame] = None
    ) -> TrainingResult:
        """Retrain existing model with new data"""
        # Implementation
        pass
```

### 2. PredictionService

```python
class PredictionService(BaseService):
    """Service for making predictions"""
    
    def __init__(
        self,
        review_repository: ReviewRepository,
        model_repository: ModelRepository,
        predictor: Predictor,
        logger: Optional[Logger] = None
    ):
        super().__init__(logger)
        self.review_repo = review_repository
        self.model_repo = model_repository
        self.predictor = predictor
    
    def predict_batch(
        self,
        review_ids: List[str],
        model_version: str = "latest"
    ) -> List[PredictionResult]:
        """
        Batch prediction workflow:
        1. Load model
        2. Fetch reviews
        3. Predict
        4. Save results
        """
        self._log_operation("Batch prediction", count=len(review_ids))
        
        # 1. Load model
        model = self.model_repo.load_model(model_version)
        self.predictor.set_model(model)
        
        # 2. Fetch reviews
        reviews = self.review_repo.get_by_ids(review_ids)
        
        # 3. Predict
        predictions = self.predictor.predict_batch(
            texts=reviews['text'].tolist()
        )
        
        # 4. Save results
        self.review_repo.save_predictions(review_ids, predictions)
        
        return predictions
    
    def predict_unlabeled(
        self,
        batch_size: int = 100,
        max_batches: int = 10
    ) -> int:
        """Predict all unlabeled reviews"""
        total_predicted = 0
        
        for batch_num in range(max_batches):
            # Fetch unlabeled batch
            reviews = self.review_repo.get_unlabeled_reviews(
                limit=batch_size
            )
            
            if reviews.empty:
                break
            
            # Predict
            predictions = self.predictor.predict_batch(
                texts=reviews['text'].tolist()
            )
            
            # Save
            self.review_repo.save_predictions(
                reviews['id'].tolist(),
                predictions
            )
            
            total_predicted += len(reviews)
            
            self._log_operation(
                "Batch predicted",
                batch=batch_num + 1,
                count=len(reviews)
            )
        
        return total_predicted
```

### 3. MonitoringService

```python
class MonitoringService(BaseService):
    """Service for monitoring model performance"""
    
    def __init__(
        self,
        review_repository: ReviewRepository,
        model_repository: ModelRepository,
        metrics_repository: MetricsRepository,
        evaluator: Evaluator,
        logger: Optional[Logger] = None
    ):
        super().__init__(logger)
        self.review_repo = review_repository
        self.model_repo = model_repository
        self.metrics_repo = metrics_repository
        self.evaluator = evaluator
    
    def check_model_performance(
        self,
        model_id: str,
        sample_size: int = 1000
    ) -> PerformanceReport:
        """
        Check current model performance:
        1. Sample labeled data
        2. Get predictions
        3. Calculate metrics
        4. Compare with baseline
        5. Alert if degraded
        """
        # 1. Sample data
        sample = self.review_repo.get_labeled_sample(
            size=sample_size
        )
        
        # 2. Get predictions
        predictions = self.review_repo.get_predictions(
            sample['id'].tolist()
        )
        
        # 3. Calculate metrics
        metrics = self.evaluator.compute_metrics(
            predictions=predictions,
            ground_truth=sample
        )
        
        # 4. Compare with baseline
        baseline = self.metrics_repo.get_baseline_metrics(model_id)
        degradation = self._calculate_degradation(metrics, baseline)
        
        # 5. Alert if degraded
        if degradation > 0.05:  # 5% threshold
            self._alert_performance_degradation(
                model_id, metrics, baseline, degradation
            )
        
        # Save metrics
        self.metrics_repo.save_metrics(model_id, metrics)
        
        return PerformanceReport(
            model_id=model_id,
            current_metrics=metrics,
            baseline_metrics=baseline,
            degradation=degradation,
            requires_retraining=degradation > 0.05
        )
    
    def _alert_performance_degradation(self, ...):
        """Send alert about model degradation"""
        self.logger.warning(
            f"Model {model_id} degraded by {degradation:.2%}"
        )
        # Send email, Slack notification, etc.
```

### 4. EvaluationService

```python
class EvaluationService(BaseService):
    """Service for model evaluation"""
    
    def __init__(
        self,
        review_repository: ReviewRepository,
        model_repository: ModelRepository,
        evaluator: Evaluator,
        logger: Optional[Logger] = None
    ):
        super().__init__(logger)
        self.review_repo = review_repository
        self.model_repo = model_repository
        self.evaluator = evaluator
    
    def evaluate_model(
        self,
        model_id: str,
        test_set: Optional[DataFrame] = None
    ) -> EvaluationResult:
        """Comprehensive model evaluation"""
        # Load model
        model = self.model_repo.load_model(model_id)
        
        # Get test data
        if test_set is None:
            test_set = self.review_repo.get_test_set()
        
        # Evaluate
        results = self.evaluator.evaluate(
            model=model,
            test_data=test_set,
            verbose=True
        )
        
        return EvaluationResult(
            model_id=model_id,
            metrics=results['metrics'],
            predictions=results['predictions'],
            report=self._generate_report(results)
        )
```

---

## Service Composition

Services can use other services:

```python
class MLWorkflowService(BaseService):
    """High-level ML workflow orchestration"""
    
    def __init__(
        self,
        training_service: TrainingService,
        evaluation_service: EvaluationService,
        prediction_service: PredictionService,
        monitoring_service: MonitoringService
    ):
        super().__init__()
        self.training = training_service
        self.evaluation = evaluation_service
        self.prediction = prediction_service
        self.monitoring = monitoring_service
    
    def full_pipeline(self, config: PipelineConfig):
        """Complete ML pipeline from training to deployment"""
        # 1. Train
        result = self.training.train_new_model(config.training)
        
        # 2. Evaluate
        eval_result = self.evaluation.evaluate_model(result.model_id)
        
        # 3. Deploy if good
        if eval_result.metrics['f1_score'] >= config.deploy_threshold:
            self.model_repo.promote_to_production(result.model_id)
            
            # 4. Predict unlabeled
            self.prediction.predict_unlabeled()
            
            # 5. Start monitoring
            self.monitoring.schedule_monitoring(result.model_id)
```

---

## Dependency Injection

```python
# Setup dependencies
review_repo = ReviewRepository(dataset=create_dataset(client))
model_repo = ModelRepository(storage_path="./models")
pipeline = TrainingPipeline()

# Inject into service
training_service = TrainingService(
    review_repository=review_repo,
    model_repository=model_repo,
    training_pipeline=pipeline
)

# Use service
result = training_service.train_new_model(config)
```

---

## Pros and Cons of the Options

### No Service Layer

* **Good:** Simple, less code
* **Bad:** Business logic scattered everywhere
* **Bad:** Hard to reuse
* **Bad:** Hard to test
* **Bad:** Tight coupling

### Fat Models

* **Good:** Logic close to data
* **Bad:** Models become too complex
* **Bad:** Hard to orchestrate multiple models
* **Bad:** Violates Single Responsibility

### Service Layer Pattern ✅

* **Good:** Clear separation of concerns
* **Good:** Reusable business logic
* **Good:** Easy to test with mocks
* **Good:** Orchestrate complex workflows
* **Good:** Handle transactions
* **Bad:** More layers = more complexity
* **Bad:** Can become "God objects" if not careful

### CQRS Pattern

* **Good:** Optimized read/write paths
* **Bad:** Over-engineering for this scale
* **Bad:** More complex to implement

---

## Testing Strategy

```python
def test_training_service():
    # Mock dependencies
    mock_repo = Mock(spec=ReviewRepository)
    mock_model_repo = Mock(spec=ModelRepository)
    mock_pipeline = Mock(spec=TrainingPipeline)
    
    # Setup mock returns
    mock_repo.get_labeled_data.return_value = sample_data
    mock_pipeline.train.return_value = (mock_model, history)
    
    # Create service with mocks
    service = TrainingService(
        review_repository=mock_repo,
        model_repository=mock_model_repo,
        training_pipeline=mock_pipeline
    )
    
    # Test
    result = service.train_new_model(config)
    
    # Assert
    assert result.model_id is not None
    mock_repo.get_labeled_data.assert_called_once()
    mock_model_repo.save_model.assert_called_once()
```

---

## Links

* [ADR-001: Overall Architecture](001-overall-architecture.md)
* [ADR-002: Data Layer Architecture](002-data-layer-architecture.md)
* [ADR-004: ML Pipeline Design](004-ml-pipeline-design.md)

---

## Notes

- Keep services focused on single responsibility
- Avoid making services too large (split if needed)
- Use dependency injection for testability
- Services should not directly access database - use repositories
- Services orchestrate, pipelines execute
- Consider async services for long-running operations
