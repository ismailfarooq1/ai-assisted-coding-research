import { expect, it } from "vitest";
import { getDuplicateSpaceTitles } from "@/lib/space-display";
it("groups NFC-equivalent titles and retains original spellings and order", () => {
  const input = Object.freeze([Object.freeze({title: "cafe\u0301"}), Object.freeze({title: "x"}), Object.freeze({title: "café"}), Object.freeze({title: "x"})]);
  expect([...getDuplicateSpaceTitles(input)]).toEqual(["cafe\u0301", "x", "café"]);
  expect([...getDuplicateSpaceTitles([{title:"A"},{title:"a"},{title:" A"}])]).toEqual([]);
  expect([...getDuplicateSpaceTitles([{title:"Product"},{title:"research"},{title:"Product"},{title:"product"}])]).toEqual(["Product"]);
  expect([...getDuplicateSpaceTitles([])]).toEqual([]);
  expect(input[0].title).toBe("cafe\u0301");
});
