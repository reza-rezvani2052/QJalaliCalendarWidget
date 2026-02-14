import sys
from datetime import timedelta
import jdatetime
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QComboBox, QLabel, QPushButton, QSpinBox,
    QGridLayout, QHBoxLayout, QVBoxLayout
    )


class DayButton(QPushButton):
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.doubleClicked.emit()


class QJalaliCalendarWidget(QWidget):
    # Backward-compatible signal name
    dateSelected = Signal(jdatetime.date)

    # Close..
    confirmed = Signal(object)
    # confirmed = Signal(jdatetime.date)

    # Qt-like signals
    selectionChanged = Signal()
    activated = Signal(jdatetime.date)
    currentPageChanged = Signal(int, int)

    DEFAULT_MONTH_NAMES_FA = [
        "فروردین", "اردیبهشت", "خرداد",  # بهار
        "تیر", "مرداد", "شهریور",  # تابستان
        "مهر", "آبان", "آذر",  # پاییز
        "دی", "بهمن", "اسفند"  # زمستان
        ]
    DEFAULT_WEEKDAY_NAMES_FA = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
    DEFAULT_WEEKDAY_FULL_NAMES_FA = [
        "شنبه", "یکشنبه", "دوشنبه", "سه شنبه", "چهارشنبه", "پنجشنبه", "جمعه"
        ]
    DIGITS_FA = "۰۱۲۳۴۵۶۷۸۹"

    def __init__(self, parent=None, force_rtl=True):
        super().__init__(parent)
        if force_rtl:
            self.setLayoutDirection(Qt.RightToLeft)

        self.setWindowFlags(Qt.Popup)
        self.setFocusPolicy(Qt.StrongFocus)

        self._month_names = list(self.DEFAULT_MONTH_NAMES_FA)
        self._weekday_names = list(self.DEFAULT_WEEKDAY_NAMES_FA)
        self._weekday_full_names = list(self.DEFAULT_WEEKDAY_FULL_NAMES_FA)
        self._digit_mode = "fa"  # fa | en

        # Theme colors (runtime-configurable)
        self._selected_bg = "#3875d6"
        self._selected_fg = "#ffffff"
        self._today_bg = "#eef8e6"
        self._today_border = "#6a9e41"
        self._outside_fg = "#9b9b9b"
        self._friday_fg = "#c83c3c"

        self._min_date = None
        self._max_date = None

        today = jdatetime.date.today()
        self._selected_date = today
        self.current_year = today.year
        self.current_month = today.month
        self._cell_dates = [None] * 42

        self._build_ui()
        self.populate_calendar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)

        self.prev_btn = QPushButton("◀")
        self.prev_btn.setToolTip("ماه قبل")
        self.prev_btn.setObjectName("navButton")
        self.prev_btn.setFixedSize(24, 24)

        self.next_btn = QPushButton("▶")
        self.next_btn.setToolTip("ماه بعد")
        self.next_btn.setObjectName("navButton")
        self.next_btn.setFixedSize(24, 24)

        self.month_combo = QComboBox()
        self.month_combo.setObjectName("monthCombo")
        self.month_combo.addItems(self._month_names)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.setFixedWidth(120)

        self.year_spin = QSpinBox()
        self.year_spin.setObjectName("yearSpin")
        self.year_spin.setRange(1, 3000)
        self.year_spin.setValue(self.current_year)
        self.year_spin.setFixedWidth(72)

        self.today_btn = QPushButton("امروز")
        self.today_btn.setObjectName("todayButton")
        self.today_btn.setFixedHeight(24)

        nav_layout.addWidget(self.month_combo)
        nav_layout.addWidget(self.year_spin)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.today_btn)
        layout.addLayout(nav_layout)

        week_layout = QHBoxLayout()
        week_layout.setSpacing(1)
        self.weekday_labels = []
        for i, wd in enumerate(self._weekday_names):
            lbl = QLabel(wd)
            lbl.setObjectName("weekHeader")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(36, 24)
            if i == 6:
                lbl.setStyleSheet(f"color: {self._friday_fg}; font-weight: 600;")
            week_layout.addWidget(lbl)
            self.weekday_labels.append(lbl)
        layout.addLayout(week_layout)

        self.grid = QGridLayout()
        self.grid.setSpacing(1)
        self.day_buttons = []
        for row in range(6):
            for col in range(7):
                idx = row * 7 + col
                btn = DayButton("")
                btn.setObjectName("dayButton")
                btn.setFixedSize(36, 28)
                btn.setCheckable(True)
                btn.setProperty("cellIndex", idx)
                btn.clicked.connect(self._on_day_button_clicked)
                btn.doubleClicked.connect(self._on_day_button_double_clicked)
                self.grid.addWidget(btn, row, col)
                self.day_buttons.append(btn)
        layout.addLayout(self.grid)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(6)
        self.selected_label = QLabel("")
        self.selected_label.setObjectName("selectedDateLabel")
        self.selected_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.btn_ok = QPushButton("تایید")
        self.btn_ok.setObjectName("btn_ok")
        self.btn_ok.setFixedHeight(24)
        self.btn_ok.clicked.connect(self.confirm_selection)
        bottom_layout.addWidget(self.selected_label, 1)
        bottom_layout.addWidget(self.btn_ok)
        layout.addLayout(bottom_layout)

        self.prev_btn.clicked.connect(self.prev_month)
        self.next_btn.clicked.connect(self.next_month)
        self.today_btn.clicked.connect(self.go_today)
        self.month_combo.currentIndexChanged.connect(self.change_month)
        self.year_spin.valueChanged.connect(self.change_year)

        self._apply_base_style()

    def _apply_base_style(self):
        self.setStyleSheet(
                """
                QJalaliCalendarWidget {
                    background: #f6f7f8;
                    border: 1px solid #c7c7c7;
                    border-radius: 4px;
                }
                QPushButton#navButton,
                QPushButton#todayButton,
                QPushButton#btn_ok {
                    background: #f1f1f1;
                    border: 1px solid #bcbcbc;
                    border-radius: 3px;
                    color: #222222;
                    padding: 0 6px;
                }
                QPushButton#navButton:hover,
                QPushButton#todayButton:hover,
                QPushButton#btn_ok:hover {
                    background: #ffffff;
                    border-color: #9f9f9f;
                }
                QLabel#selectedDateLabel {
                    background: #ffffff;
                    border: 1px solid #cfcfcf;
                    border-radius: 3px;
                    padding: 2px 6px;
                    color: #222222;
                }
                QComboBox#monthCombo,
                QSpinBox#yearSpin {
                    background: #ffffff;
                    border: 1px solid #bcbcbc;
                    border-radius: 3px;
                    color: #222222;
                    padding: 1px 6px;
                }
                QLabel#weekHeader {
                    background: #ececec;
                    border: 1px solid #cfcfcf;
                    color: #444444;
                    font-weight: 600;
                }
                QPushButton#dayButton {
                    background: #ffffff;
                    border: 1px solid #d2d2d2;
                    border-radius: 2px;
                    color: #222222;
                }
                QPushButton#dayButton:hover:enabled {
                    background: #eaf2ff;
                    border-color: #8ab5ff;
                }
                QPushButton#dayButton:checked {
                    font-weight: 600;
                }
                QPushButton#dayButton:disabled {
                    background: #f7f7f7;
                    color: #9b9b9b;
                }
                """
                )

    # Public API
    def selectedDate(self):
        return self._selected_date

    def setSelectedDate(self, date):
        if not isinstance(date, jdatetime.date):
            raise TypeError("date must be jdatetime.date")
        if not self._is_in_range(date):
            raise ValueError("date is outside allowed range")

        old_page = (self.current_year, self.current_month)
        old_selected = self._selected_date

        self._selected_date = date
        self.current_year = date.year
        self.current_month = date.month

        if old_page != (self.current_year, self.current_month):
            self.currentPageChanged.emit(self.current_year, self.current_month)
        if old_selected != self._selected_date:
            self.selectionChanged.emit()
        self.populate_calendar()

    def minimumDate(self):
        return self._min_date

    def maximumDate(self):
        return self._max_date

    def setMinimumDate(self, date):
        if date is not None and not isinstance(date, jdatetime.date):
            raise TypeError("minimum date must be jdatetime.date or None")
        self._min_date = date
        self._normalize_range()
        self._clamp_selected_to_range()
        self.populate_calendar()

    def setMaximumDate(self, date):
        if date is not None and not isinstance(date, jdatetime.date):
            raise TypeError("maximum date must be jdatetime.date or None")
        self._max_date = date
        self._normalize_range()
        self._clamp_selected_to_range()
        self.populate_calendar()

    def setDateRange(self, minimum, maximum):
        if minimum is not None and not isinstance(minimum, jdatetime.date):
            raise TypeError("minimum date must be jdatetime.date or None")
        if maximum is not None and not isinstance(maximum, jdatetime.date):
            raise TypeError("maximum date must be jdatetime.date or None")
        self._min_date = minimum
        self._max_date = maximum
        self._normalize_range()
        self._clamp_selected_to_range()
        self.populate_calendar()

    def monthShown(self):
        return self.current_month

    def yearShown(self):
        return self.current_year

    def showToday(self):
        self.go_today()

    def showSelectedDate(self):
        if self._selected_date is None:
            return
        old_page = (self.current_year, self.current_month)
        self.current_year = self._selected_date.year
        self.current_month = self._selected_date.month
        if old_page != (self.current_year, self.current_month):
            self.currentPageChanged.emit(self.current_year, self.current_month)
        self.populate_calendar()

    def setMonthNames(self, names):
        if len(names) != 12:
            raise ValueError("month names must have exactly 12 items")
        self._month_names = list(names)
        self.month_combo.blockSignals(True)
        self.month_combo.clear()
        self.month_combo.addItems(self._month_names)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.blockSignals(False)

    def setWeekdayNames(self, names):
        if len(names) != 7:
            raise ValueError("weekday names must have exactly 7 items")
        self._weekday_names = list(names)
        for idx, name in enumerate(self._weekday_names):
            self.weekday_labels[idx].setText(name)
            if idx == 6:
                self.weekday_labels[idx].setStyleSheet(
                        f"color: {self._friday_fg}; font-weight: 600;"
                        )
            else:
                self.weekday_labels[idx].setStyleSheet("")

    def setDigitMode(self, mode):
        mode = str(mode).lower()
        if mode not in {"fa", "en"}:
            raise ValueError("digit mode must be 'fa' or 'en'")
        self._digit_mode = mode
        self.populate_calendar()

    def digitMode(self):
        return self._digit_mode

    def setThemeColors(
            self,
            selected_bg=None,
            selected_fg=None,
            today_bg=None,
            today_border=None,
            outside_fg=None,
            friday_fg=None,
            ):
        if selected_bg is not None:
            self._selected_bg = selected_bg
        if selected_fg is not None:
            self._selected_fg = selected_fg
        if today_bg is not None:
            self._today_bg = today_bg
        if today_border is not None:
            self._today_border = today_border
        if outside_fg is not None:
            self._outside_fg = outside_fg
        if friday_fg is not None:
            self._friday_fg = friday_fg
            self.setWeekdayNames(self._weekday_names)
        self.populate_calendar()

    # Navigation
    def prev_month(self):
        y, m = self.get_prev_month(self.current_year, self.current_month)
        self._set_page(y, m)

    def next_month(self):
        y, m = self.get_next_month(self.current_year, self.current_month)
        self._set_page(y, m)

    def go_today(self):
        today = jdatetime.date.today()
        if not self._is_in_range(today):
            return
        self.setSelectedDate(today)

    def change_month(self, *_):
        new_month = self.month_combo.currentIndex() + 1
        if new_month == self.current_month:
            return
        self._set_page(self.current_year, new_month)

    def change_year(self, *_):
        new_year = self.year_spin.value()
        if new_year == self.current_year:
            return
        self._set_page(new_year, self.current_month)

    def _set_page(self, year, month):
        old_page = (self.current_year, self.current_month)

        # keep same day when possible
        day = min(self._selected_date.day, self.get_days_in_month(year, month))
        candidate = jdatetime.date(year, month, day)
        candidate = self._clamp_to_range(candidate)

        self.current_year = year
        self.current_month = month
        self._selected_date = candidate

        if old_page != (self.current_year, self.current_month):
            self.currentPageChanged.emit(self.current_year, self.current_month)
        self.selectionChanged.emit()
        self.populate_calendar()

    # Rendering
    def populate_calendar(self):
        today = jdatetime.date.today()

        self.month_combo.blockSignals(True)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.blockSignals(False)

        self.year_spin.blockSignals(True)
        self.year_spin.setValue(self.current_year)
        self.year_spin.blockSignals(False)

        days_in_month = self.get_days_in_month(self.current_year, self.current_month)
        first_day = jdatetime.date(self.current_year, self.current_month, 1)
        greg_weekday = first_day.togregorian().weekday()
        mapping = {5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6}
        start_weekday = mapping[greg_weekday]

        prev_year, prev_month = self.get_prev_month(self.current_year, self.current_month)
        prev_days = self.get_days_in_month(prev_year, prev_month)

        for i, btn in enumerate(self.day_buttons):
            if i < start_weekday:
                day = prev_days - start_weekday + i + 1
                y, m = prev_year, prev_month
                is_current_month = False
            elif i < start_weekday + days_in_month:
                day = i - start_weekday + 1
                y, m = self.current_year, self.current_month
                is_current_month = True
            else:
                day = i - (start_weekday + days_in_month) + 1
                y, m = self.get_next_month(self.current_year, self.current_month)
                is_current_month = False

            cell_date = jdatetime.date(y, m, day)
            self._cell_dates[i] = cell_date

            in_range = self._is_in_range(cell_date)
            enabled = is_current_month and in_range
            selected = cell_date == self._selected_date
            is_today = cell_date == today
            is_friday = i % 7 == 6

            btn.setText(self._format_digits(day))
            btn.setEnabled(enabled)
            btn.setChecked(enabled and selected)
            btn.setVisible(True)
            btn.setStyleSheet(
                    self._build_day_style(
                            is_current_month=is_current_month,
                            is_today=is_today,
                            is_selected=(enabled and selected),
                            is_friday=is_friday,
                            )
                    )
        self._update_selected_label()

    def _build_day_style(self, is_current_month, is_today, is_selected, is_friday):
        style_parts = []
        if is_friday and is_current_month:
            style_parts.append(f"color: {self._friday_fg};")
        if not is_current_month:
            style_parts.append(f"color: {self._outside_fg};")
        if is_today:
            style_parts.append(
                    f"background-color: {self._today_bg}; border: 1px solid {self._today_border};"
                    )
        if is_selected:
            style_parts.append(
                    f"background-color: {self._selected_bg};"
                    f" border-color: {self._selected_bg}; color: {self._selected_fg};"
                    " font-weight: 600;"
                    )
        return " ".join(style_parts)

    # Interaction
    def _on_day_button_clicked(self):
        sender = self.sender()
        idx = sender.property("cellIndex")
        if idx is None:
            return
        cell_date = self._cell_dates[idx]
        if cell_date is None or not self._is_in_range(cell_date):
            return
        if cell_date.month != self.current_month or cell_date.year != self.current_year:
            return
        if not sender.isEnabled():
            return

        changed = cell_date != self._selected_date
        self._selected_date = cell_date
        if changed:
            self.selectionChanged.emit()
            self.populate_calendar()

        self.activated.emit(cell_date)
        self.dateSelected.emit(cell_date)

    def _on_day_button_double_clicked(self):
        sender = self.sender()
        if sender is None or not sender.isEnabled():
            return
        self.confirm_selection()

    def confirm_selection(self):
        if self._selected_date is None:
            return
        # print("Selected:", self._selected_date)
        window = self.window()
        if window is not None:
            # این رفتار برای ویجت عمومی درست نیست و خطرناک است
            # پکیج نباید پنجره کاربر رو ببنده
            # window.close()
            # ولی چون من در سازنده این را نوشتم ایرادی نداره :
            #   self.setWindowFlags(Qt.Popup)
            # ...
            self.confirmed.emit(self._selected_date)
            # print("selected_date =", self._selected_date) # Example: 1404-11-24
            # self._selected_date.strftime("%Y/%m/%d")  # تغییر فرمت در سمت سرویس گیرنده کد
            # ...
            # window.close()
            self.close()

    def keyPressEvent(self, event: QKeyEvent):
        if self._selected_date is None:
            return super().keyPressEvent(event)

        key = event.key()
        mods = event.modifiers()
        date = self._selected_date
        new_date = None

        if key == Qt.Key_Left:
            new_date = self._add_days(date, -1)
        elif key == Qt.Key_Right:
            new_date = self._add_days(date, 1)
        elif key == Qt.Key_Up:
            new_date = self._add_days(date, -7)
        elif key == Qt.Key_Down:
            new_date = self._add_days(date, 7)
        elif key == Qt.Key_PageUp:
            delta = -12 if mods & Qt.ShiftModifier else -1
            new_date = self._add_months(date, delta)
        elif key == Qt.Key_PageDown:
            delta = 12 if mods & Qt.ShiftModifier else 1
            new_date = self._add_months(date, delta)
        elif key == Qt.Key_Home:
            new_date = jdatetime.date(date.year, date.month, 1)
        elif key == Qt.Key_End:
            last_day = self.get_days_in_month(date.year, date.month)
            new_date = jdatetime.date(date.year, date.month, last_day)
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            self.confirm_selection()
            return
        else:
            return super().keyPressEvent(event)

        if new_date is not None:
            new_date = self._clamp_to_range(new_date)
            self.setSelectedDate(new_date)

    # Helpers
    def _normalize_range(self):
        if self._min_date is not None and self._max_date is not None:
            if self._min_date > self._max_date:
                self._min_date, self._max_date = self._max_date, self._min_date

    def _clamp_selected_to_range(self):
        if self._selected_date is None:
            return
        self._selected_date = self._clamp_to_range(self._selected_date)
        self.current_year = self._selected_date.year
        self.current_month = self._selected_date.month

    def _is_in_range(self, date):
        if self._min_date is not None and date < self._min_date:
            return False
        if self._max_date is not None and date > self._max_date:
            return False
        return True

    def _clamp_to_range(self, date):
        if self._min_date is not None and date < self._min_date:
            return self._min_date
        if self._max_date is not None and date > self._max_date:
            return self._max_date
        return date

    def _format_digits(self, value):
        text = str(value)
        if self._digit_mode == "en":
            return text
        return "".join(self.DIGITS_FA[int(ch)] if ch.isdigit() else ch for ch in text)

    def _update_selected_label(self):
        if self._selected_date is None:
            self.selected_label.setText("")
            return
        self.selected_label.setText(self._format_display_date(self._selected_date))

    def _format_display_date(self, date):
        greg_weekday = date.togregorian().weekday()
        mapping = {5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6}
        weekday_name = self._weekday_full_names[mapping[greg_weekday]]
        month_name = self._month_names[date.month - 1]
        day_text = self._format_digits(date.day)
        year_text = self._format_digits(date.year)
        return f"{weekday_name} {day_text} {month_name} {year_text}"

    def _add_days(self, date, days):
        g = date.togregorian() + timedelta(days=days)
        return jdatetime.date.fromgregorian(date=g)

    def _add_months(self, date, months):
        total = (date.year * 12 + (date.month - 1)) + months
        year = total // 12
        month = (total % 12) + 1
        day = min(date.day, self.get_days_in_month(year, month))
        return jdatetime.date(year, month, day)

    @staticmethod
    def get_prev_month(year, month):
        if month == 1:
            return year - 1, 12
        return year, month - 1

    @staticmethod
    def get_next_month(year, month):
        if month == 12:
            return year + 1, 1
        return year, month + 1

    @staticmethod
    def get_days_in_month(year, month):
        if month <= 6:
            return 31
        if month <= 11:
            return 30
        try:
            jdatetime.date(year, 12, 30)
            return 30
        except ValueError:
            return 29
