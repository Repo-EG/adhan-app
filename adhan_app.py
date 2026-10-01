import json
import os
import random
import re
import ctypes
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
import winreg
from datetime import datetime, timedelta
from tkinter import font as tkfont, messagebox

from ctypes import wintypes

try:
    from zoneinfo import ZoneInfo  # على ويندوز: pip install tzdata
except ImportError:
    ZoneInfo = None

import customtkinter as ctk
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageTk

# ───────────────────────── المسارات والإعدادات ─────────────────────────
BASE_DIR = os.path.dirname(
    os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__)
)
CONFIG_PATH = os.path.join(BASE_DIR, "settings.json")
CACHE_PATH = os.path.join(BASE_DIR, "timings_cache.json")

# ── إصدار البرنامج: غيّر الرقم قبل كل إصدار جديد ──
APP_VERSION = "1.0.0"
GITHUB_REPO = "Repo-EG/adhan-app"

try:  # مجلد الأذان يُنشأ تلقائيًا ليضع المستخدم ملفاته فيه
    os.makedirs(os.path.join(BASE_DIR, "adhan"), exist_ok=True)
except OSError:
    pass

STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_NAME = "AdhanAppAlexandria"

PRAYERS = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
API_KEYS = {"fajr": "Fajr", "dhuhr": "Dhuhr", "asr": "Asr", "maghrib": "Maghrib", "isha": "Isha"}

RTL = "\u200f"

MONTHS_AR = {
    "January": "يناير", "February": "فبراير", "March": "مارس", "April": "أبريل",
    "May": "مايو", "June": "يونيو", "July": "يوليو", "August": "أغسطس",
    "September": "سبتمبر", "October": "أكتوبر", "November": "نوفمبر", "December": "ديسمبر",
}

MUEZZINS = {
    "1.mp3": {"ar": "أذان الحرم المكي", "en": "Makkah Adhan"},
    "2.mp3": {"ar": "أذان عبد الباسط عبد الصمد", "en": "Abdulbasit Abdulsamad"},
    "3.mp3": {"ar": "أذان مشاري بن راشد العفاسي (الفجر)", "en": "Mishary Alafasy (Fajr)"},
    "4.mp3": {"ar": "أذان عبد الباسط عبد الصمد (2)", "en": "Abdulbasit (2)"},
    "5.mp3": {"ar": "أذان القدس", "en": "Al-Quds Adhan"},
    "6.mp3": {"ar": "أذان ناصر القطامي", "en": "Nasser Al-Qatami"},
}

TRANSLATIONS = {
    "ar": {
        "app_title": "مواقيت الصلاة والأذان",
        "header_title": "🕌 مواقيت الصلاة",
        "city": "الإسكندرية، مصر",
        "test_btn": "▶  تجربة الأذان",
        "stop_btn": "⏹  إيقاف الأذان",
        "settings_btn": "⚙ الإعدادات",
        "settings_title": "⚙ الإعدادات",
        "general_section": "عام",
        "time_section": "الوقت",
        "adhan_section": "الأذان",
        "location_section": "الموقع وطريقة الحساب",
        "location_option": "المدينة / المحافظة",
        "method_option": "طريقة الحساب",
        "method_auto": "تلقائي (حسب الدولة)",
        "school_option": "مذهب حساب العصر",
        "school_standard": "الجمهور (الشافعي/المالكي/الحنبلي)",
        "school_hanafi": "الحنفي",
        "offsets_section": "تعديل المواقيت يدويًا (بالدقائق)",
        "search_title": "اختيار الموقع",
        "search_hint": "اكتب اسم المدينة أو المحافظة أو القرية (عربي أو إنجليزي)",
        "search_placeholder": "مثال: الإسكندرية، London، Lahore",
        "search_btn": "بحث",
        "searching": "جارٍ البحث...",
        "no_results": "لا توجد نتائج. جرّب كتابة الاسم بشكل آخر.",
        "net_error": "تعذر الاتصال بالإنترنت.",
        "update_available": "🔔 يتوفر تحديث {version} — اضغط للتحميل",
        "auto_detect_option": "الموقع التلقائي",
        "auto_detect_btn": "📍 تحديد موقعي تلقائيًا",
        "detecting": "جارٍ التحديد...",
        "detect_failed": "تعذر تحديد موقعك تلقائيًا. تأكد من الاتصال بالإنترنت أو اختر المدينة يدويًا.",
        "detect_windows": "تم تحديد موقعك عبر خدمة الموقع في ويندوز. راجع المدينة ثم اضغط «حفظ وإغلاق».",
        "detect_ip": "تم التحديد تقريبيًا من عنوان الإنترنت، وقد يظهر مكان مزوّد الخدمة وليس مدينتك بالضبط. إن لم تكن صحيحة فاخترها يدويًا، أو فعّل خدمة الموقع في ويندوز (الخصوصية ← الموقع) وأعد المحاولة.",
        "lang_option": "اللغة / Language",
        "theme_option": "المظهر",
        "dark_theme": "داكن",
        "light_theme": "فاتح",
        "time_format_option": "نظام عرض الوقت",
        "dst_option": "التوقيت الصيفي والشتوي",
        "dst_auto": "تلقائي",
        "dst_summer": "توقيت صيفي (+1 ساعة)",
        "dst_winter": "توقيت شتوي",
        "12h": "نظام 12 ساعة",
        "24h": "نظام 24 ساعة",
        "startup_option": "فتح التطبيق عند تشغيل الجهاز",
        "takbeer_only_option": "التنبيه بالتكبير فقط ⚡",
        "save_btn": "حفظ وإغلاق",
        "fajr": "الفجر", "dhuhr": "الظهر", "asr": "العصر", "maghrib": "المغرب", "isha": "العشاء",
        "next_prayer": "الصلاة القادمة: {prayer} بعد {time}",
        "loading": "جارٍ تحميل المواقيت...",
        "playing": "🔊 جارٍ تشغيل {prayer}:",
        "file_missing": "⚠️ ملفات الأذان غير موجودة في:\n{path}",
        "audio_error": "⚠️ تعذر تشغيل الصوت:\n{error}",
        "startup_enabled": "تم تفعيل التشغيل التلقائي مع ويندوز.",
        "startup_disabled": "تم إيقاف التشغيل التلقائي.",
        "error": "خطأ",
        "warning_title": "⚠️ تنبيه التوقيت",
        "dst_warn_msg": "يُضبط التوقيت المحلي تلقائيًا من النظام.\nهل أنت متأكد من تغييره يدويًا؟",
        "confirm_yes": "نعم، متأكد",
        "confirm_no": "إلغاء",
        "test_play": "تجربة الصوت",
        "muezzin_settings_section": "اختر المؤذن لكل صلاة",
        "random": "🔀 عشوائي",
        "palestine_msg": "🤲 لا تنسَ الدعاء لإخواننا في فلسطين",
    },
    "en": {
        "app_title": "Prayer Times & Adhan",
        "header_title": "🕌 Prayer Times",
        "city": "Alexandria, Egypt",
        "test_btn": "▶  Test Adhan",
        "stop_btn": "⏹  Stop Adhan",
        "settings_btn": "⚙ Settings",
        "settings_title": "⚙ Settings",
        "general_section": "General",
        "time_section": "Time",
        "adhan_section": "Adhan",
        "location_section": "Location & Calculation",
        "location_option": "City / Governorate",
        "method_option": "Calculation Method",
        "method_auto": "Auto (by country)",
        "school_option": "Asr Calculation",
        "school_standard": "Standard (Shafi/Maliki/Hanbali)",
        "school_hanafi": "Hanafi",
        "offsets_section": "Manual Adjustment (minutes)",
        "search_title": "Choose Location",
        "search_hint": "Type a city, governorate or town name (Arabic or English)",
        "search_placeholder": "e.g. Alexandria, London, Lahore",
        "search_btn": "Search",
        "searching": "Searching...",
        "no_results": "No results. Try a different spelling.",
        "net_error": "Could not connect to the internet.",
        "update_available": "🔔 Update {version} available — click to download",
        "auto_detect_option": "Automatic Location",
        "auto_detect_btn": "📍 Detect My Location",
        "detecting": "Detecting...",
        "detect_failed": "Could not detect your location. Check your internet connection or choose a city manually.",
        "detect_windows": "Location detected via Windows Location Service. Check the city, then press Save & Close.",
        "detect_ip": "Approximate location from your IP address; it may show your ISP's city instead of yours. If it is wrong, choose manually, or enable Windows Location (Privacy > Location) and retry.",
        "lang_option": "Language / اللغة",
        "theme_option": "Theme",
        "dark_theme": "Dark",
        "light_theme": "Light",
        "time_format_option": "Time Format",
        "dst_option": "Daylight Saving Time (DST)",
        "dst_auto": "Auto",
        "dst_summer": "Summer Time (+1h)",
        "dst_winter": "Winter Time",
        "12h": "12-Hour Format",
        "24h": "24-Hour Format",
        "startup_option": "Open app when the PC starts",
        "takbeer_only_option": "Takbeer Only ⚡",
        "save_btn": "Save & Close",
        "fajr": "Fajr", "dhuhr": "Dhuhr", "asr": "Asr", "maghrib": "Maghrib", "isha": "Isha",
        "next_prayer": "Next: {prayer} in {time}",
        "loading": "Loading prayer times...",
        "playing": "🔊 Playing {prayer}:",
        "file_missing": "⚠ Adhan files not found in:\n{path}",
        "audio_error": "⚠ Could not play audio:\n{error}",
        "startup_enabled": "The app will now start automatically with Windows.",
        "startup_disabled": "Automatic startup has been turned off.",
        "error": "Error",
        "warning_title": "⚠ Time Warning",
        "dst_warn_msg": "Local time is set automatically by your system.\nAre you sure you want to change it manually?",
        "confirm_yes": "Yes, Change",
        "confirm_no": "Cancel",
        "test_play": "Audio Test",
        "muezzin_settings_section": "Choose the muezzin for each prayer",
        "random": "🔀 Random",
        "palestine_msg": "🤲 Don't forget to pray for Palestine",
    },
}
# علامة الاتجاه من اليمين لليسار لكل النصوص العربية (يصحح مكان الرموز والأقواس)
for _k, _v in list(TRANSLATIONS["ar"].items()):
    TRANSLATIONS["ar"][_k] = RTL + _v

