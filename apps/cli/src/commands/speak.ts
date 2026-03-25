export async function speak(
  baseUrl: string,
  text: string,
  opts: { voice?: string; speed?: string }
) {
  const res = await fetch(`${baseUrl}/api/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      voice: opts.voice,
      speed: opts.speed ? parseFloat(opts.speed) : undefined,
    }),
  });

  if (!res.ok) {
    console.error(`Error: ${res.status} ${res.statusText}`);
    process.exit(1);
  }

  const data = (await res.json()) as Record<string, unknown>;
  const duration = data.duration_estimate;
  console.log(duration ? `Speaking: "${text}" (~${duration}s)` : `Speaking: "${text}"`);
}
