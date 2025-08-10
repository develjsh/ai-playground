#

## requirements.txt 만들기
pip freeze > requirements.txt

## 모델

### 모델 분석
02_traffic_sign_classifier는 교통 표지판 분류 문제를 다룹니다.
이 데이터셋은 이미지 크기가 작고(32×32~64×64), 클래스 수가 많지만 복잡한 배경이 적은 특성이 있습니다.
따라서 대형 복잡한 모델보다는 경량 CNN 모델이나 전이학습(Transfer Learning) 기반 모델이 효율적입니다.

1. 직접 설계한 경량 CNN (학습 속도 빠르고, 구조 단순)
구조 예시:
Conv2D(32 filters, 3×3) → ReLU → MaxPooling
Conv2D(64 filters, 3×3) → ReLU → MaxPooling
Conv2D(128 filters, 3×3) → ReLU → MaxPooling
Flatten → Dense(128) → Dropout → Dense(클래스 수, softmax)

장점: 구현 쉽고, 데이터가 적어도 학습 가능
단점: 복잡한 패턴 학습 능력은 제한됨

2. 전이학습 (Transfer Learning) – 데이터 많거나 빠른 성능 향상 원할 때
예시: MobileNetV2, ResNet50, EfficientNetB0

방법
ImageNet 사전 학습 가중치 불러오기
마지막 분류층만 교체 (Dense(클래스 수, activation='softmax'))
필요 시 중간 레이어 일부 학습(fine-tuning)

장점 : 적은 데이터로도 높은 정확도, 학습 속도 빠름
단점 : 모델 크기가 다소 클 수 있음 (MobileNetV2는 비교적 경량)

3. 추천 전략
데이터 양이 충분 → 전이학습(MobileNetV2)로 빠르게 좋은 성능
데이터 양이 적음 → 간단한 CNN + 데이터 증강(ImageDataGenerator)
리소스 제약 많음 (예: 라즈베리파이 배포) → MobileNetV2, EfficientNetB0 같이 경량 모델

### 모델 선택
