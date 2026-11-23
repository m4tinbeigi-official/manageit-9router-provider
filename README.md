# ManageIt 9Router Provider

ریپازیتوری کمکی برای افزودن درگاه **ManageIt AI Gateway** به **9Router** به راحتی و خودکارانه.

## مدل‌های رایگان که اضافه می‌شن

| نام مدل | برند | وضعیت |
|---|---|---|
| `manageit/claude-haiku-5.5` | Anthropic | رایگان |
| `manageit/nemotron-3-ultra-550b-a55b:free` | NVIDIA | رایگان |
| `manageit/qwen3.6-35b-a3b-fp8` | Qwen | رایگان |
| `manageit/qwen3.8-27b` | Qwen | رایگان |

هیچ مدل پولی در لیست قرار ندارد. فقط مدل‌های رایگان هستند.

## ساختار فایل‌ها

```
manageit-9router-provider/
├── README.md
├── SKILL.md
├── config.example.yaml
├── manageit_9router.py
└── scripts/
    └── restart-9router.sh
```

## نصب و استفاده

### ۱. فایل‌ها رو دانلود کن
```bash
git clone <repo-url> manageit-9router-provider
cd manageit-9router-provider
```

### ۲. تنظیمات رو پر کن
```bash
cp config.example.yaml config.yaml
# حالا config.yaml رو ویرایش کن و مقدار api_key را بذار
```

### ۳. اجرا کن
```bash
python3 manageit_9router.py --config config.yaml
```

### ۴. ری‌استارت ۹روتر
اختیاری ولی پیشنهادی:
```bash
./scripts/restart-9router.sh
# یا
launchctl kickstart -k gui/$(id -u)/ai.hermes.9router
```

## استفاده اولیه

اگر می‌خواهید مدل‌های بیشتری هم اضافه کنید، به فایل `manageit_9router.py` نگاه نکنید.
فقط مدل‌هایی که در `config.yaml` لیست می‌کنید، اضافه می‌شوند.
