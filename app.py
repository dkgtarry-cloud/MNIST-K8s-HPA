from flask import Flask, request, jsonify
import torch
from torchvision import transforms
from PIL import Image
from model import SimpleCNN   # ← 你上周定义的模型类

app = Flask(__name__)

# ======================
# 模型加载（新增部分）
# ======================
model = SimpleCNN()
model.load_state_dict(torch.load("mnist_cnn.pth", map_location="cpu"))
model.eval()

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

print("✅ 模型加载成功")

# ======================
# 路由部分
# ======================
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return jsonify({'msg': 'Use POST to upload image'})
    try:
        file = request.files['file']
        img = Image.open(file.stream)
        img = transform(img).unsqueeze(0)

        with torch.no_grad():
            output = model(img)
            pred = torch.argmax(output, 1).item()

        return jsonify({'prediction': int(pred)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
