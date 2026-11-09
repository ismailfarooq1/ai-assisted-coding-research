import { expect, it } from "vitest";
import { colorToHex } from "@/lib/color";

// Post-execution task-validity audit, not a replacement for the frozen primary oracle.
// The task did not specify where alpha belongs. Each candidate must satisfy the
// entire behavior vector through one consistent interface, not choose per case.
it("satisfies alpha behavior through one consistently applied reasonable interface", () => {
  type Color = { red?: number; green?: number; blue?: number };
  const candidate = colorToHex as (...args: unknown[]) => string | undefined;
  const cases: [Color | undefined, number | undefined, string | undefined][] = [
    [undefined, undefined, undefined],
    [undefined, 0.5, undefined],
    [{}, undefined, "#000000"],
    [{ red: 1, green: 0.5, blue: 0 }, undefined, "#ff8000"],
    [{ red: 1, green: 0.5, blue: 0 }, 0.5, "#ff800080"],
    [{}, 0, "#00000000"],
    [{}, 1, "#000000ff"],
    [{}, -1, "#00000000"],
    [{}, 2, "#000000ff"],
    [{}, Infinity, "#000000ff"],
    [{}, -Infinity, "#000000ff"],
    [{}, NaN, "#000000ff"],
    [{ red: NaN, green: -1, blue: 2 }, undefined, "#0000ff"],
  ];
  const objectResults = cases.map(([color, alpha]) => candidate(color === undefined ? undefined : { ...color, alpha }));
  const secondArgumentResults = cases.map(([color, alpha]) => candidate(color, alpha));
  const expected = cases.map(([, , value]) => value);
  const supported = [objectResults, secondArgumentResults].map((values) => values.every((value, index) => value === expected[index]));
  expect(supported.some(Boolean), JSON.stringify({ objectResults, secondArgumentResults, expected })).toBe(true);
});
