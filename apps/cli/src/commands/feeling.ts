export async function feeling(baseUrl: string, name: string) {
  const res = await fetch(`${baseUrl}/api/feeling`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  if (!res.ok) {
    console.error(`Error: ${res.status} ${res.statusText}`);
    process.exit(1);
  }

  console.log(`Feeling set: ${name}`);
}
