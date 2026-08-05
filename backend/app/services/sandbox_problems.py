"""Curated SQL sandbox problems for dev stubs and surprise-me variants."""

from __future__ import annotations

SQL_SANDBOX_PROBLEMS: dict[str, dict] = {
    "sql_select_basics": {
        "question_text": (
            "Write a query that returns every employee's name and salary, "
            "sorted alphabetically by name. Return columns named `name` and `salary`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Select employee names and salaries\nSELECT ",
        "solution_sql": "SELECT name, salary FROM employees ORDER BY name",
        "hints": [
            "You only need the employees table for this one.",
            "Use SELECT with the two column names, then FROM employees.",
            "Add ORDER BY name at the end for alphabetical order.",
        ],
        "order_sensitive": True,
        "difficulty": 2,
        "explanation": "A basic SELECT with ORDER BY sorts rows alphabetically by name.",
    },
    "sql_filtering": {
        "question_text": (
            "Find all employees in the Engineering department (dept_id = 1) "
            "who earn more than $80,000. Return `name` and `salary`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Filter by department and salary\nSELECT ",
        "solution_sql": (
            "SELECT name, salary FROM employees "
            "WHERE dept_id = 1 AND salary > 80000"
        ),
        "hints": [
            "Filter rows with WHERE — you need two conditions.",
            "dept_id = 1 identifies Engineering.",
            "Combine with AND salary > 80000.",
        ],
        "order_sensitive": False,
        "difficulty": 3,
        "explanation": "WHERE combines predicates with AND to narrow rows.",
    },
    "sql_aggregations": {
        "question_text": (
            "For each department, compute the average salary of its employees. "
            "Join departments to employees and return `department_name` and `avg_salary` "
            "(rounded to 2 decimals)."
        ),
        "dataset": "employees",
        "starter_sql": "-- Average salary per department\nSELECT ",
        "solution_sql": (
            "SELECT d.name AS department_name, ROUND(AVG(e.salary), 2) AS avg_salary "
            "FROM departments d "
            "JOIN employees e ON d.dept_id = e.dept_id "
            "GROUP BY d.name"
        ),
        "hints": [
            "Join departments and employees on dept_id.",
            "Use AVG(e.salary) with GROUP BY department name.",
            "ROUND(AVG(...), 2) keeps two decimal places.",
        ],
        "order_sensitive": False,
        "difficulty": 4,
        "explanation": "GROUP BY collapses rows per department; AVG aggregates salary within each group.",
    },
    "sql_joins": {
        "question_text": (
            "Produce a list of every employee who has a manager, showing the employee's name "
            "and their manager's name side-by-side. Return columns `employee_name` and `manager_name`, "
            "ordered alphabetically by employee name."
        ),
        "dataset": "employees",
        "starter_sql": "-- Self-join employees to their managers\nSELECT ",
        "solution_sql": (
            "SELECT e.name AS employee_name, m.name AS manager_name "
            "FROM employees e "
            "JOIN employees m ON e.manager_id = m.emp_id "
            "WHERE e.manager_id IS NOT NULL "
            "ORDER BY e.name"
        ),
        "hints": [
            "This is a self-join — alias employees twice (e and m).",
            "Match e.manager_id to m.emp_id.",
            "Filter out rows where manager_id IS NULL, then ORDER BY employee name.",
        ],
        "order_sensitive": True,
        "difficulty": 5,
        "explanation": "A self-join links each employee row to their manager's row via manager_id.",
    },
    "sql_subqueries": {
        "question_text": (
            "Find employees who earn more than the company-wide average salary. "
            "Return `name` and `salary`, ordered by salary descending."
        ),
        "dataset": "employees",
        "starter_sql": "-- Subquery for average salary\nSELECT ",
        "solution_sql": (
            "SELECT name, salary FROM employees "
            "WHERE salary > (SELECT AVG(salary) FROM employees) "
            "ORDER BY salary DESC"
        ),
        "hints": [
            "Compute AVG(salary) in a subquery inside WHERE.",
            "Compare each employee's salary to that average.",
            "ORDER BY salary DESC for highest first.",
        ],
        "order_sensitive": True,
        "difficulty": 5,
        "explanation": "A scalar subquery in WHERE filters rows against an aggregate computed separately.",
    },
    "sql_window_functions": {
        "question_text": (
            "Rank employees within each department by salary (highest = 1). "
            "Return `name`, `dept_id`, `salary`, and `salary_rank`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Window ranking by department\nSELECT ",
        "solution_sql": (
            "SELECT name, dept_id, salary, "
            "RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS salary_rank "
            "FROM employees"
        ),
        "hints": [
            "Use RANK() OVER (...) — a window function.",
            "PARTITION BY dept_id restarts ranking per department.",
            "ORDER BY salary DESC inside OVER so rank 1 is highest paid.",
        ],
        "order_sensitive": False,
        "difficulty": 6,
        "explanation": "RANK() OVER (PARTITION BY … ORDER BY …) ranks within peer groups without collapsing rows.",
    },
    "sql_relational_model": {
        "question_text": (
            "Show every department name alongside how many employees belong to it. "
            "Return `department_name` and `employee_count`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Count employees per department\nSELECT ",
        "solution_sql": (
            "SELECT d.name AS department_name, COUNT(e.emp_id) AS employee_count "
            "FROM departments d "
            "LEFT JOIN employees e ON d.dept_id = e.dept_id "
            "GROUP BY d.name"
        ),
        "hints": [
            "LEFT JOIN keeps departments even with zero employees.",
            "COUNT(e.emp_id) counts employees per group.",
            "GROUP BY department name.",
        ],
        "order_sensitive": False,
        "difficulty": 3,
        "explanation": "LEFT JOIN preserves all departments; COUNT aggregates related employee rows.",
    },
    "sql_data_modeling": {
        "question_text": (
            "List employees who belong to more than one sales region. "
            "Return `name` and `region_count`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Employees spanning multiple regions\nSELECT ",
        "solution_sql": (
            "SELECT e.name, COUNT(r.region_id) AS region_count "
            "FROM employees e "
            "JOIN regions r ON e.emp_id = r.emp_id "
            "GROUP BY e.name "
            "HAVING COUNT(r.region_id) > 1"
        ),
        "hints": [
            "Join employees to regions.",
            "GROUP BY employee name and COUNT regions.",
            "HAVING filters groups with more than one region.",
        ],
        "order_sensitive": False,
        "difficulty": 5,
        "explanation": "HAVING filters aggregated groups after GROUP BY.",
    },
    "sql_indexes": {
        "question_text": (
            "Find the highest-paid employee in each department. "
            "Return `dept_id`, `name`, and `salary`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Top earner per department\nSELECT ",
        "solution_sql": (
            "SELECT dept_id, name, salary FROM ("
            "SELECT dept_id, name, salary, "
            "RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rk "
            "FROM employees) WHERE rk = 1"
        ),
        "hints": [
            "Use a window function to rank by salary within dept_id.",
            "Wrap in a subquery and filter rk = 1.",
            "RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC).",
        ],
        "order_sensitive": False,
        "difficulty": 6,
        "explanation": "Window ranking inside a subquery isolates the top row per partition.",
    },
    "sql_transactions": {
        "question_text": (
            "Show total sales amount per employee name. Return `name` and `total_sales`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Aggregate sales per employee\nSELECT ",
        "solution_sql": (
            "SELECT e.name, SUM(s.amount) AS total_sales "
            "FROM employees e "
            "JOIN sales s ON e.emp_id = s.emp_id "
            "GROUP BY e.name"
        ),
        "hints": [
            "Join employees to sales on emp_id.",
            "SUM(s.amount) aggregates per employee.",
            "GROUP BY e.name.",
        ],
        "order_sensitive": False,
        "difficulty": 4,
        "explanation": "Joining then aggregating produces per-employee totals from transactional rows.",
    },
    "sql_query_optimization": {
        "question_text": (
            "Find departments where average employee salary exceeds $75,000. "
            "Return `department_name` and `avg_salary`."
        ),
        "dataset": "employees",
        "starter_sql": "-- High-average departments\nSELECT ",
        "solution_sql": (
            "SELECT d.name AS department_name, AVG(e.salary) AS avg_salary "
            "FROM departments d "
            "JOIN employees e ON d.dept_id = e.dept_id "
            "GROUP BY d.name "
            "HAVING AVG(e.salary) > 75000"
        ),
        "hints": [
            "Join departments and employees.",
            "GROUP BY department and compute AVG(salary).",
            "HAVING AVG(e.salary) > 75000 filters groups.",
        ],
        "order_sensitive": False,
        "difficulty": 5,
        "explanation": "HAVING filters on aggregate values after GROUP BY.",
    },
    "sql_advanced_analytics": {
        "question_text": (
            "For each employee, show their name, salary, and the running total of salary "
            "within their department (ordered by salary ascending). "
            "Return `name`, `dept_id`, `salary`, `running_total`."
        ),
        "dataset": "employees",
        "starter_sql": "-- Running total with window function\nSELECT ",
        "solution_sql": (
            "SELECT name, dept_id, salary, "
            "SUM(salary) OVER (PARTITION BY dept_id ORDER BY salary "
            "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total "
            "FROM employees"
        ),
        "hints": [
            "Use SUM() OVER with PARTITION BY dept_id.",
            "ORDER BY salary inside the window frame.",
            "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW for running total.",
        ],
        "order_sensitive": False,
        "difficulty": 7,
        "explanation": "A running total window frame accumulates values within each partition.",
    },
}

SQL_SURPRISE_VARIANTS: list[dict] = [
    {
        "question_text": "Which sales reps (employee name) sold more than $30,000 total? Return `name` and `total_sales`.",
        "dataset": "employees",
        "starter_sql": "SELECT ",
        "solution_sql": (
            "SELECT e.name, SUM(s.amount) AS total_sales "
            "FROM employees e JOIN sales s ON e.emp_id = s.emp_id "
            "GROUP BY e.name HAVING SUM(s.amount) > 30000"
        ),
        "hints": ["Join employees to sales.", "SUM(amount) per employee.", "HAVING filters groups."],
        "order_sensitive": False,
        "difficulty": 5,
        "explanation": "HAVING filters aggregated groups by a threshold.",
    },
    {
        "question_text": "List customers from the UK with their total order quantity. Return `name` and `total_qty`.",
        "dataset": "orders",
        "starter_sql": "SELECT ",
        "solution_sql": (
            "SELECT c.name, SUM(ol.quantity) AS total_qty "
            "FROM customers c "
            "JOIN order_lines ol ON c.customer_id = ol.customer_id "
            "WHERE c.country = 'UK' "
            "GROUP BY c.name"
        ),
        "hints": ["Filter customers WHERE country = 'UK'.", "Join to order_lines.", "SUM(quantity) per customer."],
        "order_sensitive": False,
        "difficulty": 4,
        "explanation": "WHERE filters rows before aggregation; GROUP BY collapses per customer.",
    },
    {
        "question_text": "Find the top-selling product category by total revenue (quantity * unit_price). Return `category` and `revenue`.",
        "dataset": "orders",
        "starter_sql": "SELECT ",
        "solution_sql": (
            "SELECT p.category, SUM(ol.quantity * p.unit_price) AS revenue "
            "FROM order_lines ol "
            "JOIN products p ON ol.product_id = p.product_id "
            "GROUP BY p.category "
            "ORDER BY revenue DESC LIMIT 1"
        ),
        "hints": ["Join order_lines to products.", "Revenue = quantity * unit_price.", "ORDER BY revenue DESC LIMIT 1."],
        "order_sensitive": False,
        "difficulty": 6,
        "explanation": "Computed aggregates in SELECT with ORDER BY LIMIT picks the top group.",
    },
]


def problem_for_concept(concept_id: str) -> dict | None:
    return SQL_SANDBOX_PROBLEMS.get(concept_id)


def fallback_problem(concept_id: str | None = None, dataset: str | None = None) -> dict:
    """A curated problem to swap in when a generated one doesn't run.

    Prefers the concept's own problem, then any problem on the same dataset, so the
    learner still gets something relevant rather than a broken challenge.
    """
    if concept_id:
        own = SQL_SANDBOX_PROBLEMS.get(concept_id)
        if own and (dataset is None or own["dataset"] == dataset):
            return own
    if dataset:
        for problem in SQL_SANDBOX_PROBLEMS.values():
            if problem["dataset"] == dataset:
                return problem
        for variant in SQL_SURPRISE_VARIANTS:
            if variant["dataset"] == dataset:
                return variant
    return SQL_SANDBOX_PROBLEMS["sql_select_basics"]


def is_sql_topic(topic_id: str) -> bool:
    return topic_id == "topic_sql"
