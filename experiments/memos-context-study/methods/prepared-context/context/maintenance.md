# Context maintenance

Sources: [`AGENTS.md`, Documentation](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/AGENTS.md), [`CONTEXT.md`](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/CONTEXT.md), and [`docs/design/README.md`](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/docs/design/README.md), commit `b40d8a7b573774c52b022c8d6537d6baf2129dc0`.

When a code change affects guidance, check the native agent instructions, relevant package README/doc.go files and any corresponding prepared notes. Verify statements against current source and tests. Keep domain terminology consistent with `CONTEXT.md`.

Memos distinguishes design rationale from current behavior. Unreleased designs may evolve with their implementation. After release, the design body is frozen and later changes belong in dated amendments. Use source, tests and current package documentation to determine behavior rather than assuming a historical design body describes the latest code.

For this additional context pack, cite updated source evidence when revising a statement. Flag uncertainty or contradictions instead of presenting an unverified statement as fact. Keep notes relevant to the assigned task and affected project behavior.
