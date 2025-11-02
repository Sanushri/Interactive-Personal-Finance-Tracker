
""" Please read the README.txt file and run the statements mentioned in that 
    in that file for proper functioning of the below code as it contains
Libraries outside of Python's built-in libraries like Streamlit, matplotlib , numpy and plotly   """

import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import json
import os
import numpy as np
from datetime import datetime

# Backend Class: ExpenseManager
class ExpenseManager:
    
    def __init__(self, data_file='expenses.json'):
        self.data_file = data_file
        self.expenses = self.load_expenses()  # Multi-dimensional list: list of dicts

    def load_expenses(self):
        """Load expenses from JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []

    def save_expenses(self):
        """Save expenses to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.expenses, f, indent=4)

    def add_expense(self, date, amount, description, category='General'):
        """Adding a new expense."""
        expense = {
            'id': len(self.expenses) + 1,
            'date': date,
            'amount': float(amount),
            'description': description,
            'category': category
        }
        self.expenses.append(expense)
        self.save_expenses()

    def update_expense(self, expense_id, date=None, amount=None, description=None, category=None):
        """Updating an existing expense."""
        for expense in self.expenses:  # Loop through expenses
            if expense['id'] == expense_id:
                if date: expense['date'] = date
                if amount: expense['amount'] = float(amount)
                if description: expense['description'] = description
                if category: expense['category'] = category
                self.save_expenses()
                return True
        return False

    def delete_expense(self, expense_id):
        """Deleting an expense."""
        self.expenses = [e for e in self.expenses if e['id'] != expense_id]  # Flow Control: List comprehension
        self.save_expenses()

    def filter_expenses(self, start_date=None, end_date=None, category=None):
        """Filtering expenses using Flow Control (loops and conditionals)."""
        filtered = []
        for expense in self.expenses:  # Loop through multi-dimensional list
            if start_date and expense['date'] < start_date: continue
            if end_date and expense['date'] > end_date: continue
            if category and expense['category'] != category: continue
            filtered.append(expense)
        return filtered

    def get_expenses_array(self):
        """Converting expenses to numpy array for analysis."""
        if not self.expenses:
            return np.array([])
        amounts = np.array([e['amount'] for e in self.expenses])
        return amounts

    def calculate_total(self, filtered_expenses=None):
        """Calculating total expenses."""
        expenses = filtered_expenses or self.expenses
        if not expenses:
            return 0.0
        amounts = np.array([e['amount'] for e in expenses])
        return np.sum(amounts)

    def get_budget_alert(self, budget):
        """Check if total expense exceeds budget using Numpy."""
        total = self.calculate_total()
        return total > budget, total

    def get_category_totals(self):
        """Aggregating totals by category."""
        categories = {}
        for expense in self.expenses:  
            cat = expense['category']
            categories[cat] = categories.get(cat, 0) + expense['amount']
        return categories


# Frontend: Streamlit App
def main():

    # Initializing manager
    manager = ExpenseManager()

    st.title("Personal Finance Tracker")

    # Sidebar for filters and budget
    st.sidebar.header("Filters & Budget")
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")
    category_filter = st.sidebar.selectbox("Category", ["All"] + list(set(e['category'] for e in manager.expenses)))
    budget = st.sidebar.number_input("Monthly Budget", min_value=0.0, value=1000.0)

    # Apply filters
    filtered_expenses = manager.filter_expenses(
        start_date=str(start_date) if start_date else None,
        end_date=str(end_date) if end_date else None,
        category=category_filter if category_filter != "All" else None
    )

    # Adding Expense Form
    st.header("Add Expense")
    with st.form("add_expense"):
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.0)
        description = st.text_input("Description")
        category = st.selectbox("Category", ["General", "Food", "Transport", "Entertainment","Bills"])
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            manager.add_expense(str(date), amount, description, category)
            st.success("Expense added!")
            st.cache_data.clear()
            st.rerun()

    # Displaying Expenses with Edit/Delete option
    st.header("Past Expenses")
    st.write(f"Debug: Total expenses loaded: {len(manager.expenses)} | Filtered: {len(filtered_expenses)}")
    if manager.expenses:  #filtered_expenses
        for expense in manager.expenses:   #filtered_expenses
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            col1.write(f"{expense['date']} - {expense['description']} ({expense['category']})")
            col2.write(f"${expense['amount']}")
            if col3.button("Edit", key=f"edit_{expense['id']}"):
                st.session_state.edit_id = expense['id']
            if col4.button("Delete", key=f"del_{expense['id']}"):
                manager.delete_expense(expense['id'])
                st.cache_data.clear()
                st.rerun()

    # Edit Form (if editing)
    if 'edit_id' in st.session_state:
        st.header("Edit Expense")
        expense = next((e for e in manager.expenses if e['id'] == st.session_state.edit_id), None)
        if expense:
            with st.form("edit_expense"):
                date = st.date_input("Date", value=datetime.strptime(expense['date'], '%Y-%m-%d').date())
                amount = st.number_input("Amount", value=expense['amount'])
                description = st.text_input("Description", value=expense['description'])
                category = st.selectbox("Category", ["General", "Food", "Transport", "Entertainment","Bills"], index=["General", "Food", "Transport", "Entertainment"].index(expense['category']))
                if st.form_submit_button("Update"):
                    manager.update_expense(st.session_state.edit_id, str(date), amount, description, category)
                    del st.session_state.edit_id
                    st.success("Updated!")
                    st.cache_data.clear()
                    st.rerun()

    # Expense Analysis Chart
    st.header("Expense Analysis")
    total = manager.calculate_total(filtered_expenses)
    st.write(f"Total Expenses: ${total:.2f}")

    # Budget Alert
    alert, current_total = manager.get_budget_alert(budget)
    if alert:
        st.error(f"Budget exceeded! Current total: ${current_total:.2f}")

    # Pie Chart (Categories)
    cat_totals = manager.get_category_totals()
    if cat_totals:
        fig = px.pie(values=list(cat_totals.values()), names=list(cat_totals.keys()), title="Expenses by Category")
        st.plotly_chart(fig)

    # Line Chart (Expenses over Time)
    if manager.expenses:
        dates = [e['date'] for e in sorted(manager.expenses, key=lambda x: x['date'])]
        amounts = [e['amount'] for e in sorted(manager.expenses, key=lambda x: x['date'])]
        fig, ax = plt.subplots()
        ax.plot(dates, amounts, marker='o',color="purple" )
        ax.set_title("Expenses Over Time")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Bar Chart (Monthly Totals)
    monthly_totals = {}
    for e in manager.expenses:
        month_num = int(e['date'][5:7])  # MM
        month_name = datetime(1900, month_num, 1).strftime('%B')
        monthly_totals[month_name] = monthly_totals.get(month_name, 0) + e['amount']
    if monthly_totals:   # Sort months by their numerical order (January=1, February=2, etc.)
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
        sorted_months = [m for m in month_order if m in monthly_totals]
        sorted_totals = [monthly_totals[m] for m in sorted_months]
        fig = px.bar(x=sorted_months, y=sorted_totals, title="Monthly Expenses",color=sorted_totals, color_continuous_scale='Blues')
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()