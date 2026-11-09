import { expect, it } from "vitest";
import { getReleaseTag } from "@/lib/release-version";
it("normalizes historical tags idempotently without broadening calendar syntax", () => {
  for (const value of ["v0.1.0", "v0.0.0", "v0.25.9-rc.2"]) expect(getReleaseTag(value)).toBe(value);
  expect(getReleaseTag("0.25.9-rc.2")).toBe("v0.25.9-rc.2");
  expect(getReleaseTag("26.09.0")).toBe("26.09.0");
  for (const value of ["v26.09.0", "vv0.1.0", "V0.1.0", " v0.1.0", "v0.1.0 ", "v0.01.0", "v0.1.00", "v0.1.0-rc.0", "v0.1.0-rc.01", "v1.2.3"]) expect(getReleaseTag(value)).toBeUndefined();
});
