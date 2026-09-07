# API

所有业务接口返回 `JudgmentResponse` 包装结构。

## POST /api/v1/judgment

Request:

```json
{
  "email_id": "mail-1",
  "raw": "From: a@example.com\nTo: b@example.com\nSubject: hi\n\nhello"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "email_id": "mail-1",
    "threat_score": 5,
    "confidence": 0.8,
    "threat_level": "TRUSTED",
    "threat_types": [],
    "summary": "...",
    "evidence": [],
    "dimension_scores": {}
  },
  "error": null
}
```

## POST /api/v1/judgment/batch

Request: `{ "emails": [ ... ] }`

单封邮件内部 Fail-Fast；批量内每封隔离。

## POST /api/v1/explain

输入 `JudgmentResult` 和 `format=markdown|text`，输出报告正文字符串。

## POST /api/v1/recommend

输入已标注恶意样本数组，输出 `RuleSuggestion`。建议仅供参考，不修改规则。

## POST /api/v1/feedback

提交人工反馈：确认、修正、误报、漏报。

## GET /api/v1/feedback/stats

返回 bad case 分类统计。

## GET /api/v1/feedback/export

返回 JSONL 字符串。
