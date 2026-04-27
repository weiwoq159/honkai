export function formatKey(key: string): string {
  return `idps_76_${key}`.toUpperCase();
}

export function getItem(key: string): ISafeAny {
  const str = localStorage.getItem(formatKey(key)) as string;
  try {
    return JSON.parse(str);
  } catch (e) {
    return null;
  }
}

export function setItem(key: string, data: ISafeAny) {
  localStorage.setItem(formatKey(key), JSON.stringify(data));
}

export function remoteItem(key: string) {
  localStorage.removeItem(formatKey(key));
}