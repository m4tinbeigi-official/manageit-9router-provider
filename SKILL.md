---
name: manageit-9router-provider
description: "Add ManageIt AI Gateway provider to 9Router. Supports Anthropic Claude Haiku 5.5, NVIDIA Nemotron 3 Ultra, Qwen3.6 35B A3B, Qwen3.8 27B (all FREE)."
version: 1.0.0
author: Rick Sanchez (C-137)
license: MIT
metadata:
  hermes:
    tags: [ManageIt, 9Router, provider, free-models]
  related_skills: [manageit-ai-gateway, 9router-custom-model-integration]
---

# ManageIt 9Router Provider

This skill lets you add the **ManageIt AI Gateway** provider to your 9Router instance.

## مدل‌های که اضافه می‌شن

| مدل | برند | قیمت |
|---|---|---|
| `manageit/claude-haiku-5.5` | Anthropic | رایگان |
| `manageit/nemotron-3-ultra-550b-a55b:free` | NVIDIA | رایگان |
| `manageit/qwen3.6-35b-a3b-fp8` | Qwen | رایگان |
| `manageit/qwen3.8-27b` | Qwen | رایگان |

## پیش‌نیازها

- Python 3.8+
- نصب‌شده‌ی 9Router در `/Users/ricksabchez/.9router/db/data.sqlite`

## نصب

```bash
# فایل را دانلود کن
curl -O https://raw.githubusercontent.com/<repo>/main/manageit_9router.py
cp config.example.yaml config.yaml
# حالا config.yaml رو ویرایش کن و api_key رو بذار
python3 manageit_9router.py --config config.yaml
```

## استفاده

```bash
# فعال‌سازی با فایل تنظیمات
python3 manageit_9router.py --config config.yaml

# فقط مدل‌های رایگان (پیش‌فرض)
python3 manageit_9router.py --free-only

# نمایش اطلاعات و خارج کردن از اسکریپت (dry-run)
python3 manageit_9router.py --dry-run
```

## چکliste

- مدل‌های رایگان فقط اضافه می‌شن
- کلید تو به هیچ‌کدومی ذخیره نمی‌شه
- ۹روتر بعد از اضافه شدن، خودکار ری‌استارت می‌شه

## لینک‌ها

- 9Router: https://github.com/decolua/9router
- ManageIt: https://ai.manageit.dev
