/* global Office */

/** Word on macOS (desktop). */
export function isWordMac() {
  try {
    return (
      typeof Office !== "undefined" &&
      Office.context?.platform === Office.PlatformType.Mac
    );
  } catch {
    return false;
  }
}

export function isWordDesktop() {
  try {
    const p = Office?.context?.platform;
    return (
      p === Office.PlatformType.Mac || p === Office.PlatformType.PC
    );
  } catch {
    return true;
  }
}
