本项目是一个基于 Kubernetes 的 MNIST 图像分类推理平台，使用 Flask + PyTorch 构建模型推理服务，并通过 Docker 实现容器化部署。相比上个项目（CIFAR10-K8s-API），本项目重点实践 自动扩缩容（HPA）、容器 QoS 管理 与 Metrics Server 指标采集，验证 AI 推理服务在集群中的资源调度与伸缩机制。

项目覆盖从 镜像构建 → 集群部署（Deployment / Service / Ingress）→ 指标采集（Metrics Server）→ 自动扩缩容（HPA）→ QoS 分类验证（Guaranteed / Burstable / BestEffort）→ 负载压测与自愈测试 的完整流程，掌握了 Kubernetes 在 AI 应用中的 性能监控、负载均衡与资源优化 思路。

通过本项目，深入理解了 Kubernetes 在 AI 平台中的 自动化运维与弹性计算原理，以及模型服务在生产环境下的 稳定性与可扩展性保障机制。

## 环境说明
- Python  + PyTorch 
- Docker Desktop (K8s Enabled)
- kubectl CLI 工具
- 镜像仓库：本地 registry


## 部署步骤
构建 Docker 镜像,启动容器并测试推理服务
```bash
docker build -t mnist-api:v1 .
docker run -d -p 5000:5000 mnist-api:v1
curl -X POST -F"file=@sample.png" Localhost:5000/predict
{"prediction":5}
```

<img width="865" height="475" alt="image" src="https://github.com/user-attachments/assets/d91f9ab6-0fa8-46ff-bc63-9fd5ad177b5a" />

<img width="865" height="91" alt="image" src="https://github.com/user-attachments/assets/885b0464-3949-41d1-8e1f-3a6aa267624f" />

<img width="865" height="98" alt="image" src="https://github.com/user-attachments/assets/b15916b6-c2aa-42af-898d-4f6cf6e4806b" />

部署Deployment、Service、Ingressh服务，并进行测试

```bash
kubectl apply -f deploy.yaml
kubectl get pods
kubectl get svc
kubectl get ingress
curl -X POST -F"file=@sample.png" tarry.mnistapi.local/predict
{"prediction":5}
```

<img width="865" height="426" alt="image" src="https://github.com/user-attachments/assets/a212f673-e64a-4df9-9393-2ff4aafda5a4" />

安装Metrics Server与配置

```bash
kubectl apply -f components.yaml
```

在Docker Desktop环境中，metrics-server默认无法采集节点指标，因为：kubelet采用自签名证书；缺少 IP SAN（Subject Alternative Name）字段；
metrics-server 在与 kubelet 建立 HTTPS 通信时校验失败。
解决方法：
通过修改 metrics-server 启动参数，添加：
```bash
--kubelet-insecure-tls
```
跳过证书验证。


<img width="865" height="159" alt="image" src="https://github.com/user-attachments/assets/5cd922a5-891d-439b-84e2-267e4216df15" />

<img width="865" height="91" alt="image" src="https://github.com/user-attachments/assets/a5705db4-0bab-4bd5-9874-1eee8629abe0" />

<img width="865" height="44" alt="image" src="https://github.com/user-attachments/assets/5b3ab63c-a294-4074-b8d3-6f0c4dc7bacd" />

安装HPA服务
```bash
kubectl apply -f hpa.yaml
```
<img width="865" height="39" alt="image" src="https://github.com/user-attachments/assets/0517e6c2-da39-4e61-a55d-7814ce30dc5a" />
<img width="865" height="67" alt="image" src="https://github.com/user-attachments/assets/3d799998-6eda-48aa-883e-83086782cfe8" />

开启压力测试

循环向 Flask API 发送请求，模拟高并发负载

```bash
while true; do
  curl -s http://tarry.mnistapi.local/predict -F "file=@sample.png" > /dev/null
done
```

<img width="865" height="75" alt="image" src="https://github.com/user-attachments/assets/ca390d77-67bb-4294-afe1-73b4e95e0abd" />

扩容阶段

```bash
cpu: 0%/50% → 250%/50% → 110%/50% → 97%/50%
replicas: 1 → 4 → 5
```
HPA 监测到平均 CPU 使用率达到目标的 250%，触发扩容；

Deployment 被指令扩容；

ReplicaSet 开始创建新 Pod；

最终副本数上升到 5 个，CPU 使用率回落到 97%，系统趋稳。

新 Pod 状态依次经历 Pending → ContainerCreating → Running；

负载下降后系统逐步缩回单副本，实现了完整的自动伸缩闭环。

<img width="865" height="240" alt="image" src="https://github.com/user-attachments/assets/bbb14cbb-110d-4903-aadf-73a3acbbaf14" />

<img width="865" height="828" alt="image" src="https://github.com/user-attachments/assets/542ee3d2-4d05-4521-b253-d66d51b8e8c0" />