DEFAULT_LOCATION = {
    "label": {"ar": "الإسكندرية، مصر", "en": "Alexandria, Egypt"},
    "cc": "EG", "lat": 31.2001, "lng": 29.9187, "tz": "Africa/Cairo",
}

DEFAULT_CONFIG = {
    "lang": "ar",
    "theme": "Dark",
    "use_24h": False,
    "takbeer_only": False,
    "dst_mode": "Auto",  # Auto | Summer | Winter
    "muezzins": {p: "random" for p in PRAYERS},
    "location": DEFAULT_LOCATION,
    "method": "auto",    # "auto" (حسب الدولة) أو رقم طريقة الحساب
    "school": 0,         # 0 = الجمهور، 1 = الحنفي (يؤثر على العصر فقط)
    "offsets": {p: 0 for p in PRAYERS},  # تعديل يدوي بالدقائق لكل صلاة
}


def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        for key in ("muezzins", "offsets"):
            part = saved.pop(key, {})
            if isinstance(part, dict):
                cfg[key].update({k: v for k, v in part.items() if k in PRAYERS})
        loc = saved.pop("location", None)
        if isinstance(loc, dict) and all(k in loc for k in ("label", "cc", "lat", "lng", "tz")):
            cfg["location"] = loc
        cfg.update({k: v for k, v in saved.items() if k in cfg})
        cfg["offsets"] = {p: int(cfg["offsets"].get(p, 0) or 0) for p in PRAYERS}
    except (OSError, ValueError, TypeError, KeyError):
        pass
    if cfg["method"] != "auto" and not isinstance(cfg["method"], int):
        cfg["method"] = "auto"
    if cfg["school"] not in (0, 1):
        cfg["school"] = 0
    return cfg


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print("تعذر حفظ الإعدادات:", e)


# ───────────────────────── المواقيت: الموقع + طريقة الحساب ─────────────────────────
# ───────────────────────── تشغيل الصوت عبر MCI (مدمج في ويندوز) ─────────────────────────
_winmm = ctypes.windll.winmm
_winmm.mciSendStringW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.UINT, ctypes.c_void_p]
_winmm.mciSendStringW.restype = wintypes.DWORD
_winmm.mciGetErrorStringW.argtypes = [wintypes.DWORD, wintypes.LPWSTR, wintypes.UINT]


def mci(command):
    buf = ctypes.create_unicode_buffer(256)
    err = _winmm.mciSendStringW(command, buf, 255, None)
    if err:
        eb = ctypes.create_unicode_buffer(256)
        _winmm.mciGetErrorStringW(err, eb, 255)
        raise RuntimeError(f"MCI {err}: {eb.value}")
    return buf.value


GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
CAL_URL = "https://api.aladhan.com/v1/calendar"

# رقم الطريقة في Aladhan: (الاسم بالعربية، الاسم بالإنجليزية)
METHODS = {
    3: ("رابطة العالم الإسلامي", "Muslim World League"),
    5: ("الهيئة المصرية العامة للمساحة", "Egyptian General Authority of Survey"),
    4: ("أم القرى - مكة المكرمة", "Umm Al-Qura, Makkah"),
    2: ("أمريكا الشمالية (ISNA)", "Islamic Society of North America"),
    1: ("جامعة العلوم الإسلامية - كراتشي", "Univ. of Islamic Sciences, Karachi"),
    8: ("منطقة الخليج", "Gulf Region"),
    9: ("الكويت", "Kuwait"),
    10: ("قطر", "Qatar"),
    16: ("دبي", "Dubai"),
    23: ("الأردن", "Jordan"),
    18: ("تونس", "Tunisia"),
    19: ("الجزائر", "Algeria"),
    21: ("المغرب", "Morocco"),
    13: ("تركيا - رئاسة الشؤون الدينية", "Diyanet, Turkey"),
    12: ("اتحاد المنظمات الإسلامية - فرنسا", "UOIF, France"),
    14: ("روسيا", "Russia"),
    11: ("سنغافورة", "Singapore"),
    17: ("ماليزيا (JAKIM)", "JAKIM, Malaysia"),
    20: ("إندونيسيا (KEMENAG)", "KEMENAG, Indonesia"),
    22: ("لشبونة - البرتغال", "Lisbon, Portugal"),
    7: ("طهران", "Tehran"),
    0: ("الجعفري", "Shia Ithna-Ashari (Jafari)"),
    15: ("لجنة رؤية الهلال", "Moonsighting Committee"),
}

# الطريقة التلقائية حسب رمز الدولة (غير المذكورة تأخذ رابطة العالم الإسلامي)
METHOD_BY_CC = {
    "EG": 5, "SA": 4, "AE": 16, "KW": 9, "QA": 10, "BH": 8, "OM": 8, "JO": 23,
    "TN": 18, "DZ": 19, "MA": 21, "TR": 13, "RU": 14, "SG": 11, "MY": 17, "ID": 20,
    "FR": 12, "PT": 22, "IR": 7, "PK": 1, "IN": 1, "BD": 1, "AF": 1, "US": 2, "CA": 2,
}


