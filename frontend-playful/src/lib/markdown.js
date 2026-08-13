import { marked } from 'marked';

marked.use({
	gfm: true,
	breaks: false
});

const ALLOWED_TAGS = new Set([
	'a',
	'blockquote',
	'br',
	'code',
	'del',
	'div',
	'em',
	'h1',
	'h2',
	'h3',
	'h4',
	'hr',
	'li',
	'ol',
	'p',
	'pre',
	'strong',
	'table',
	'tbody',
	'td',
	'th',
	'thead',
	'tr',
	'ul'
]);

const ALLOWED_ATTRS = {
	a: new Set(['href', 'title']),
	td: new Set(['align']),
	th: new Set(['align']),
	code: new Set(['class']),
	pre: new Set(['class'])
};

/**
 * Escape HTML special characters in plain text.
 * @param {string} text
 */
function escapeText(text) {
	return text
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;');
}

/**
 * Strip disallowed tags/attrs from marked HTML. Keeps markdown output safe for {@html}.
 * @param {string} html
 */
function sanitize(html) {
	return html.replace(/<\/?([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>/g, (match, tag, attrs) => {
		const name = tag.toLowerCase();
		const closing = match.startsWith('</');
		if (!ALLOWED_TAGS.has(name)) return '';
		if (closing) return `</${name}>`;

		const allowed = ALLOWED_ATTRS[name];
		if (!allowed || !attrs.trim()) return `<${name}>`;

		const kept = [];
		const attrRe = /([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g;
		let m;
		while ((m = attrRe.exec(attrs)) !== null) {
			const attr = m[1].toLowerCase();
			if (!allowed.has(attr)) continue;
			let value = m[2] ?? m[3] ?? m[4] ?? '';
			if (attr === 'href') {
				const trimmed = value.trim();
				if (!/^(https?:|mailto:|#)/i.test(trimmed)) continue;
				value = trimmed.replace(/"/g, '&quot;');
			} else {
				value = escapeText(value);
			}
			kept.push(`${attr}="${value}"`);
		}
		return kept.length ? `<${name} ${kept.join(' ')}>` : `<${name}>`;
	});
}

/**
 * Render lesson markdown (GFM, including tables) to sanitized HTML.
 * @param {string | null | undefined} src
 * @returns {string}
 */
export function renderMarkdown(src) {
	if (!src) return '';
	const parsed = marked.parse(String(src), { async: false });
	let html = sanitize(typeof parsed === 'string' ? parsed : String(parsed));
	html = html.replace(/<table\b[\s\S]*?<\/table>/gi, (table) => `<div class="table-wrap">${table}</div>`);
	return html;
}
