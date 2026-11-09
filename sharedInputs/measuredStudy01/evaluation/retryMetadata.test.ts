import { expect, it } from "vitest";
import { BinaryWriter } from "@bufbuild/protobuf/wire";
import { Code, ConnectError } from "@connectrpc/connect";
import { getRetryAfterSeconds, getErrorMessage } from "@/lib/error";
const makeError = (value: string, reason = "RATE_LIMITED") => {
  const writer = new BinaryWriter();
  writer.tag(1, 2).string(reason); writer.tag(2, 2).string("memos.api");
  const entry = new BinaryWriter(); entry.tag(1, 2).string("retry_after_seconds"); entry.tag(2, 2).string(value);
  writer.tag(3, 2).bytes(entry.finish());
  const error = new ConnectError("original", Code.ResourceExhausted);
  error.details.push({type: "google.rpc.ErrorInfo", value: writer.finish()}); return error;
};
it("strictly parses positive safe-integer delay metadata", () => {
  for (const value of ["1", "42", "9007199254740991"]) expect(getRetryAfterSeconds(makeError(value))).toBe(Number(value));
  for (const value of ["", "0", "-1", "+1", "01", "1.5", "1e3", "42junk", " 42", "42 ", "9007199254740992", "Infinity"]) expect(getRetryAfterSeconds(makeError(value))).toBeUndefined();
  expect(getRetryAfterSeconds(makeError("42", "OTHER"))).toBeUndefined();
  expect(getRetryAfterSeconds(new Error("x"))).toBeUndefined();
  expect(getErrorMessage(makeError("42"))).toBe("Too many requests. Try again in 42s.");
  expect(getErrorMessage(makeError("42junk"))).toBe("original");
});
