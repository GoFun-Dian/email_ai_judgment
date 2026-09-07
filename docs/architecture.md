# Architecture

## Data Flow

```text
Raw Email
  -> EmailFeatureExtractor
  -> RunnableParallel(phishing, attachment, bec, spam)
  -> FusionChain
  -> JudgmentResult
```

AI 研判模块作为独立旁路服务运行。它不消费规则引擎结果，不做规则/AI 分数融合，也不回写任何生效规则。

## Layers

- API：FastAPI 请求/响应适配。
- Engine：Fail-Fast 管道边界。
- Extractors：确定性邮件特征提取。
- Chains：四个独立 LLM 研判维度。
- Fusion：确定性加权平均与威胁等级映射。
- Feedback：Repository 抽象，SQLite 默认实现。

## Fail-Fast

所有步骤失败后立即抛出 `JudgmentException` 子类。引擎边界捕获后包装为 `JudgmentResponse(success=false)`，不返回任何部分结果。
