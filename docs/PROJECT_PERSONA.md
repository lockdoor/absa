# Review Radar - Project Persona & Requirements

## 📋 Project Overview

**Project Name:** Review Radar - ABSA Social Media Sentiment Analysis System

**Mission:** ระบบวิเคราะห์ความรู้สึกแบบ Aspect-Based จาก social media platforms เพื่อช่วยลูกค้าเข้าใจความคิดเห็นของผู้บริโภคต่อผลิตภัณฑ์ใหม่ในแต่ละมิติ

**Problem Statement:** เมื่อมีผลิตภัณฑ์ใหม่เข้าสู่ตลาด แบรนด์ต้องการทราบความคิดเห็นและความรู้สึกของผู้บริโภคต่อผลิตภัณฑ์ในด้านต่างๆ (aspects) อย่างรวดเร็วและแม่นยำ เพื่อนำไปปรับปรุงและวางแผนการตลาด

---

## 👥 Personas & Stakeholders

### 1. **ลูกค้า (Client/Brand Owner)**
**บทบาท:** เจ้าของแบรนด์/ผลิตภัณฑ์ที่ต้องการเข้าใจความรู้สึกของผู้บริโภค

**ความต้องการ:**
- 📊 รายงานความรู้สึกต่อผลิตภัณฑ์ในแต่ละด้าน (aspects)
- 📈 Insight เชิงลึกเพื่อการตัดสินใจ
- ⚡ ได้ผลลัพธ์รวดเร็วหลังผลิตภัณฑ์เปิดตัว
- 🎯 ความแม่นยำสูงในการวิเคราะห์

**Pain Points:**
- การวิเคราะห์ manual ใช้เวลานาน
- ข้อมูลกระจัดกระจายในหลาย platforms
- ไม่สามารถติดตามแบบ real-time

**Success Metrics:**
- ได้รายงานภายใน 24-48 ชั่วโมงหลังเก็บข้อมูล
- Accuracy ≥ 85% ในการจำแนก aspects และ sentiments

---

### 2. **Data Collection Team**
**บทบาท:** ทีมงานที่รับผิดชอบเก็บข้อมูลจาก social media platforms

**ความต้องการ:**
- 🔍 เครื่องมือในการค้นหาและเก็บข้อมูลจากหลาย platforms
- 💾 ระบบจัดเก็บข้อมูลที่มีประสิทธิภาพ
- 📝 Interface สำหรับการ label ข้อมูล (เพื่อ validation)

**Responsibilities:**
- เก็บ reviews/comments จาก social media
- Labeling ข้อมูลสำหรับ validation/training
- ตรวจสอบคุณภาพข้อมูล

**Tools/Platforms:**
- Facebook, Instagram, Twitter/X, TikTok, Pantip, Reddit
- YouTube comments, Google Reviews
- E-commerce reviews (Shopee, Lazada)

---

### 3. **ML Engineer/Data Scientist**
**บทบาท:** พัฒนาและดูแล ABSA model

**ความต้องการ:**
- 📉 Monitoring system เพื่อติดตาม model performance
- 🔄 Pipeline สำหรับ retraining model อัตโนมัติ
- 📊 Metrics และ evaluation tools
- 🧪 Experiment tracking

**Responsibilities:**
- Train/retrain ABSA model
- Monitor model performance
- Improve model accuracy
- Handle model degradation

**Success Metrics:**
- Model F1-score ≥ 85% (aspects & sentiments)
- Inference time < 100ms per review
- Auto-retrain เมื่อ performance drop > 5%

---

### 4. **System Administrator**
**บทบาท:** จัดการ infrastructure และ deployment

**ความต้องการ:**
- 🚀 Scalable infrastructure
- 📈 Monitoring และ logging
- 🔐 Security และ data privacy
- 💰 Cost optimization

**Responsibilities:**
- Deploy และ maintain system
- Scale resources ตาม demand
- Backup และ disaster recovery

---

## 🔄 System Workflow

### Phase 1: Project Initiation
```
Client Request → Project Setup → Define Aspects → Configure Data Sources
```

