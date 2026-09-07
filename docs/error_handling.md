# Error Handling

## Envelope

```json
{
  "success": false,
  "data": null,
  "error": {
    "failed_step": "feature_extraction",
    "error_type": "FEATURE_EXTRACTION_ERROR",
    "message": "Email feature extraction failed",
    "detail": "...",
    "timestamp": "2026-09-07T00:00:00Z"
  }
}
```

## Error Types

| ErrorType | Typical failed_step | Meaning |
| --- | --- | --- |
| FEATURE_EXTRACTION_ERROR | feature_extraction | EML/dict 解析、头部、正文、附件、URL 或发件人画像提取失败 |
| LLM_INVOCATION_ERROR | phishing_chain / attachment_chain / bec_chain / spam_chain | LLM 调用失败 |
| OUTPUT_PARSE_ERROR | phishing_chain / attachment_chain / bec_chain / spam_chain | LLM 输出无法解析为 Pydantic 模型 |
| TIMEOUT_ERROR | judgment_pipeline / dimension chain | 超时 |
| VALIDATION_ERROR | fusion_chain / api_request_validation | 数据校验或融合输入异常 |
| UNKNOWN_ERROR | judgment_pipeline / api_unknown | 未分类异常 |

## Rules

- 不重试。
- 不 fallback。
- 不跳过失败步骤继续跑。
- 不返回部分结果。
- 批量研判只隔离邮件，不改变单封邮件内部 Fail-Fast 行为。
