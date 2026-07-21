# `cds.test()` API

> Local mirror of the relevant sections of <https://cap.cloud.sap/docs/node.js/cds-test>.

`cds.test()` is the programmatic entry point used inside a test file. It
boots a CAP server (or attaches to one), exposes HTTP helpers, and
provides Chai-based assertions.

## Booting

```js
const cds = require('@sap/cds')
const { GET, POST, PUT, PATCH, DELETE, expect, axios, defaults, data } = cds.test('@capire/bookshop')
```

You can pass:
- a path to a project folder (string)
- nothing (uses `cwd`)
- a module name (resolved via `node_modules`)

## HTTP helpers

Two equivalent calling conventions:

Tagged-template (concise, URL-only):

```js
const { data } = await GET `/browse/Books`
```

Function form (URL + body/options):

```js
await POST('/submitOrder', { book: 201, quantity: 5 })
await GET('/books', { auth: { username: 'alice' } })
```

Supported verbs: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`. They return
a response-like object with `data`, `status`, `headers`.

### Portable options

These options work no matter which underlying HTTP client `cds.test()`
selects:

- `baseURL`
- `auth` — `{ username, password }` for basic auth
- `headers`
- `validateStatus` — function `(status) => boolean`

### `defaults` object

Settings applied to every helper call:

```js
const { defaults } = cds.test()
defaults.auth = { username: 'alice' }
defaults.path = '/odata/v4/browse'
defaults.headers = { 'Accept-Language': 'en' }
defaults.validateStatus = status => status >= 500
```

## Lifecycle

- `test.run(...)` — async; starts the CDS server, returns a controlled-
  shutdown handle
- `test.in(folder)` — switches `cds.root` safely (fluent chaining)
- `test.log()` — returns `{ output, clear(), release() }` to capture
  `console.log` output during a block
- `test.data.reset()` — resets and redeploys the database; useful in
  `beforeEach` for isolation

## Globals injected when `cds.test` is loaded

- `describe(name, fn)`
- `test(name, fn)` / `it(name, fn)`
- `beforeAll`, `afterAll`, `beforeEach`, `afterEach`

## Assertions

```js
const { expect } = cds.test()
expect(data.value).to.deep.equal([...])
expect(response.data).to.containSubset({ error: { code: 'READONLY_ENTITY' } })
```

Preconfigured Chai plugins:
- `chai-subset`
- `chai-as-promised`

## Version note (very important)

- **Older versions** used Axios under the hood; the response shape and
  `validateStatus` semantics matched Axios.
- **Newer versions** default to the Fetch API. The portable options
  above continue to work, but some Axios-only fields are no longer
  available.
- **Chai 5** is ESM. Jest, which is CommonJS-first, may need to use its
  own `expect` instead of Chai's — see `test-frameworks.md`.

## Skill guidance

When writing a new test file, the skill MUST:

1. Use `cds.test(<project>)` at the top.
2. Destructure only the helpers needed (`GET`, `POST`, `expect`, etc.).
3. Group tests with `describe`, even if there's only one.
4. Use `defaults.auth` and `defaults.path` instead of repeating them
   in every call.
5. Reset DB state in `beforeEach` if the test mutates data.

When *running* a test file, the skill MUST NOT modify it. If a test is
broken, that is reported in `CAP-TEST-FAILURE.md`; the fix is the
user's call.