**Input:**
- ข้อมูลผลิตภัณฑ์
- Aspects ที่สนใจ (เช่น คุณภาพ, ราคา, การจัดส่ง, บริการ)
- Social media platforms target
- Timeline

**Output:**
- Project configuration
- Data collection plan

---

### Phase 2: Data Collection
```
Social Media → Data Scraping → Data Storage → Initial Labeling (sample)
```

**Process:**
1. ทีม Data Collection เก็บข้อมูลจาก platforms ที่กำหนด
2. เก็บข้อมูลลงใน database (Supabase/Postgres)
3. Label ข้อมูลตัวอย่างเพื่อ validation

**Data Schema:**
- `review_text`: ข้อความรีวิว/comment
- `source`: แหล่งที่มา (platform)
- `product_id`: รหัสผลิตภัณฑ์
- `collected_at`: เวลาที่เก็บ
- `aspects`: aspects ที่ตรวจพบ (array)
- `sentiments`: ความรู้สึกในแต่ละ aspect
- `is_labeled`: สถานะการ label
- `confidence_score`: ความมั่นใจของ model

---

### Phase 3: Inference
```
Raw Data → Preprocessing → ABSA Model → Aspect & Sentiment Extraction → Results
```

**Process:**
1. ดึงข้อมูลที่ยังไม่ผ่าน inference
2. Preprocess text (clean, normalize)
3. ส่งผ่าน ABSA model เพื่อ predict aspects & sentiments
4. บันทึกผลลัพธ์พร้อม confidence score
5. ข้อมูลที่ confidence ต่ำ → flagged สำหรับ manual review

**Output:**
- Predicted aspects (multi-label)
- Sentiment per aspect (positive/neutral/negative)
- Confidence scores

---

### Phase 4: Validation & Labeling
```
Inference Results → Sample Selection → Manual Labeling → Ground Truth Dataset
```

**Process:**
1. สุ่มตัวอย่างจากข้อมูลที่ inference แล้ว
2. ทีม Data Collection ทำ manual labeling
3. เก็บเป็น ground truth สำหรับ validation
4. เปรียบเทียบกับ prediction ของ model

**Selection Strategy:**
- Random sampling (10% ของข้อมูล)
- High-confidence samples (เพื่อ verify)
- Low-confidence samples (เพื่อ improve)
- Edge cases

---

### Phase 5: Model Monitoring & Evaluation
```
Labeled Data → Calculate Metrics → Monitor Performance → Alert if Degradation
```

**Metrics:**
- **Aspect Extraction:** Precision, Recall, F1-score (per aspect)
- **Sentiment Classification:** Accuracy, F1-score (per sentiment)
- **Overall Performance:** Macro/Micro F1

**Monitoring:**
- Daily/Weekly performance tracking
- Drift detection
- Performance degradation alerts

**Alert Conditions:**
- F1-score drops > 5% จากค่า baseline
- Accuracy < 80%
- Significant distribution shift

---

### Phase 6: Model Retraining
```
Performance Drop → Prepare Training Data → Retrain Model → Evaluate → Deploy
```

**Trigger Conditions:**
1. Model performance drop ≥ 5%
2. Accumulated labeled data ≥ threshold (e.g., 1,000 new samples)
3. Manual trigger by ML Engineer
4. Scheduled retraining (e.g., monthly)

**Retraining Process:**
1. Aggregate all labeled data
2. Split into train/val/test (80/10/10)
3. Retrain ABSA model
4. Validate on test set
5. A/B test: compare with current model
6. Deploy if performance improves

**Safeguards:**
- Keep previous model as backup
- Gradual rollout (canary deployment)
- Rollback if issues detected

---

### Phase 7: Reporting & Insights
```
Analysis Results → Generate Reports → Dashboard → Client Delivery
```

**Reports Include:**
- Aspect distribution (which aspects mentioned most)
- Sentiment breakdown per aspect
- Trend over time
- Top positive/negative reviews
- Actionable insights

**Delivery Format:**
- PDF report
- Interactive dashboard
- API for real-time queries
- Email alerts for significant changes

---

## 🎯 Use Cases

### Use Case 1: New Product Launch Analysis
**Actor:** Client (Brand Owner)

