/** Client-side mirror of backend SQL datasets for sql.js */

export const SQL_DATASETS = {
	employees: {
		label: 'HR & Sales',
		description: 'Classic employee / department / sales schema for joins and aggregations.',
		tables: {
			departments: {
				columns: [
					{ name: 'dept_id', type: 'INTEGER', pk: true },
					{ name: 'name', type: 'TEXT' }
				],
				rows: [
					[1, 'Engineering'],
					[2, 'Sales'],
					[3, 'Marketing'],
					[4, 'HR']
				]
			},
			employees: {
				columns: [
					{ name: 'emp_id', type: 'INTEGER', pk: true },
					{ name: 'name', type: 'TEXT' },
					{ name: 'dept_id', type: 'INTEGER' },
					{ name: 'salary', type: 'REAL' },
					{ name: 'manager_id', type: 'INTEGER' }
				],
				rows: [
					[1, 'Alice Chen', 1, 120000, null],
					[2, 'Bob Martinez', 1, 95000, 1],
					[3, 'Carol White', 2, 88000, null],
					[4, 'David Kim', 2, 76000, 3],
					[5, 'Eva Patel', 3, 82000, null],
					[6, 'Frank Lopez', 1, 71000, 1],
					[7, 'Grace Nguyen', 4, 69000, null],
					[8, 'Henry Brown', 2, 54000, 3]
				]
			},
			regions: {
				columns: [
					{ name: 'region_id', type: 'INTEGER', pk: true },
					{ name: 'emp_id', type: 'INTEGER' },
					{ name: 'region_name', type: 'TEXT' }
				],
				rows: [
					[1, 3, 'West'],
					[2, 3, 'East'],
					[3, 4, 'West'],
					[4, 8, 'East']
				]
			},
			sales: {
				columns: [
					{ name: 'sale_id', type: 'INTEGER', pk: true },
					{ name: 'emp_id', type: 'INTEGER' },
					{ name: 'amount', type: 'REAL' },
					{ name: 'sale_date', type: 'TEXT' },
					{ name: 'region', type: 'TEXT' }
				],
				rows: [
					[1, 3, 42000, '2025-01-15', 'West'],
					[2, 4, 18500, '2025-01-22', 'West'],
					[3, 8, 9200, '2025-02-03', 'East'],
					[4, 3, 31000, '2025-02-18', 'East'],
					[5, 4, 22100, '2025-03-01', 'West'],
					[6, 8, 14800, '2025-03-12', 'East']
				]
			}
		}
	},
	orders: {
		label: 'E-commerce',
		description: 'Customers, products, and order lines for filtering and GROUP BY practice.',
		tables: {
			customers: {
				columns: [
					{ name: 'customer_id', type: 'INTEGER', pk: true },
					{ name: 'name', type: 'TEXT' },
					{ name: 'city', type: 'TEXT' },
					{ name: 'country', type: 'TEXT' }
				],
				rows: [
					[1, 'Acme Corp', 'London', 'UK'],
					[2, 'Globex', 'Paris', 'FR'],
					[3, 'Initech', 'Berlin', 'DE'],
					[4, 'Umbrella Co', 'Madrid', 'ES']
				]
			},
			products: {
				columns: [
					{ name: 'product_id', type: 'INTEGER', pk: true },
					{ name: 'name', type: 'TEXT' },
					{ name: 'category', type: 'TEXT' },
					{ name: 'unit_price', type: 'REAL' }
				],
				rows: [
					[1, 'Widget A', 'Hardware', 29.99],
					[2, 'Widget B', 'Hardware', 49.99],
					[3, 'Cloud Plan', 'SaaS', 99.0],
					[4, 'Support Pack', 'Services', 199.0]
				]
			},
			order_lines: {
				columns: [
					{ name: 'line_id', type: 'INTEGER', pk: true },
					{ name: 'order_id', type: 'INTEGER' },
					{ name: 'customer_id', type: 'INTEGER' },
					{ name: 'product_id', type: 'INTEGER' },
					{ name: 'quantity', type: 'INTEGER' },
					{ name: 'order_date', type: 'TEXT' }
				],
				rows: [
					[1, 1001, 1, 1, 10, '2025-01-05'],
					[2, 1001, 1, 3, 1, '2025-01-05'],
					[3, 1002, 2, 2, 5, '2025-01-12'],
					[4, 1003, 3, 1, 20, '2025-02-01'],
					[5, 1004, 1, 4, 2, '2025-02-14'],
					[6, 1005, 4, 3, 3, '2025-03-02']
				]
			}
		}
	}
};

export function getDatasetSchema(name) {
	const ds = SQL_DATASETS[name];
	if (!ds) return null;
	const tables = {};
	for (const [tname, tdef] of Object.entries(ds.tables)) {
		tables[tname] = {
			columns: tdef.columns,
			row_count: tdef.rows.length,
			sample_rows: tdef.rows.slice(0, 5)
		};
	}
	return { name, label: ds.label, description: ds.description, tables };
}
