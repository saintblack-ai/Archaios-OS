/**
 * Cloudflare Worker scheduled trigger for Archaios OS.
 * Expects ARCHAIOS_ENDPOINT (var) and ARCHAIOS_TOKEN (secret).
 */

export default {
  async scheduled(event, env, ctx) {
    const endpoint = env.ARCHAIOS_ENDPOINT;
    const token = env.ARCHAIOS_TOKEN;

    if (!endpoint || !token) {
      console.error("Missing ARCHAIOS_ENDPOINT or ARCHAIOS_TOKEN");
      return;
    }

    const payload = {
      source: "cloudflare_worker",
      trigger: "daily_cron",
      scheduledTime: event.scheduledTime,
    };

    ctx.waitUntil(
      fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      }).then(async (res) => {
        if (!res.ok) {
          const body = await res.text();
          throw new Error(`Archaios endpoint failed: ${res.status} ${body}`);
        }
        return res.text();
      }).catch((err) => {
        console.error("Scheduled trigger error:", err);
      })
    );
  },
};
