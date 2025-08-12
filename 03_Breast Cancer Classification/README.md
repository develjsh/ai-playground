# 유방암 진단 데이터 기반 양성/악성 분류 모델 구축

## 1. 프로젝트 개요
이 프로젝트는 **유방암 진단 데이터**를 활용하여, 종양이 **양성(Benign)**인지 **악성(Malignant)**인지 분류하는 머신러닝·딥러닝 모델을 구축하는 것을 목표로 합니다.  
데이터는 **Kaggle - Breast Cancer Wisconsin (Diagnostic) Dataset**을 사용하며, 데이터의 수치형 피처들을 분석(EDA)하고 모델 학습에 적합한 형태로 전처리한 뒤 다양한 모델을 비교·평가합니다.

---

## 2. 데이터 소개

### 2.1 사용한 데이터
- **출처:** [Kaggle Dataset](https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data)
- **데이터 형태:** CSV, 표 형식
- **관측치:** 569건
- **피처 수:** 30개 (모두 수치형, 암 조직 세포의 형태학적 특징)
- **목표 변수(Target):** Diagnosis (`M`=Malignant, `B`=Benign)

### 2.2 추천 데이터셋 목록
1. VinDr-Mammo
풀필드 디지털 유방 촬영(FFDM) 기반의 대규모 영상 데이터셋으로, 총 5,000건의 유방 촬영 영상과 BI-RADS 평가, 비양성 병변 위치 정보 등을 포함합니다. 딥러닝 기반의 컴퓨터 지원 진단(CADx) 모델 개발에 매우 적합합니다.
arXiv

2. KAUH-BCMD (King Abdullah University Hospital)
약 5,000명의 환자, 7,205장의 실제 디지털 유방 촬영 이미지로 구성되며, 전처리된 이미지와 고성능 CNN (Residual Depth-wise Network, RDN) 모델 결과를 포함합니다. 최신 모델 성능 비교에 유리합니다.
Frontiers

3. TCIA / CBIS-DDSM
The Cancer Imaging Archive (TCIA)는 다양한 암종의 영상 데이터를 제공하는 주요 공개 리포지토리입니다. 특히 CBIS-DDSM (Digital Database for Screening Mammography) 등 유방암 관련 유방 X-ray 이미지를 대규모로 포함하고 있어 영상 기반 분석에 유용합니다.
위키백과
The Cancer Imaging Archive (TCIA)

4. BRACS
H&E 염색된 조직 슬라이드(Whole-Slide Images)를 포함한 병리학적 이미지 데이터셋으로, 양성과 악성뿐 아니라 atypical 병변에 대한 서브타이핑(subtyping)이 가능한 데이터가 포함되어 있습니다. 고해상도 조직 이미지 분석에 적합합니다.
arXiv

5. BACH
현미경 베이스의 조직 병리 이미지 데이터셋으로 구성된 경쟁형 데이터셋으로서, 병리학적 이미지 기반 분류 모델 평가에 활용할 수 있습니다.
arXiv

6. BCNB25 (Early Breast Cancer Core-Needle Biopsy WSI Dataset)
아시아 지역 코어 바늘 생검(needle biopsy) WSI 데이터를 담은 유일한 공개 워홀 슬라이드 이미지 데이터셋입니다. 지역 간 다양성 분석에 의미가 있습니다.
ScienceDirect

7. PLCO Breast Dataset
대규모 코호트 기반의 수치형/범주형 데이터가 포함된 종합 유방암 데이터로, 약 78,000명의 데이터를 포함합니다. 표준 ML/딥러닝 모델에서 임상적 특성(feature) 기반 분석에 활용될 수 있습니다.

---

## 3. 프로젝트 진행 절차

### 3.1 데이터 탐색(EDA)
- 데이터 구조 및 결측치 확인
- Target 변수 분포 확인 (양성/악성 비율)
- 피처별 기초 통계량 및 분포 시각화
- 상관관계 분석(Correlation Heatmap)
- PCA(주성분 분석) 등을 통한 차원 축소 후 시각화

### 3.2 피처 엔지니어링
- 필요시 스케일링(StandardScaler, MinMaxScaler 등)
- 피처 선택(Feature Selection)
- 파생 피처 생성 예시:
  - **Count Encoding**: 특정 값 빈도 기반 인코딩
  - **Aggregation Feature**: 평균, 표준편차, 합계 등 통계 기반 피처
  - 동일 패턴을 갖는 그룹 추정(동일 환자군 유사도 계산 등)

> ※ 본 프로젝트에서는 필수적으로 모든 피처 엔지니어링을 적용하지 않으며, 모델 성능 향상을 위해 선택적으로 수행

### 3.3 모델 학습 및 비교
- **기본 모델**
  - 로지스틱 회귀(Logistic Regression)
  - 서포트 벡터 머신(SVM)
  - 랜덤 포레스트(Random Forest)
  - XGBoost / LightGBM
  - 간단한 MLP(다층 퍼셉트론) 딥러닝 모델
- **모델 평가**
  - 교차 검증(Cross Validation)
  - Accuracy, Precision, Recall, F1-score, ROC-AUC

### 3.4 앙상블(Ensemble)
- Voting Classifier (Hard / Soft Voting)
- Stacking
- Bagging / Boosting 기법

### 3.5 최종 모델 선정
- 테스트 데이터셋에서 성능이 가장 우수한 모델 선택
- 모델 해석(Feature Importance, SHAP 등)
