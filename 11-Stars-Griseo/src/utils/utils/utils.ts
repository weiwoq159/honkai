export function parseJSON(jsonString: string, defaultValue?: unknown) {
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    console.error(error);
    return defaultValue ?? {};
  }
}
