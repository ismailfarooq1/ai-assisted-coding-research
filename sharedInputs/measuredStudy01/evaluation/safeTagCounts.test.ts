import { expect, it } from "vitest";
import { mergeTagCounts } from "@/lib/tag";
it("merges safe counts without overflow or inherited keys", () => {
  const source = Object.freeze({a: 3, zero: 0, negative: -1, fraction: 0.5, nan: NaN, infinite: Infinity, unsafe: Number.MAX_SAFE_INTEGER + 1, text: "3"} as unknown as Record<string, number>);
  const result = mergeTagCounts(undefined, source, {a: 4, huge: Number.MAX_SAFE_INTEGER}, {huge: 1});
  expect(Object.getPrototypeOf(result)).toBeNull();
  expect({...result}).toEqual({a: 7, zero: 0, huge: Number.MAX_SAFE_INTEGER});
  expect(source.a).toBe(3);
  const dangerous = JSON.parse('{"__proto__":2,"constructor":3}') as Record<string, number>;
  const special = mergeTagCounts(dangerous, dangerous);
  expect(Object.hasOwn(special, "__proto__")).toBe(true); expect(special.__proto__).toBe(4); expect(special.constructor).toBe(6);
  const inherited = Object.assign(Object.create({inherited: 7}), {own: 1});
  expect({...mergeTagCounts(inherited)}).toEqual({own: 1});
});
