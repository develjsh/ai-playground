# ML Toy Projects

이 레포지토리는 머신러닝과 딥러닝의 다양한 개념을 실습하고 실험하기 위한 토이 프로젝트 모음입니다.  
간단한 분류 문제부터 이미지 처리, 음성 인식, 캡션 생성 등 다양한 주제를 다룹니다.

목표: 실전 모델 구현 경험을 쌓고, 머신러닝 전반에 대한 이해도를 높이는 것

---

## 사용 기술

- Python 3.x
- TensorFlow / PyTorch (프로젝트별로 다름)
- Scikit-learn
- OpenCV / librosa / matplotlib 등
- Jupyter Notebook

---

## 프로젝트 목록

| 번호 | 프로젝트 | 설명 | 상태 |
|------|-----------|------|------|
| 01 | [Scratch Neural Network](./01_scratch_neural_net) | 파이썬으로 신경망을 처음부터 구현 | 완료 |
| 02 | [Traffic Sign Classifier](./02_traffic_sign_classifier) | 교통 표지판 이미지 분류 | 완료 |
| 03 | [Breast Cancer Classification](./03_breast_cancer_classifier) | 유방암 진단 데이터로 양성/악성 분류 | 진행 중 |
| 04 | [Gender Recognition from Voice](./04_gender_from_voice) | 음성 특성을 통해 성별 예측 | 미진행 |
| 05 | [Image Caption Generator](./05_image_captioning) | 이미지를 설명하는 캡션 생성 | 미진행 |
| 06 | [Music Genre Classification](./06_music_genre_classification) | 음악 오디오로 장르 예측 | 미진행 |
| 07 | [Colorize B&W Images](./07_bw_image_colorization) | 흑백 이미지에 색 입히기 | 미진행 |
| 08 | [Driver Drowsiness Detection](./08_driver_drowsiness_detection) | 얼굴/눈 움직임으로 졸음 탐지 | 미진행 |
| 09 | [CIFAR-10 Image Classification](./09_cifar10_classification) | 10개 카테고리 이미지 분류 | 미진행 |
| 10 | [Age Detection](./10_age_detection) | 얼굴 사진으로 나이 추정 | 미진행 |

---

## 실행 방법

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 라이브러리 설치
pip install -r requirements.txt

# 각 프로젝트 폴더로 이동해서 실행
cd 01_scratch_neural_net
jupyter notebook
