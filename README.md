# 📅 QJalaliCalendarWidget

> A modern, customizable Jalali (Persian) calendar widget for PySide6\
> ویجت تقویم جلالی حرفه‌ای و قابل شخصی‌سازی برای PySide6

------------------------------------------------------------------------

## ❓ Why QJalaliCalendarWidget? | چرا این پروژه؟

### 🇬🇧 English

Qt does not provide a built-in Jalali (Persian) calendar widget.  
Developers often need to implement custom solutions from scratch.

**QJalaliCalendarWidget** fills this gap by providing a modern, customizable, and production-ready Jalali calendar component for PySide6 applications.

### 🇮🇷 فارسی

Qt به‌صورت پیش‌فرض ویجتی برای تقویم جلالی (شمسی) ارائه نمی‌دهد و توسعه‌دهندگان معمولاً مجبورند این قابلیت را از ابتدا پیاده‌سازی کنند.

پروژه **QJalaliCalendarWidget** این خلأ را با ارائه یک ویجت تقویم جلالی مدرن، قابل شخصی‌سازی و آماده استفاده در محیط‌های واقعی (Production) برای PySide6 برطرف می‌کند.

------------------------------------------------------------------------

## 🌟 Features \| ویژگی‌ها

### 🇬🇧 English

- ✅ Jalali (Persian) calendar support\
- ✅ Built with **PySide6**
- ✅ Right-to-left (RTL) layout support
- ✅ Customizable theme colors
- ✅ Persian / English digit modes
- ✅ Keyboard navigation
- ✅ Date range restriction (min/max)
- ✅ Custom month & weekday names
- ✅ Qt-style signals (`selectionChanged`, `activated`, etc.)
- ✅ Modern UI design

------------------------------------------------------------------------

### 🇮🇷 فارسی

- ✅ پشتیبانی کامل از تقویم جلالی (شمسی)
- ✅ توسعه داده شده با PySide6
- ✅ پشتیبانی کامل از راست‌به‌چپ (RTL)
- ✅ قابلیت شخصی‌سازی رنگ‌ها (تم)
- ✅ نمایش اعداد فارسی یا انگلیسی
- ✅ ناوبری با کیبورد
- ✅ محدودسازی بازه تاریخ (حداقل/حداکثر)
- ✅ امکان تغییر نام ماه‌ها و روزهای هفته
- ✅ سیگنال‌های مشابه QCalendarWidget
- ✅ طراحی مدرن و تمیز

------------------------------------------------------------------------

## 📷 Screenshot \| تصویر ویجت

> تصویر ویجت جلالی

![QJalaliCalendarWidget Screenshot](https://raw.githubusercontent.com/reza-rezvani2052/QJalaliCalendarWidget/master/docs/screenshot.png)

------------------------------------------------------------------------

## 📦 Installation \| نصب

``` bash
pip install qjalalicalendarwidget
```

------------------------------------------------------------------------

## 🚀 Basic Usage \| مثال استفاده

``` python
import sys
from PySide6.QtWidgets import QApplication

from qjalalicalendarwidget import QJalaliCalendarWidget

app = QApplication(sys.argv)


def on_date_confirmed(selected_date):
    print(selected_date.strftime("%Y/%m/%d"))
    app.quit()


def move_to_center(calendar):
    from PySide6.QtGui import QGuiApplication

    calendar.adjustSize()

    # --- Center of Screen ---
    screen = QGuiApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()

    calendar.resize(calendar.sizeHint())
    x = (screen_geometry.width() - calendar.width()) // 2
    y = (screen_geometry.height() - calendar.height()) // 2

    calendar.move(x, y)


calendar = QJalaliCalendarWidget()
calendar.confirmed.connect(on_date_confirmed)

move_to_center(calendar)
calendar.show()

sys.exit(app.exec())
```

------------------------------------------------------------------------

## 🎨 Customization \| شخصی‌سازی

### Change Digit Mode \| تغییر حالت اعداد

``` python
calendar.setDigitMode("fa")  # Persian digits
calendar.setDigitMode("en")  # English digits
```

------------------------------------------------------------------------

### Set Date Range \| تعیین بازه تاریخ

``` python
import jdatetime

calendar.setMinimumDate(jdatetime.date(1403, 1, 1))
calendar.setMaximumDate(jdatetime.date(1404, 12, 29))
```

------------------------------------------------------------------------

### Customize Theme Colors \| تغییر رنگ‌ها

``` python
calendar.setThemeColors(
    selected_bg="#2e7d32",
    selected_fg="#ffffff",
    today_bg="#e8f5e9",
    friday_fg="#d32f2f"
)
```

------------------------------------------------------------------------

## ⌨ Keyboard Navigation \| ناوبری با کیبورد

| Key                     | Action                    |
|-------------------------|---------------------------|
| ← →                     | Previous / Next day       |
| ↑ ↓                     | Previous / Next week      |
| PageUp / PageDown       | Previous / Next month     |
| Shift + PageUp/PageDown | Previous / Next year      |
| Home / End              | First / Last day of month |
| Enter                   | Confirm selection         |

------------------------------------------------------------------------

## 🔔 Signals \| سیگنال‌ها

``` python
calendar.selectionChanged.connect(...)
calendar.activated.connect(...)
calendar.currentPageChanged.connect(...)
calendar.confirmed.connect(...)
calendar.dateSelected.connect(...)
```

------------------------------------------------------------------------

## 📋 Requirements \| پیش‌نیازها

- Python 3.11+
- PySide6
- jdatetime

------------------------------------------------------------------------

## 📄 License \| مجوز

MIT License

------------------------------------------------------------------------

## 🤝 Contributing \| مشارکت

Pull requests are welcome.\
For major changes, please open an issue first.

از پیشنهادها و مشارکت شما استقبال می‌شود.

------------------------------------------------------------------------

## 🔗 Links

- GitHub: https://github.com/reza-rezvani2052/QJalaliCalendarWidget
- PyPI: https://pypi.org/project/qjalalicalendarwidget/

------------------------------------------------------------------------

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.