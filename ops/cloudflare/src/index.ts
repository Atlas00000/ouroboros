/**
 * Placeholder Cloudflare Worker entry — not used by Phase 0/1 runtime.
 * Replace when you add a real Worker (e.g. edge webhook, R2 helper).
 */
export default {
  async fetch(_request: Request): Promise<Response> {
    return new Response("Ouroboros Cloudflare placeholder", { status: 200 });
  },
};
