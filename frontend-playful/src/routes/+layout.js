// Upvex runs as an SPA: auth tokens live client-side and all data comes from
// the FastAPI backend, so SSR adds complexity without benefit in v1.
export const ssr = false;
export const prerender = false;
