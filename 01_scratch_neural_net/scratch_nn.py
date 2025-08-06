import numpy as np

# XOR 데이터셋
X = np.array([[0,0],[0,1],[1,0],[1,1]])
y = np.array([[0],[1],[1],[0]])

# 하이퍼파라미터 설정
input_size = 2      # XOR 문제의 입력 개수 (2개)
hidden_size = 2     # 은닉층 노드 수 (XOR 문제는 최소 2개 필요)
output_size = 1     # 출력 노드 수 (XOR의 출력은 1개)
lr = 0.1            # 학습률(learning rate)
epochs = 10000      # 학습 반복 횟수

# 참고:
# - hidden_size는 너무 적으면 학습이 안 되고, 너무 많으면 오버피팅 위험이 있습니다.
# - 실습 목적이므로 최소값(2)으로 설정했습니다.

# 가중치 초기화
np.random.seed(42)
W1 = np.random.randn(input_size, hidden_size)
b1 = np.zeros((1, hidden_size))
W2 = np.random.randn(hidden_size, output_size)
b2 = np.zeros((1, output_size))

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_deriv(x):
    return x * (1 - x)

# 학습 루프
for epoch in range(epochs):
    # 순전파
    z1 = np.dot(X, W1) + b1
    a1 = sigmoid(z1)
    z2 = np.dot(a1, W2) + b2
    a2 = sigmoid(z2)

    # 손실 계산 (MSE)
    loss = np.mean((y - a2) ** 2)

    # 역전파
    d_a2 = (a2 - y) * sigmoid_deriv(a2)
    d_W2 = np.dot(a1.T, d_a2)
    d_b2 = np.sum(d_a2, axis=0, keepdims=True)

    d_a1 = np.dot(d_a2, W2.T) * sigmoid_deriv(a1)
    d_W1 = np.dot(X.T, d_a1)
    d_b1 = np.sum(d_a1, axis=0, keepdims=True)

    # 가중치 업데이트
    W2 -= lr * d_W2
    b2 -= lr * d_b2
    W1 -= lr * d_W1
    b1 -= lr * d_b1

    if epoch % 1000 == 0:
        print(f"Epoch {epoch}, Loss: {loss:.4f}")

# 결과 확인
print("예측 결과:")
print(a2)