**Scenario:**
1. Client launches new smartphone
2. Wants to know public opinion in first 2 weeks
3. Focus aspects: design, performance, camera, battery, price

**Steps:**
1. Client submits project request
2. Data team collects reviews from social media
3. System infers aspects & sentiments
4. ML engineer validates sample data
5. Client receives report showing:
   - Camera: 85% positive
   - Battery: 60% positive, 30% negative
   - Price: 70% negative (too expensive)

**Outcome:** Client adjusts marketing strategy, considers price promotions

---

### Use Case 2: Continuous Product Monitoring
**Actor:** Client + Data Collection Team

**Scenario:**
1. Monitor established product monthly
2. Track sentiment changes over time
3. Identify emerging issues

**Steps:**
1. Automated data collection daily
2. Weekly inference batches
3. Monthly labeling for validation
4. Alert if negative sentiment spike detected

**Outcome:** Early detection of product issues (e.g., quality defect)

---

### Use Case 3: Model Performance Degradation
**Actor:** ML Engineer

**Scenario:**
1. Model accuracy drops from 87% to 81%
2. New slang/language patterns not recognized

**Steps:**
1. Monitoring system detects performance drop
2. Alert sent to ML engineer
3. Analyze error patterns
4. Collect more labeled data for weak areas
5. Retrain model with updated data
6. Deploy improved model (accuracy back to 86%)

**Outcome:** Maintained model performance

---

### Use Case 4: Multi-Product Comparison
**Actor:** Client

**Scenario:**
1. Client wants to compare their product vs competitors
2. Analyze same aspects across products

**Steps:**
1. Collect data for multiple products
2. Run inference for all products
3. Generate comparison report

**Outcome:** Client identifies competitive advantages/weaknesses

---

## 💾 Data Management

### Data Storage Strategy
```
Raw Data → Bronze Layer (raw storage)
         → Silver Layer (cleaned, labeled)
         → Gold Layer (analysis-ready)
```

**Storage Duration:**
- Raw data: 2 years
- Labeled data: Permanent (training data)
- Inference results: 1 year
- Reports: Permanent

---

## 🔐 Privacy & Ethics

**Considerations:**
- ✅ Public data only (no private messages)
- ✅ Anonymize user information
- ✅ Comply with platform ToS
- ✅ PDPA/GDPR compliance
- ✅ No manipulation or spam detection bypass

---

## 📊 Success Criteria

### Technical Metrics
- Model Accuracy: ≥ 85%
- Inference Speed: < 100ms/review
- System Uptime: ≥ 99%
- Retraining Time: < 4 hours

### Business Metrics
- Client Satisfaction: ≥ 4.5/5
- Time to Insight: < 48 hours
- Cost per Analysis: Optimized
- Repeat Clients: ≥ 70%

---

## 🛠️ Technical Stack

### Data Collection
- Platform APIs (Facebook, Twitter, etc.)
- Web scraping (Selenium, BeautifulSoup)
- Data pipeline (Airflow/Prefect)

### Storage
- Database: Supabase/PostgreSQL
- File storage: S3/Cloud Storage

### ML/AI
- Framework: PyTorch + Transformers
- Model: BERT-based multilingual
- Inference: FastAPI
- Monitoring: MLflow/Weights & Biases

### Infrastructure
- Cloud: AWS/GCP/Azure
- Containers: Docker + Kubernetes
- CI/CD: GitHub Actions

---

## 📈 Future Enhancements

1. **Real-time Streaming:** Process data as it arrives
2. **Multi-language Support:** Auto-detect and handle multiple languages
3. **Aspect Discovery:** Auto-discover new aspects from data
4. **Sentiment Intensity:** Fine-grained sentiment (very positive → very negative)
5. **Trend Prediction:** Forecast sentiment trends
6. **Chatbot Interface:** Query results via conversational AI

---

## 📝 Document Control

**Version:** 1.0  
**Last Updated:** December 22, 2025  
**Author:** Review Radar Team  
**Status:** Draft → Review → Approved

**Change Log:**
- v1.0: Initial persona and requirements document