class PrayerService:
    # يجلب جدول الشهر كاملًا بإحداثيات المدينة ومنطقتها الزمنية، ويحفظه للعمل بدون إنترنت.

    def __init__(self):
        self.days = {}  # "YYYY-MM-DD" -> {"timings", "hijri", "gregorian"}
        self.key = None
        self._fetching = False
        self._next_try = 0

    @staticmethod
    def resolve_method(cfg):
        m = cfg.get("method", "auto")
        if isinstance(m, int):
            return m
        return METHOD_BY_CC.get(str(cfg["location"].get("cc", "")).upper(), 3)

    def make_key(self, cfg):
        loc = cfg["location"]
        return (f"{float(loc['lat']):.4f},{float(loc['lng']):.4f}|{loc['tz']}|"
                f"{self.resolve_method(cfg)}|{cfg['school']}")

    def _load_cache(self, key):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                c = json.load(f)
            if c.get("key") == key:
                return c.get("days", {})
        except (OSError, ValueError):
            pass
        return {}

    def _save_cache(self):
        cutoff = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        self.days = {k: v for k, v in self.days.items() if k >= cutoff}
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump({"key": self.key, "days": self.days}, f, ensure_ascii=False)
        except OSError:
            pass

    def day(self, dt):
        return self.days.get(dt.strftime("%Y-%m-%d"))

    def refresh_if_needed(self, now, cfg):
        key = self.make_key(cfg)
        if key != self.key:  # تغيّر الموقع أو الطريقة: ابدأ من جديد
            self.key = key
            self.days = self._load_cache(key)
            self._next_try = 0
        if self._fetching or time.time() < self._next_try:
            return
        for d in (now, now + timedelta(days=1)):  # اليوم وغدًا (لفجر الغد بعد العشاء)
            if self.day(d) is None:
                loc = cfg["location"]
                params = {"latitude": loc["lat"], "longitude": loc["lng"],
                          "method": self.resolve_method(cfg), "school": cfg["school"],
                          "timezonestring": loc["tz"], "month": d.month, "year": d.year}
                self._fetching = True
                need = d.strftime("%Y-%m-%d")
                threading.Thread(target=self._fetch, args=(key, params, need), daemon=True).start()
                return

    def _fetch(self, key, params, need):
        try:
            r = requests.get(CAL_URL, params=params, timeout=12)
            r.raise_for_status()
            fresh = {}
            for item in r.json()["data"]:
                g, h = item["date"]["gregorian"], item["date"]["hijri"]
                dd, mm, yy = g["date"].split("-")
                fresh[f"{yy}-{mm}-{dd}"] = {
                    "timings": {k: item["timings"][k].split()[0][:5] for k in API_KEYS.values()},
                    "hijri": {"day": h["day"], "year": h["year"],
                              "month_ar": h["month"]["ar"], "month_en": h["month"]["en"]},
                    "gregorian": {"day": g["day"], "year": g["year"], "month_en": g["month"]["en"]},
                }
            if key == self.key:  # تجاهل النتيجة لو تغيّر الموقع أثناء الجلب
                self.days = {**self.days, **fresh}
                self._save_cache()
                if need not in self.days:
                    self._next_try = time.time() + 300
        except Exception as e:
            print("خطأ في جلب المواقيت:", e)
            self._next_try = time.time() + 60
        finally:
            self._fetching = False


# ───────────────────────── فحص التحديثات (GitHub Releases) ─────────────────────────
def parse_version(text):
    nums = re.findall(r"\d+", str(text))[:4]
    return tuple(int(n) for n in nums) or (0,)


class UpdateChecker:
    # يسأل GitHub عن آخر إصدار منشور، ويعيد الفحص كل 6 ساعات في الخلفية.

    def __init__(self):
        self.latest = None  # رقم الإصدار الأحدث إن وُجد (مثل "1.1.0")
        self.url = None
        self._fetching = False
        self._next = 0

    def check_if_due(self):
        if self._fetching or time.time() < self._next:
            return
        self._fetching = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            r = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=10,
                             headers={"Accept": "application/vnd.github+json", "User-Agent": "AdhanApp"})
            if r.status_code == 404:  # لا يوجد إصدار منشور بعد
                self.latest = None
            else:
                r.raise_for_status()
                d = r.json()
                tag = d.get("tag_name", "")
                if parse_version(tag) > parse_version(APP_VERSION):
                    self.latest = tag.lstrip("vV")
                    self.url = d.get("html_url")
                else:
                    self.latest = None
            self._next = time.time() + 6 * 3600
        except Exception as e:
            print("تعذر فحص التحديثات:", e)
            self._next = time.time() + 600
        finally:
            self._fetching = False


# ───────────────────────── عناصر الرسم على Canvas ─────────────────────────
W, H = 450, 620  # أبعاد النافذة المنطقية

# (المستطيل، نصف القطر) للبطاقات الزجاجية
HEADER_BOX = (25, 23, 425, 138)
TIMES_BOX = (25, 289, 425, 479)
GLASS_TINT = (10, 15, 26, 70)   # آخر رقم = قوة التعتيم (0 شفاف تمامًا، 255 معتم)
GLASS_BLUR = 3                  # قوة تغبيش الخلفية خلف الزجاج (0 لإلغائه)


class CText:
    """نص على الـ Canvas مع ظل خفيف لضمان وضوحه فوق أي صورة."""

    def __init__(self, app, x, y, size, color, anchor="center", justify="center"):
        self.c = app.canvas
        self.font = tkfont.Font(family="Segoe UI", size=-app.px(size), weight="bold")
        px, py, d = app.px(x), app.px(y), max(1, app.px(1))
        self.shadow = self.c.create_text(px + d, py + d, text="", fill="#05080f",
                                         font=self.font, anchor=anchor, justify=justify)
        self.main = self.c.create_text(px, py, text="", fill=color,
                                       font=self.font, anchor=anchor, justify=justify)

    def set(self, text):
        self.c.itemconfig(self.shadow, text=text)
        self.c.itemconfig(self.main, text=text)

    def ids(self):
        return (self.shadow, self.main)


class CButton:
    """زر بحواف منحنية وشفافية حقيقية مرسوم على الـ Canvas."""

    def __init__(self, app, box, radius, fill, hover, size, command, tag, outline=None):
        self.app, self.box, self.radius, self.outline = app, box, radius, outline
        self.hovered = False
        x0, y0, x1, y1 = box
        self.normal = self.hover_img = None
        self.img_id = app.canvas.create_image(app.px(x0), app.px(y0), anchor="nw")
        self.text = CText(app, (x0 + x1) / 2, (y0 + y1) / 2, size, "#ffffff")
        self.set_colors(fill, hover)
        for item in (self.img_id, *self.text.ids()):
            app.canvas.addtag_withtag(tag, item)
        app.canvas.tag_bind(tag, "<Enter>", lambda e: self._hover(True))
        app.canvas.tag_bind(tag, "<Leave>", lambda e: self._hover(False))
        app.canvas.tag_bind(tag, "<Button-1>", lambda e: command())

    def set_colors(self, fill, hover):
        x0, y0, x1, y1 = self.box
        w, h = x1 - x0, y1 - y0
        self.normal = self.app.rounded(w, h, self.radius, fill, self.outline)
        self.hover_img = self.app.rounded(w, h, self.radius, hover, self.outline)
        self.app.canvas.itemconfig(self.img_id, image=self.hover_img if self.hovered else self.normal)

    def set_text(self, text):
        self.text.set(text)

    def set_visible(self, visible):
        state = "normal" if visible else "hidden"
        for item in (self.img_id, *self.text.ids()):
            self.app.canvas.itemconfig(item, state=state)

    def _hover(self, on):
        self.hovered = on
        self.app.canvas.itemconfig(self.img_id, image=self.hover_img if on else self.normal)
        self.app.canvas.configure(cursor="hand2" if on else "")


