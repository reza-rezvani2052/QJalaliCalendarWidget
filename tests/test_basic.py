import os
import sys
import unittest
from pathlib import Path

import jdatetime
from PySide6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qjalalicalendarwidget import QJalaliCalendarWidget


class TestQJalaliCalendarWidgetBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = QJalaliCalendarWidget()

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()

    def test_widget_initializes_with_selected_date(self):
        selected = self.widget.selectedDate()
        self.assertIsInstance(selected, jdatetime.date)
        self.assertEqual(self.widget.monthShown(), selected.month)
        self.assertEqual(self.widget.yearShown(), selected.year)

    def test_set_selected_date_updates_page(self):
        target = jdatetime.date(1404, 7, 10)
        self.widget.setSelectedDate(target)
        self.assertEqual(self.widget.selectedDate(), target)
        self.assertEqual(self.widget.monthShown(), 7)
        self.assertEqual(self.widget.yearShown(), 1404)

    def test_set_selected_date_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.widget.setSelectedDate("1404-01-01")

    def test_set_selected_date_out_of_range_raises(self):
        self.widget.setDateRange(jdatetime.date(1404, 1, 1), jdatetime.date(1404, 1, 10))
        with self.assertRaises(ValueError):
            self.widget.setSelectedDate(jdatetime.date(1404, 1, 11))

    def test_set_date_range_normalizes_min_max(self):
        self.widget.setDateRange(jdatetime.date(1404, 1, 20), jdatetime.date(1404, 1, 10))
        self.assertEqual(self.widget.minimumDate(), jdatetime.date(1404, 1, 10))
        self.assertEqual(self.widget.maximumDate(), jdatetime.date(1404, 1, 20))

    def test_digit_mode_changes_day_button_text(self):
        self.widget.setDigitMode("en")
        self.assertEqual(self.widget._format_digits(123), "123")
        self.widget.setDigitMode("fa")
        self.assertEqual(self.widget._format_digits(123), "۱۲۳")

    def test_invalid_digit_mode_raises(self):
        with self.assertRaises(ValueError):
            self.widget.setDigitMode("xx")

    def test_static_month_helpers(self):
        self.assertEqual(QJalaliCalendarWidget.get_prev_month(1404, 1), (1403, 12))
        self.assertEqual(QJalaliCalendarWidget.get_next_month(1404, 12), (1405, 1))

    def test_days_in_month(self):
        self.assertEqual(QJalaliCalendarWidget.get_days_in_month(1404, 1), 31)
        self.assertEqual(QJalaliCalendarWidget.get_days_in_month(1404, 7), 30)
        self.assertIn(QJalaliCalendarWidget.get_days_in_month(1404, 12), (29, 30))
