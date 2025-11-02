import unittest
import os
from finance_tracker import ExpenseManager  # Import from the combined file

class TestExpenseManager(unittest.TestCase):
    def setUp(self):
        self.manager = ExpenseManager('test_expenses.json')
        self.manager.expenses = []  # Reset for tests

    def test_add_expense(self):
        self.manager.add_expense('2023-01-01', 50.0, 'Test', 'Food')
        self.assertEqual(len(self.manager.expenses), 1)
        self.assertEqual(self.manager.expenses[0]['amount'], 50.0)

    def test_update_expense(self):
        self.manager.add_expense('2023-01-01', 50.0, 'Test', 'Food')
        self.manager.update_expense(1, amount=60.0)
        self.assertEqual(self.manager.expenses[0]['amount'], 60.0)

    def test_delete_expense(self):
        self.manager.add_expense('2023-01-01', 50.0, 'Test', 'Food')
        self.manager.delete_expense(1)
        self.assertEqual(len(self.manager.expenses), 0)

    def test_filter_expenses(self):
        self.manager.add_expense('2023-01-01', 50.0, 'Test1', 'Food')
        self.manager.add_expense('2023-02-01', 30.0, 'Test2', 'Transport')
        filtered = self.manager.filter_expenses(category='Food')
        self.assertEqual(len(filtered), 1)

    def test_calculate_total(self):
        self.manager.add_expense('2023-01-01', 50.0, 'Test', 'Food')
        self.assertEqual(self.manager.calculate_total(), 50.0)

    def tearDown(self):
        if os.path.exists('test_expenses.json'):
            os.remove('test_expenses.json')