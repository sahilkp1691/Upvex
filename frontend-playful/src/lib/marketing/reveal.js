/**
 * Scroll-triggered reveal action for the marketing pages.
 * Adds `.is-in` once the element crosses into the viewport, with an optional
 * stagger delay, instead of firing on mount regardless of scroll position.
 *
 * Usage: <div use:reveal={{ delay: i * 70 }} data-reveal>...</div>
 * @param {HTMLElement} node
 * @param {{ delay?: number }} [opts]
 */
export function reveal(node, opts = {}) {
	const apply = ({ delay = 0 } = {}) => {
		node.style.setProperty('--reveal-delay', `${delay}ms`);
	};
	apply(opts);

	if (typeof IntersectionObserver === 'undefined') {
		node.classList.add('is-in');
		return {};
	}

	const observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) {
					entry.target.classList.add('is-in');
					observer.unobserve(entry.target);
				}
			}
		},
		{ threshold: 0.15, rootMargin: '0px 0px -10% 0px' }
	);
	observer.observe(node);

	return {
		update: apply,
		destroy() {
			observer.disconnect();
		}
	};
}