GREEN = ((16, 185, 129, 235), (5, 150, 105, 245))
RED = ((239, 68, 68, 235), (220, 38, 38, 245))
DARK = ((30, 41, 59, 190), (51, 65, 85, 225))

# لوحة ألوان نافذة الإعدادات: (الوضع الفاتح، الوضع الداكن)
UI = {
    "bg": ("#f1f5f9", "#0b1220"),
    "card": ("#ffffff", "#131c2e"),
    "border": ("#e2e8f0", "#1f2a40"),
    "text": ("#0f172a", "#e2e8f0"),
    "muted": ("#64748b", "#8b9bb4"),
    "accent": ("#0d9488", "#2dd4bf"),
    "accent_hover": ("#0f766e", "#5eead4"),
    "on_accent": ("#ffffff", "#042f2e"),
    "field": ("#eef2f7", "#1b2740"),
    "field_btn": ("#dbe3ee", "#24334f"),
    "field_hover": ("#cbd5e1", "#2e4062"),
    "track": ("#cbd5e1", "#334155"),
    "warn": ("#d97706", "#fbbf24"),
}


# ───────────────────────── التطبيق ─────────────────────────
class AdhanApp:
    def __init__(self):
        self.cfg = load_config()
        self.service = PrayerService()
        self.updater = UpdateChecker()
        self.audio_proc = None
        self.audio_backend = None  # None | "mci" | "ps"
        self._audio_started = 0
        self.last_triggered = {}
        self.settings_win = None
        self._tz_name = None
        self._tz = None

        ctk.set_appearance_mode(self.cfg["theme"])
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.geometry(f"{W}x{H}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # معامل تكبير الشاشة، لأن Canvas لا يتكبّر تلقائيًا مثل عناصر customtkinter
        self.s = max(1.0, self.root.winfo_fpixels("1i") / 96)

        self._build_ui()
        self.update_ui_language()
        self.tick()

    # ---------- أدوات مساعدة ----------
    def px(self, v):
        return int(round(v * self.s))

    def t(self, key):
        return TRANSLATIONS[self.cfg["lang"]].get(key, key)

    @property
    def is_ar(self):
        return self.cfg["lang"] == "ar"

    @staticmethod
    def font(size, bold=True):
        return ctk.CTkFont(family="Segoe UI", size=size, weight="bold" if bold else "normal")

    def tzinfo(self):
        name = self.cfg["location"].get("tz")
        if name != self._tz_name:
            self._tz_name = name
            try:
                self._tz = ZoneInfo(name) if ZoneInfo else None
            except Exception:
                self._tz = None
                print("تعذر تحميل المنطقة الزمنية، ثبّت الحزمة:  pip install tzdata")
        return self._tz

    def now(self):
        # الوقت الحالي في مدينة الصلاة نفسها (وليس بالضرورة توقيت الجهاز)
        tz = self.tzinfo()
        return datetime.now(tz) if tz else datetime.now().astimezone()

    def adjust(self, key, time_str, now):
        try:
            dt = datetime.strptime(time_str, "%H:%M")
        except (TypeError, ValueError):
            return "--:--"
        d = now.dst()
        dst_active = bool(d) if d is not None else time.localtime().tm_isdst > 0
        mode = self.cfg["dst_mode"]
        if mode == "Summer" and not dst_active:
            dt += timedelta(hours=1)
        elif mode == "Winter" and dst_active:
            dt -= timedelta(hours=1)
        dt += timedelta(minutes=int(self.cfg["offsets"].get(key, 0)))
        return dt.strftime("%H:%M")

    def location_label(self):
        label = self.cfg["location"]["label"]
        text = label.get(self.cfg["lang"]) or next(iter(label.values()), "")
        return (RTL + text) if self.is_ar else text

    def format_time(self, time_str):
        try:
            dt = datetime.strptime(time_str, "%H:%M")
        except (TypeError, ValueError):
            return "--:--"
        if self.cfg["use_24h"]:
            return dt.strftime("%H:%M")
        h12 = dt.hour % 12 or 12
        if self.is_ar:
            suffix = "ص" if dt.hour < 12 else "م"
        else:
            suffix = "AM" if dt.hour < 12 else "PM"
        return f"{h12:02d}:{dt.minute:02d} {suffix}"

    def format_dates(self, day):
        if not day:
            return "--   |   --"
        h, g = day["hijri"], day["gregorian"]
        if self.is_ar:
            g_month = MONTHS_AR.get(g["month_en"], g["month_en"])
            return (f"{RTL}{h['day']} {h['month_ar']} {h['year']} هـ   |   "
                    f"{RTL}{g['day']} {g_month} {g['year']} م")
        return (f"{h['day']} {h['month_en']} {h['year']} AH   |   "
                f"{g['day']} {g['month_en']} {g['year']} AD")

    @staticmethod
    def make_location(r, is_ar):
        name = r.get("name", "")
        admin = r.get("admin1") or ""
        parts = [x for x in (admin if admin != name else "", r.get("country") or "") if x]
        sep = "، " if is_ar else ", "
        label = name + (sep + sep.join(parts) if parts else "")
        return {"label": {"ar": label, "en": label}, "detail": sep.join(parts), "name": name,
                "cc": (r.get("country_code") or "").upper(), "lat": float(r["latitude"]),
                "lng": float(r["longitude"]), "tz": r.get("timezone") or ""}

    # ---------- الرسم ----------
    def rounded(self, w, h, r, fill, outline=None):
        """مستطيل منحني الحواف شبه شفاف (مع تنعيم الحواف)."""
        ss = 4
        wp, hp, rp = self.px(w), self.px(h), self.px(r)
        img = Image.new("RGBA", (wp * ss, hp * ss), (0, 0, 0, 0))
        ImageDraw.Draw(img).rounded_rectangle(
            [0, 0, wp * ss - 1, hp * ss - 1], radius=rp * ss, fill=fill,
            outline=outline, width=ss if outline else 0)
        photo = ImageTk.PhotoImage(img.resize((wp, hp), Image.LANCZOS))
        self._keep.append(photo)
        return photo

    def load_wall(self):
        wp, hp = self.px(W), self.px(H)
        for name in ("wall.png", "wall.jpg"):
            path = os.path.join(BASE_DIR, name)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    k = max(wp / img.width, hp / img.height)  # ملء النافذة دون تشويه
                    img = img.resize((max(wp, round(img.width * k)), max(hp, round(img.height * k))),
                                     Image.LANCZOS)
                    left, top = (img.width - wp) // 2, (img.height - hp) // 2
                    return img.crop((left, top, left + wp, top + hp))
                except OSError:
                    pass
        return Image.new("RGBA", (wp, hp), (15, 23, 42, 255))

    def bake_glass(self, base, box, radius):
        """يرسم بطاقة زجاجية داخل صورة الخلفية نفسها: تغبيش + تعتيم خفيف + حد ناعم."""
        x0, y0, x1, y1 = (self.px(v) for v in box)
        w, h, r, ss = x1 - x0, y1 - y0, self.px(radius), 4

        mask = Image.new("L", (w * ss, h * ss), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=r * ss, fill=255)
        mask = mask.resize((w, h), Image.LANCZOS)

        region = base.crop((x0, y0, x1, y1))
        if GLASS_BLUR:
            region = region.filter(ImageFilter.GaussianBlur(self.px(GLASS_BLUR)))
        region = Image.alpha_composite(region, Image.new("RGBA", (w, h), GLASS_TINT))
        base.paste(region, (x0, y0), mask)

        border = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        ImageDraw.Draw(border).rounded_rectangle(
            [0, 0, w * ss - 1, h * ss - 1], radius=r * ss, outline=(255, 255, 255, 55), width=ss)
        base.alpha_composite(border.resize((w, h), Image.LANCZOS), (x0, y0))

    # ---------- بناء الواجهة ----------
    def _build_ui(self):
        self._keep = []  # مراجع الصور حتى لا يحذفها Python
        wall = self.load_wall()
        self.bake_glass(wall, HEADER_BOX, 16)
        self.bake_glass(wall, TIMES_BOX, 16)
        self._bg = ImageTk.PhotoImage(wall.convert("RGB"))

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bd=0, bg="#0f172a")
        self.canvas.place(x=0, y=0, width=self.px(W), height=self.px(H))
        self.canvas.create_image(0, 0, image=self._bg, anchor="nw")

        # شرائط تمييز الصلاة القادمة (تُرسم قبل النصوص لتبقى تحتها)
        hl_img = self.rounded(376, 32, 10, (29, 78, 216, 170))
        self.highlights = {}
        for i, p in enumerate(PRAYERS):
            y = TIMES_BOX[1] + 10 + i * 34
            self.highlights[p] = self.canvas.create_image(
                self.px(37), self.px(y), anchor="nw", image=hl_img, state="hidden")

        # الهيدر
        self.title_text = CText(self, W / 2, 43, 23, "#ffffff")
        self.sub_text = CText(self, W / 2, 68, 13, "#cbd5e1")
        self.date_text = CText(self, W / 2, 90, 12, "#38bdf8")
        self.next_text = CText(self, W / 2, 112, 13, "#34d399")

        # صفوف المواقيت
        self.name_texts, self.time_texts = {}, {}
        for i, p in enumerate(PRAYERS):
            cy = TIMES_BOX[1] + 10 + i * 34 + 16
            self.name_texts[p] = CText(self, 400, cy, 14, "#38bdf8", anchor="e")
            self.time_texts[p] = CText(self, 50, cy, 14, "#ffffff", anchor="w")

        self.test_btn = CButton(self, (31, 487, 419, 525), 12, *GREEN, 14, self.toggle_test, "test")
        self.muezzin_text = CText(self, W / 2, 546, 11, "#38bdf8")
        self.settings_btn = CButton(self, (150, 568, 300, 600), 10, *DARK, 12, self.open_settings,
                                    "settings", outline=(255, 255, 255, 40))
        self.palestine_text = CText(self, W / 2, 610, 11, "#f59e0b")
        # شريط التحديث: يظهر أعلى النافذة عند وجود إصدار أحدث
        self.update_btn = CButton(self, (85, 2, 365, 22), 10, (16, 185, 129, 235), (5, 150, 105, 245),
                                  11, self.open_update_page, "update")
        self.update_btn.set_visible(False)

    def update_ui_language(self):
        self.root.title(self.t("app_title"))
        self.title_text.set(self.t("header_title"))
        self.sub_text.set(self.location_label())
        self.settings_btn.set_text(self.t("settings_btn"))
        self.palestine_text.set(self.t("palestine_msg"))
        for p, txt in self.name_texts.items():
            txt.set(self.t(p))
        self.update_test_button()

    def update_test_button(self):
        if self.is_playing():
            self.test_btn.set_colors(*RED)
            self.test_btn.set_text(self.t("stop_btn"))
        else:
            self.test_btn.set_colors(*GREEN)
            self.test_btn.set_text(self.t("test_btn"))

    # ---------- الحلقة الرئيسية ----------
    def tick(self):
        try:
            self.update()
        except Exception as e:
            print("خطأ في التحديث:", e)
        self.root.after(1000, self.tick)

    def update(self):
        now = self.now()
        self.service.refresh_if_needed(now, self.cfg)

        self.updater.check_if_due()
        if self.updater.latest:
            self.update_btn.set_text(self.t("update_available").format(version=self.updater.latest))
            self.update_btn.set_visible(True)
        else:
            self.update_btn.set_visible(False)

        self.check_audio()

        day = self.service.day(now)
        if not day:
            self.next_text.set(self.t("loading"))
            self.date_text.set("--   |   --")
            for p in PRAYERS:
                self.time_texts[p].set("--:--")
                self.canvas.itemconfig(self.highlights[p], state="hidden")
            return

        self.date_text.set(self.format_dates(day))

        today = now.strftime("%Y-%m-%d")
        dts = {}
        for p in PRAYERS:
            ts = self.adjust(p, day["timings"].get(API_KEYS[p]), now)
            self.time_texts[p].set(self.format_time(ts))
            self.canvas.itemconfig(self.highlights[p], state="hidden")
            if ts != "--:--":
                h, m = map(int, ts.split(":"))
                dts[p] = now.replace(hour=h, minute=m, second=0, microsecond=0)

        upcoming = {p: d for p, d in dts.items() if d > now}
        if not upcoming and "fajr" in dts:
            fajr = dts["fajr"] + timedelta(days=1)
            tom = self.service.day(now + timedelta(days=1))
            if tom:  # فجر الغد الفعلي من الجدول
                ts = self.adjust("fajr", tom["timings"].get("Fajr"), now)
                if ts != "--:--":
                    h, m = map(int, ts.split(":"))
                    fajr = (now + timedelta(days=1)).replace(hour=h, minute=m, second=0, microsecond=0)
            upcoming = {"fajr": fajr}
        if upcoming:
            nxt = min(upcoming, key=upcoming.get)
            secs = int((upcoming[nxt] - now).total_seconds())
            hrs, rem = divmod(secs, 3600)
            mins, s = divmod(rem, 60)
            self.canvas.itemconfig(self.highlights[nxt], state="normal")
            self.next_text.set(self.t("next_prayer").format(
                prayer=self.t(nxt).replace(RTL, ""), time=f"{hrs:02d}:{mins:02d}:{s:02d}"))

        for p, d in dts.items():
            if 0 <= (now - d).total_seconds() < 15 and self.last_triggered.get(p) != today:
                self.last_triggered[p] = today
                self.play_adhan(p, self.t(p))
                break

    # ---------- الصوت ----------
    def resolve_file(self, name):
        if self.cfg["takbeer_only"]:
            stem, ext = os.path.splitext(name)
            for cand in (f"{stem} takbeer{ext}", name):
                p = os.path.join(BASE_DIR, "takbeer", cand)
                if os.path.exists(p):
                    return p
        p = os.path.join(BASE_DIR, "adhan", name)
        return p if os.path.exists(p) else None

    def is_playing(self):
        return self.audio_backend is not None

    def stop_audio(self):
        backend, self.audio_backend = self.audio_backend, None
        if backend == "mci":
            for cmd in ("stop adhan", "close adhan"):
                try:
                    mci(cmd)
                except RuntimeError:
                    pass
        proc, self.audio_proc = self.audio_proc, None
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except OSError:
                pass
        self.muezzin_text.set("")
        self.update_test_button()

    def check_audio(self):
        # يُستدعى كل ثانية: ينهي حالة التشغيل عند انتهاء الملف
        if not self.audio_backend or time.time() - self._audio_started < 3:
            return
        if self.audio_backend == "mci":
            try:
                mode = mci("status adhan mode")
            except RuntimeError:
                mode = "stopped"
            if mode == "stopped":
                self.stop_audio()
        elif self.audio_proc and self.audio_proc.poll() is not None:
            self.stop_audio()

    def toggle_test(self):
        if self.is_playing():
            self.stop_audio()
        else:
            self.play_adhan()

    def _play_mci(self, path):
        try:
            mci("close adhan")
        except RuntimeError:
            pass
        mci(f'open "{path}" type mpegvideo alias adhan')
        try:
            mci("play adhan")
        except RuntimeError:
            try:
                mci("close adhan")
            except RuntimeError:
                pass
            raise
        self.audio_backend = "mci"

    def _play_powershell(self, path):
        safe = path.replace("'", "''")
        ps = (
            "Add-Type -AssemblyName presentationCore; "
            "$p = New-Object System.Windows.Media.MediaPlayer; "
            f"$p.Open([uri]'{safe}'); $p.Play(); "
            "while (-not $p.NaturalDuration.HasTimeSpan) { Start-Sleep -Milliseconds 50 }; "
            "Start-Sleep -Milliseconds ([int]$p.NaturalDuration.TimeSpan.TotalMilliseconds + 500)"
        )
        self.audio_proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
            creationflags=subprocess.CREATE_NO_WINDOW)
        self.audio_backend = "ps"

    def play_adhan(self, prayer_key=None, display_name=None):
        self.stop_audio()
        display_name = display_name or self.t("test_play")

        choice = self.cfg["muezzins"].get(prayer_key, "random")
        if choice == "random" or choice not in MUEZZINS:
            available = [f for f in MUEZZINS if self.resolve_file(f)]
            choice = random.choice(available) if available else None

        path = self.resolve_file(choice) if choice else None
        if not path:
            self.muezzin_text.set(self.t("file_missing").format(path=os.path.join(BASE_DIR, "adhan")))
            return
        path = os.path.abspath(path)

        error = None
        try:
            self._play_mci(path)
        except Exception as e:  # احتياطي: PowerShell
            print("فشل التشغيل عبر MCI:", e)
            try:
                self._play_powershell(path)
            except Exception as e2:
                print("فشل التشغيل عبر PowerShell:", e2)
                error = e
        if error:
            self.muezzin_text.set(self.t("audio_error").format(error=str(error)[:70]))
            return

        self._audio_started = time.time()
        self.update_test_button()
        msg = self.t("playing").format(prayer=display_name.replace(RTL, ""))
        name = MUEZZINS[choice][self.cfg["lang"]]
        prefix = RTL if self.is_ar else ""
        self.muezzin_text.set(f"{prefix}{msg}\n{prefix}{name}")

    # ---------- التشغيل التلقائي مع ويندوز ----------
    @staticmethod
    def is_in_startup():
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ) as k:
                winreg.QueryValueEx(k, STARTUP_NAME)
            return True
        except FileNotFoundError:
            return False

    def set_startup(self, enabled):
        if getattr(sys, "frozen", False):
            cmd = f'"{sys.executable}"'
        else:
            pyw = sys.executable.replace("python.exe", "pythonw.exe")
            pyw = pyw if os.path.exists(pyw) else sys.executable
            cmd = f'"{pyw}" "{os.path.abspath(__file__)}"'
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE) as k:
                if enabled:
                    winreg.SetValueEx(k, STARTUP_NAME, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(k, STARTUP_NAME)
                    except FileNotFoundError:
                        pass
            messagebox.showinfo(self.t("app_title"),
                                self.t("startup_enabled" if enabled else "startup_disabled"))
        except OSError as e:
            messagebox.showerror(self.t("error"), str(e))

    # ---------- النوافذ ----------
    def show_warning(self, parent, title, message, on_cancel):
        win = ctk.CTkToplevel(parent)
        win.title(title)
        win.geometry("400x220")
        win.resizable(False, False)
        win.configure(fg_color=UI["bg"])
        win.after(150, win.grab_set)

        card = ctk.CTkFrame(win, corner_radius=16, fg_color=UI["card"],
                            border_width=1, border_color=UI["border"])
        card.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(card, text=title, font=self.font(15), text_color=UI["warn"]).pack(pady=(18, 6))
        ctk.CTkLabel(card, text=message, font=self.font(12, False), text_color=UI["text"],
                     justify="center").pack(padx=14, pady=4)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(pady=(14, 14))

        def cancel():
            on_cancel()
            win.destroy()

        ctk.CTkButton(btns, text=self.t("confirm_yes"), font=self.font(12), fg_color="#ef4444",
                      hover_color="#dc2626", text_color="#ffffff", width=120, height=34,
                      corner_radius=10, command=win.destroy).pack(side="left", padx=8)
        ctk.CTkButton(btns, text=self.t("confirm_no"), font=self.font(12), fg_color=UI["field_btn"],
                      hover_color=UI["field_hover"], text_color=UI["text"], width=120, height=34,
                      corner_radius=10, command=cancel).pack(side="right", padx=8)

    def detect_location(self):
        # يرجع (الموقع، المصدر). المصدر: "windows" (أدق) أو "ip" (تقريبي)
        lang = self.cfg["lang"]
        lat = lng = tz = None
        source = "ip"
        fallback = {}

        # 1) خدمة الموقع في ويندوز (Wi-Fi / GPS)
        try:
            ps = (
                "Add-Type -AssemblyName System.Device; "
                "$w = New-Object System.Device.Location.GeoCoordinateWatcher("
                "[System.Device.Location.GeoPositionAccuracy]::High); "
                "if ($w.TryStart($false, [TimeSpan]::FromSeconds(10))) { "
                "$t = 0; while ($w.Status -ne 'Ready' -and $t -lt 80) { Start-Sleep -Milliseconds 100; $t++ }; "
                "$c = $w.Position.Location; "
                "if (-not $c.IsUnknown) { $ci = [Globalization.CultureInfo]::InvariantCulture; "
                "Write-Output ($c.Latitude.ToString($ci) + ',' + $c.Longitude.ToString($ci)) } }"
            )
            out = subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()
            la, lo = out.split(",")
            lat, lng = float(la), float(lo)
            source = "windows"
        except Exception:
            lat = lng = None

        # 2) احتياطي: تقريبي من عنوان الإنترنت
        if lat is None:
            d = requests.get("https://ipwho.is/", timeout=10).json()
            if not d.get("success"):
                raise RuntimeError(d.get("message", "ip lookup failed"))
            lat, lng = float(d["latitude"]), float(d["longitude"])
            tz = (d.get("timezone") or {}).get("id")
            fallback = {"name": d.get("city") or "", "admin1": d.get("region") or "",
                        "country": d.get("country") or "", "country_code": d.get("country_code") or ""}

        # المنطقة الزمنية من الإحداثيات
        if not tz:
            tz = requests.get("https://api.open-meteo.com/v1/forecast", timeout=10,
                              params={"latitude": lat, "longitude": lng, "timezone": "auto",
                                      "current": "temperature_2m"}).json()["timezone"]

        # اسم المكان بلغة التطبيق (من الإحداثيات)
        info = dict(fallback)
        try:
            r = requests.get("https://nominatim.openstreetmap.org/reverse", timeout=10,
                             params={"lat": lat, "lon": lng, "format": "jsonv2", "zoom": 10,
                                     "accept-language": lang},
                             headers={"User-Agent": "AdhanApp/1.0 (desktop prayer times)"}).json()
            a = r.get("address", {})
            name = (a.get("city") or a.get("town") or a.get("village") or a.get("municipality")
                    or a.get("county") or r.get("name") or "")
            if name:
                info = {"name": name, "admin1": a.get("state") or a.get("province") or a.get("region") or "",
                        "country": a.get("country") or "", "country_code": (a.get("country_code") or "").upper()}
        except Exception as e:
            print("تعذر جلب اسم المكان:", e)

        if not info.get("country_code") or not tz:
            raise RuntimeError("country or timezone unknown")
        res = {"name": info.get("name") or info.get("admin1") or info.get("country", ""),
               "admin1": info.get("admin1", ""), "country": info.get("country", ""),
               "country_code": info["country_code"], "latitude": lat, "longitude": lng, "timezone": tz}
        return self.make_location(res, self.is_ar), source

    def open_location_search(self, parent, on_pick):
        win = ctk.CTkToplevel(parent)
        win.title(self.t("search_title"))
        win.geometry("440x580")
        win.resizable(False, False)
        win.configure(fg_color=UI["bg"])
        win.after(150, win.grab_set)

        ar = self.is_ar
        side = "right" if ar else "left"
        lang = self.cfg["lang"]
        token = [0]

        def close():
            win.destroy()
            try:
                parent.after(100, parent.grab_set)
            except Exception:
                pass

        win.protocol("WM_DELETE_WINDOW", close)

        ctk.CTkLabel(win, text=self.t("search_title"), font=self.font(19),
                     text_color=UI["text"]).pack(pady=(20, 2))
        ctk.CTkLabel(win, text=self.t("search_hint"), font=self.font(11, False),
                     text_color=UI["muted"]).pack()

        bar = ctk.CTkFrame(win, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=12)
        entry = ctk.CTkEntry(bar, placeholder_text=self.t("search_placeholder"), height=40, corner_radius=12,
                             font=self.font(12, False), justify="right" if ar else "left",
                             fg_color=UI["card"], border_color=UI["border"], text_color=UI["text"])
        btn = ctk.CTkButton(bar, text=self.t("search_btn"), width=90, height=40, corner_radius=12,
                            font=self.font(12), fg_color=UI["accent"], hover_color=UI["accent_hover"],
                            text_color=UI["on_accent"], command=lambda: search())
        entry.pack(side=side, fill="x", expand=True)
        btn.pack(side=side, padx=(8, 0) if ar else (0, 8))

        status = ctk.CTkLabel(win, text="", font=self.font(11, False), text_color=UI["muted"])
        status.pack()
        results = ctk.CTkScrollableFrame(win, fg_color="transparent",
                                         scrollbar_button_color=UI["field_btn"],
                                         scrollbar_button_hover_color=UI["field_hover"])
        results.pack(fill="both", expand=True, padx=12, pady=(4, 14))
        entry.bind("<Return>", lambda e: search())
        entry.after(250, entry.focus)

        def choose(loc):
            on_pick(loc)
            close()

        def render(box):
            if box["err"]:
                status.configure(text=self.t("net_error"))
                return
            found = [r for r in box["data"] if r.get("timezone")]
            if not found:
                status.configure(text=self.t("no_results"))
                return
            status.configure(text="")
            for r in found:
                loc = self.make_location(r, ar)
                pre = RTL if ar else ""
                text = pre + loc["name"] + (("\n" + pre + loc["detail"]) if loc["detail"] else "")
                ctk.CTkButton(results, text=text, anchor="e" if ar else "w", height=54, corner_radius=12,
                              font=self.font(12, False), fg_color=UI["card"], hover_color=UI["field_btn"],
                              text_color=UI["text"], border_width=1, border_color=UI["border"],
                              command=lambda l=loc: choose(l)).pack(fill="x", pady=3, padx=4)

        def search():
            q = entry.get().strip()
            if len(q) < 2:
                return
            token[0] += 1
            my = token[0]
            status.configure(text=self.t("searching"))
            for w in results.winfo_children():
                w.destroy()
            box = {"done": False, "data": None, "err": False}

            def work():
                try:
                    r = requests.get(GEO_URL, params={"name": q, "count": 15, "language": lang,
                                                      "format": "json"}, timeout=10)
                    r.raise_for_status()
                    box["data"] = r.json().get("results") or []
                except Exception as e:
                    print("خطأ في البحث عن الموقع:", e)
                    box["err"] = True
                box["done"] = True

            threading.Thread(target=work, daemon=True).start()

            def poll():
                if not win.winfo_exists() or token[0] != my:
                    return
                if box["done"]:
                    render(box)
                else:
                    win.after(100, poll)

            poll()

    def open_settings(self):
        if self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.focus()
            return

        win = self.settings_win = ctk.CTkToplevel(self.root)
        win.title(self.t("settings_title"))
        win.geometry("460x760")
        win.resizable(False, False)
        win.configure(fg_color=UI["bg"])
        win.after(150, win.grab_set)

        ar = self.is_ar
        anchor = "e" if ar else "w"
        side_start, side_end = ("right", "left") if ar else ("left", "right")

        def close_window():
            ctk.set_appearance_mode(self.cfg["theme"])  # إلغاء معاينة المظهر غير المحفوظ
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", close_window)

        # ── الرأس ──
        head = ctk.CTkFrame(win, fg_color="transparent")
        head.pack(fill="x", padx=24, pady=(22, 8))
        ctk.CTkLabel(head, text="⚙", width=46, height=46, corner_radius=14, font=self.font(22),
                     fg_color=UI["accent"], text_color=UI["on_accent"]).pack(side=side_start)
        titles = ctk.CTkFrame(head, fg_color="transparent")
        titles.pack(side=side_start, padx=12)
        ctk.CTkLabel(titles, text=self.t("settings_title").replace("⚙ ", ""), font=self.font(21),
                     text_color=UI["text"]).pack(anchor=anchor)
        ctk.CTkLabel(titles, text=f"{self.t('app_title')}  •  v{APP_VERSION}", font=self.font(11, False),
                     text_color=UI["muted"]).pack(anchor=anchor)

        # ── شريط الأزرار السفلي (ثابت) ──
        bar = ctk.CTkFrame(win, fg_color="transparent")
        bar.pack(side="bottom", fill="x", padx=24, pady=(6, 18))
        save_btn = ctk.CTkButton(bar, text=self.t("save_btn"), font=self.font(14), height=44,
                                 corner_radius=14, fg_color=UI["accent"], hover_color=UI["accent_hover"],
                                 text_color=UI["on_accent"], command=lambda: save_and_close())
        cancel_btn = ctk.CTkButton(bar, text=self.t("confirm_no"), font=self.font(13), height=44, width=110,
                                   corner_radius=14, fg_color=UI["field_btn"], hover_color=UI["field_hover"],
                                   text_color=UI["text"], command=close_window)
        save_btn.pack(side=side_start, fill="x", expand=True)
        cancel_btn.pack(side=side_start, padx=(0, 10) if not ar else (10, 0))

        body = ctk.CTkScrollableFrame(win, fg_color="transparent",
                                      scrollbar_button_color=UI["field_btn"],
                                      scrollbar_button_hover_color=UI["field_hover"])
        body.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        def section(title_key):
            ctk.CTkLabel(body, text=self.t(title_key), font=self.font(12),
                         text_color=UI["accent"]).pack(anchor=anchor, padx=20, pady=(14, 5))
            card = ctk.CTkFrame(body, corner_radius=16, fg_color=UI["card"],
                                border_width=1, border_color=UI["border"])
            card.pack(fill="x", padx=10)
            return card

        def row(card, text, make_widget):
            """صف واحد: الاسم في جهة البداية والعنصر في الجهة المقابلة (يراعي اتجاه اللغة)."""
            if card.winfo_children():
                ctk.CTkFrame(card, height=1, fg_color=UI["border"]).pack(fill="x", padx=16)
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=10)
            lbl = ctk.CTkLabel(r, text=text, font=self.font(12), text_color=UI["text"])
            widget = make_widget(r)
            lbl.pack(side=side_start)
            widget.pack(side=side_end)
            return widget

        def menu(values, current, width=190):
            def make(parent):
                m = ctk.CTkOptionMenu(
                    parent, values=values, width=width, height=34, corner_radius=10,
                    dynamic_resizing=False, font=self.font(12, False), dropdown_font=self.font(12, False),
                    fg_color=UI["field"], button_color=UI["field_btn"], button_hover_color=UI["field_hover"],
                    text_color=UI["text"], dropdown_fg_color=UI["card"],
                    dropdown_hover_color=UI["field_btn"], dropdown_text_color=UI["text"])
                m.set(current)
                return m
            return make

        def switch(var):
            return lambda parent: ctk.CTkSwitch(
                parent, text="", variable=var, width=48, fg_color=UI["track"],
                progress_color=UI["accent"], button_color=("#ffffff", "#e2e8f0"),
                button_hover_color=("#f8fafc", "#ffffff"))

        # ── عام ──
        general = section("general_section")
        lang_combo = row(general, self.t("lang_option"),
                         menu(["العربية", "English"], "العربية" if ar else "English"))

        theme_map = {self.t("dark_theme"): "Dark", self.t("light_theme"): "Light"}
        theme_label = {v: k for k, v in theme_map.items()}
        theme_combo = row(general, self.t("theme_option"), menu(list(theme_map), theme_label[self.cfg["theme"]]))
        theme_combo.configure(command=lambda c: ctk.set_appearance_mode(theme_map.get(c, "Dark")))  # معاينة فورية

        startup_var = ctk.BooleanVar(value=self.is_in_startup())
        row(general, self.t("startup_option"), switch(startup_var))

        # ── الموقع وطريقة الحساب ──
        state = {"loc": dict(self.cfg["location"])}

        def loc_text(loc):
            t = loc["label"].get(self.cfg["lang"]) or next(iter(loc["label"].values()), "")
            return (RTL + t) if ar else t

        def pick_location():
            def on_pick(loc):
                state["loc"] = loc
                loc_btn.configure(text=loc_text(loc))
            self.open_location_search(win, on_pick)

        calc = section("location_section")
        loc_btn = row(calc, self.t("location_option"), lambda parent: ctk.CTkButton(
            parent, text=loc_text(state["loc"]), width=240, height=34, corner_radius=10,
            font=self.font(12, False), fg_color=UI["field"], hover_color=UI["field_hover"],
            text_color=UI["text"], command=pick_location))

        def finish_detect(box):
            auto_btn.configure(state="normal", text=self.t("auto_detect_btn"))
            if box["err"]:
                auto_status.configure(text=self.t("detect_failed"), text_color=UI["warn"], height=40)
                return
            loc, source = box["res"]
            state["loc"] = loc
            loc_btn.configure(text=loc_text(loc))
            auto_status.configure(text=self.t("detect_windows" if source == "windows" else "detect_ip"),
                                  text_color=UI["muted"], height=56)

        def auto_detect():
            auto_btn.configure(state="disabled", text=self.t("detecting"))
            auto_status.configure(text="", height=1)
            box = {"done": False, "res": None, "err": False}

            def work():
                try:
                    box["res"] = self.detect_location()
                except Exception as e:
                    print("تعذر تحديد الموقع:", e)
                    box["err"] = True
                box["done"] = True

            threading.Thread(target=work, daemon=True).start()

            def poll():
                if not win.winfo_exists():
                    return
                if box["done"]:
                    finish_detect(box)
                else:
                    win.after(150, poll)

            poll()

        auto_btn = row(calc, self.t("auto_detect_option"), lambda parent: ctk.CTkButton(
            parent, text=self.t("auto_detect_btn"), width=240, height=34, corner_radius=10,
            font=self.font(12), fg_color=UI["accent"], hover_color=UI["accent_hover"],
            text_color=UI["on_accent"], command=auto_detect))
        auto_status = ctk.CTkLabel(calc, text="", height=1, font=self.font(11, False), text_color=UI["muted"],
                                   wraplength=370, justify="right" if ar else "left")
        auto_status.pack(anchor=anchor, padx=18, pady=(0, 6))

        mprefix = RTL if ar else ""
        method_names = {mid: mprefix + names[0 if ar else 1] for mid, names in METHODS.items()}
        auto_label = self.t("method_auto")
        label_to_method = {auto_label: "auto"}
        label_to_method.update({v: k for k, v in method_names.items()})
        cur_method = auto_label if self.cfg["method"] == "auto" else method_names.get(self.cfg["method"], auto_label)
        method_combo = row(calc, self.t("method_option"), menu(list(label_to_method), cur_method, width=250))

        school_map = {self.t("school_standard"): 0, self.t("school_hanafi"): 1}
        school_label = {v: k for k, v in school_map.items()}
        school_combo = row(calc, self.t("school_option"),
                           menu(list(school_map), school_label.get(self.cfg["school"], self.t("school_standard")),
                                width=250))

        # ── الوقت ──
        time_card = section("time_section")
        time_combo = row(time_card, self.t("time_format_option"),
                         menu([self.t("12h"), self.t("24h")],
                              self.t("24h") if self.cfg["use_24h"] else self.t("12h")))

        dst_map = {self.t("dst_auto"): "Auto", self.t("dst_summer"): "Summer", self.t("dst_winter"): "Winter"}
        dst_label = {v: k for k, v in dst_map.items()}
        dst_combo = row(time_card, self.t("dst_option"), menu(list(dst_map), dst_label[self.cfg["dst_mode"]]))
        dst_combo.configure(command=lambda choice: choice != self.t("dst_auto") and self.show_warning(
            win, self.t("warning_title"), self.t("dst_warn_msg"),
            on_cancel=lambda: dst_combo.set(self.t("dst_auto"))))

        # ── تعديل المواقيت بالدقائق ──
        offs = section("offsets_section")
        offset_values = [f"{v:+d}" if v else "0" for v in range(-15, 16)]
        offset_combos = {}
        for p in PRAYERS:
            v = int(self.cfg["offsets"].get(p, 0))
            offset_combos[p] = row(offs, self.t(p), menu(offset_values, f"{v:+d}" if v else "0", width=110))

        # ── الأذان ──
        adhan = section("adhan_section")
        takbeer_var = ctk.BooleanVar(value=self.cfg["takbeer_only"])
        row(adhan, self.t("takbeer_only_option"), switch(takbeer_var))

        ctk.CTkLabel(adhan, text=self.t("muezzin_settings_section"), font=self.font(11, False),
                     text_color=UI["muted"]).pack(anchor=anchor, padx=18, pady=(10, 0))

        prefix = RTL if ar else ""
        label_to_key = {self.t("random"): "random"}
        label_to_key.update({prefix + info[self.cfg["lang"]]: f for f, info in MUEZZINS.items()})
        key_to_label = {v: k for k, v in label_to_key.items()}

        muezzin_combos = {}
        for p in PRAYERS:
            current = key_to_label.get(self.cfg["muezzins"].get(p, "random"), self.t("random"))
            muezzin_combos[p] = row(adhan, self.t(p), menu(list(label_to_key), current, width=250))

        def save_and_close():
            was_startup = self.is_in_startup()
            self.cfg["lang"] = "ar" if lang_combo.get() == "العربية" else "en"
            self.cfg["theme"] = theme_map.get(theme_combo.get(), "Dark")
            self.cfg["dst_mode"] = dst_map.get(dst_combo.get(), "Auto")
            self.cfg["use_24h"] = time_combo.get() == self.t("24h")
            self.cfg["takbeer_only"] = takbeer_var.get()
            self.cfg["location"] = state["loc"]
            self.cfg["method"] = label_to_method.get(method_combo.get(), "auto")
            self.cfg["school"] = school_map.get(school_combo.get(), 0)
            for p, cb in offset_combos.items():
                self.cfg["offsets"][p] = int(cb.get())
            for p, cb in muezzin_combos.items():
                self.cfg["muezzins"][p] = label_to_key.get(cb.get(), "random")

            ctk.set_appearance_mode(self.cfg["theme"])
            save_config(self.cfg)
            if startup_var.get() != was_startup:
                self.set_startup(startup_var.get())
            self.update_ui_language()
            self.update()
            win.destroy()

    def open_update_page(self):
        webbrowser.open(self.updater.url or f"https://github.com/{GITHUB_REPO}/releases/latest")

    def on_close(self):
        self.stop_audio()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AdhanApp().run()
