import { expect, it } from "vitest";
import { getMemoViewId, isCalendarRoute } from "@/lib/memo-views";
it("extracts only exact user-view resource names", () => {
  for (const [name, value] of [["users/steven/views/work", "work"], ["users/a b/views/x y", "x y"]]) expect(getMemoViewId(name)).toBe(value);
  for (const name of ["orgs/a/views/b", "users/a/memos/b", "users//views/x", "users/a/views/", "users/a/views/x/y", "/users/a/views/x", "work", "", "Users/a/views/b"]) expect(getMemoViewId(name)).toBe(name);
  expect(isCalendarRoute("/calendar/2026/11")).toBe(true);
});
