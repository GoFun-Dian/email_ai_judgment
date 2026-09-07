# Enterprise Email AI Judgment Agent

企业邮件网关 AI 研判 Agent 是一个独立旁路服务，用于对邮件进行多维度 AI 威胁研判，输出威胁评分、置信度和可解释证据。

## 核心原则

1. **AI 与规则引擎完全独立**：不接收规则引擎结果，不与规则分数融合，不回写规则系统。
2. **Fail-Fast**：任一步骤失败立即中断；无 fallback、无 retry、无跳过。
3. **统一响应结构**：所有接口返回 `JudgmentResponse`。

## 快速开始

```bash
python -m pip install -r requirements.txt
python -m pytest
python examples/judge_email.py
python examples/judge_with_error.py
```

启动 API：

```bash
uvicorn email_ai_judgment.api.app:create_app --factory --reload
```

如果未安装为包，请设置：

```bash
export PYTHONPATH=src
```

## 配置

复制 `.env.example` 为 `.env` 后配置：

- `EMAIL_AI_LLM_PROVIDER=openai|mock`
- `EMAIL_AI_OPENAI_API_KEY`
- `EMAIL_AI_LLM_MODEL`
- `EMAIL_AI_LLM_TIMEOUT_SECONDS`
- `EMAIL_AI_LLM_TEMPERATURE=0`
- `EMAIL_AI_LLM_MAX_RETRIES=0`
- 四维评分权重与威胁等级阈值
- `EMAIL_AI_FEEDBACK_DB_PATH`

Fail-Fast 是唯一运行模式，项目不提供降级或容错开关。

## 响应结构

成功：

```json
{
  "success": true,
  "data": {
    "threat_score": 88.5,
    "confidence": 0.91,
    "threat_level": "MALICIOUS"
  },
  "error": null
}
```

失败：

```json
{
  "success": false,
  "data": null,
  "error": {
    "failed_step": "phishing_chain",
    "error_type": "LLM_INVOCATION_ERROR",
    "message": "phishing_chain LLM invocation failed",
    "detail": "...",
    "timestamp": "2026-09-07T00:00:00Z"
  }
}
```

## 主要模块

- `extractors/`：邮件特征提取。
- `chains/`：四维研判链和确定性融合链。
- `engine/`：LCEL 总管道与 Fail-Fast 包装。
- `agents/`：规则推荐 Agent，仅输出参考建议。
- `explain/`：研判解释报告。
- `feedback/`：人工反馈闭环，Repository 抽象 + SQLite 默认实现。
- `api/`：FastAPI 全异步接口。

## API

- `POST /api/v1/judgment`
- `POST /api/v1/judgment/batch`
- `POST /api/v1/explain`
- `POST /api/v1/recommend`
- `POST /api/v1/feedback`
- `GET /api/v1/feedback/stats`
- `GET /api/v1/feedback/export`

详见 `docs/api.md`。
