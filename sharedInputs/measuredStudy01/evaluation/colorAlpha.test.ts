import { expect, it } from "vitest";
import { colorToHex } from "@/lib/color";
it("supports explicit alpha and preserves RGB behavior", () => {
  const convert = colorToHex as (value?: {red?: number; green?: number; blue?: number; alpha?: number}) => string | undefined;
  expect(convert({red: 1, green: 0.5, blue: 0, alpha: 0.5})).toBe("#ff800080");
  expect(convert({alpha: 0})).toBe("#00000000");
  expect(convert({alpha: 1})).toBe("#000000ff");
  for (const alpha of [Infinity, -Infinity, NaN, 2]) expect(convert({alpha})).toBe("#000000ff");
  expect(convert({alpha: -1})).toBe("#00000000");
  expect(convert({red: NaN, green: -1, blue: 2})).toBe("#0000ff");
  expect(convert({alpha: undefined})).toBe("#000000");
  expect(convert()).toBeUndefined();
});
