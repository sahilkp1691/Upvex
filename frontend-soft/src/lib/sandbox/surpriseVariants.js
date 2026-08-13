/** Surprise-me problem variants (mirrors backend sandbox_problems.py) */

export const SURPRISE_VARIANTS = [
	{
		question_text:
			'Which sales reps (employee name) sold more than $30,000 total? Return `name` and `total_sales`.',
		dataset: 'employees',
		starter_sql: 'SELECT ',
		solution_sql:
			'SELECT e.name, SUM(s.amount) AS total_sales FROM employees e JOIN sales s ON e.emp_id = s.emp_id GROUP BY e.name HAVING SUM(s.amount) > 30000',
		hints: ['Join employees to sales.', 'SUM(amount) per employee.', 'HAVING filters groups.'],
		order_sensitive: false,
		difficulty: 5,
		explanation: 'HAVING filters aggregated groups by a threshold.'
	},
	{
		question_text:
			'List customers from the UK with their total order quantity. Return `name` and `total_qty`.',
		dataset: 'orders',
		starter_sql: 'SELECT ',
		solution_sql:
			"SELECT c.name, SUM(ol.quantity) AS total_qty FROM customers c JOIN order_lines ol ON c.customer_id = ol.customer_id WHERE c.country = 'UK' GROUP BY c.name",
		hints: ["Filter customers WHERE country = 'UK'.", 'Join to order_lines.', 'SUM(quantity) per customer.'],
		order_sensitive: false,
		difficulty: 4,
		explanation: 'WHERE filters rows before aggregation; GROUP BY collapses per customer.'
	},
	{
		question_text:
			'Find the top-selling product category by total revenue (quantity * unit_price). Return `category` and `revenue`.',
		dataset: 'orders',
		starter_sql: 'SELECT ',
		solution_sql:
			'SELECT p.category, SUM(ol.quantity * p.unit_price) AS revenue FROM order_lines ol JOIN products p ON ol.product_id = p.product_id GROUP BY p.category ORDER BY revenue DESC LIMIT 1',
		hints: ['Join order_lines to products.', 'Revenue = quantity * unit_price.', 'ORDER BY revenue DESC LIMIT 1.'],
		order_sensitive: false,
		difficulty: 6,
		explanation: 'Computed aggregates in SELECT with ORDER BY LIMIT picks the top group.'
	}
];

export function randomSurprise() {
	return SURPRISE_VARIANTS[Math.floor(Math.random() * SURPRISE_VARIANTS.length)];
}
