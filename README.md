# Review Radar 🎯

Aspect-Based Sentiment Analysis (ABSA) Package สำหรับการวิเคราะห์ความรู้สึกของรีวิวตาม aspects ต่างๆ

## 🌟 Features

- **Data Management**: โหลด preprocess และจัดการข้อมูลรีวิว
- **ABSA Models**: โมเดลสำหรับ aspect extraction และ sentiment classification
- **Training Pipeline**: ระบบ training ที่สมบูรณ์พร้อม callbacks และ metrics
- **Evaluation**: เครื่องมือประเมินผลแบบละเอียด
- **Inference**: API สำหรับการทำนายที่ใช้งานง่าย

## 📦 Installation

```bash
pip install -e .
```

## 🚀 Quick Start

### 1. Load และ Preprocess Data

```python
from review_radar import ReviewDataset, TextPreprocessor, DataLoader

# Load data
loader = DataLoader()
df = loader.load_csv("train_data.csv")

# Preprocess
preprocessor = TextPreprocessor(lowercase=True, remove_urls=True)
df = preprocessor.preprocess_dataframe(df, text_column="review_text")

# Create dataset
dataset = ReviewDataset(
    data=df,
    text_column="review_text",
    aspect_column="aspect",
    sentiment_column="sentiment"
)

# Split data
splits = dataset.split_data(train_ratio=0.8, val_ratio=0.1)
```

### 2. Train Model

```python
from review_radar import ABSAModel, Trainer, ModelConfig, TrainingConfig
from review_radar import EarlyStopping, ModelCheckpoint
import torch

# Config
model_config = ModelConfig(
    model_name="bert-base-multilingual-cased",
    num_aspects=5,
    num_sentiments=3
)

# Create model
model = ABSAModel(
    model_name=model_config.model_name,
    num_aspects=model_config.num_aspects,
    num_sentiments=model_config.num_sentiments
)

# Setup training
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Callbacks
callbacks = [
    EarlyStopping(monitor='val_loss', patience=3),
    ModelCheckpoint(filepath='best_model.pt', monitor='val_loss')
]

# Trainer
trainer = Trainer(
    model=model,
    train_loader=train_loader,  # Your DataLoader
    val_loader=val_loader,
    optimizer=optimizer,
    device=device,
    callbacks=callbacks
)

# Train
history = trainer.fit(num_epochs=10, criterion=criterion)
```

### 3. Evaluate

```python
from review_radar import Evaluator, print_evaluation_report

evaluator = Evaluator(model=model, device=device)

results = evaluator.evaluate(
    test_loader=test_loader,
    aspect_names=["food", "service", "price", "ambiance", "location"],
    sentiment_names=["negative", "neutral", "positive"],
    verbose=True
)

print_evaluation_report(results['metrics'])
```

### 4. Inference

```python
from review_radar import Predictor

predictor = Predictor(
    model=model,
    device=device,
    aspect_names=["food", "service", "price", "ambiance", "location"],
    sentiment_names=["negative", "neutral", "positive"]
)

# Predict single text
texts = ["อาหารอร่อยมาก แต่บริการช้าไปหน่อย"]
results = predictor.predict(texts, return_probs=True)

for result in results:
    print(f"Text: {result['text']}")
    print(f"Aspects: {result['aspects']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Sentiment Probs: {result['sentiment_probs']}")
```

## 📁 Project Structure

```
review_radar/
├── __init__.py
├── config/              # Configuration
│   ├── __init__.py
│   └── settings.py
├── data/                # Data handling
│   ├── __init__.py
│   ├── base_dataset.py
│   ├── review_dataset.py
│   ├── preprocessor.py
│   └── loader.py
├── models/              # Model architectures
│   ├── __init__.py
│   ├── base_model.py
│   ├── absa_model.py
│   └── extractors.py
├── training/            # Training pipeline
│   ├── __init__.py
│   ├── trainer.py
│   ├── callbacks.py
│   └── metrics.py
├── evaluation/          # Evaluation
│   ├── __init__.py
│   ├── evaluator.py
│   └── metrics.py
├── inference/           # Inference
│   ├── __init__.py
│   └── predictor.py
└── utils/               # Utilities
    ├── __init__.py
    ├── logger.py
    └── helpers.py
```

## 🛠️ Requirements

- Python >= 3.8
- PyTorch >= 1.12
- Transformers >= 4.20
- pandas
- numpy
- scikit-learn
- tqdm

## 📝 License

MIT License

## 👥 Contributors

Review Radar Team
