# Cursor project configuration

## MCP servers (`mcp.json`)

Project-scoped [Model Context Protocol](https://cursor.com/docs/mcp) servers for
this repo. Cursor loads `.cursor/mcp.json` automatically when the workspace is
opened.

### `nocodebackend`

Runs the [`@nocodebackend/mcp`](https://www.npmjs.com/package/@nocodebackend/mcp)
server via `npx`. It requires an `NCB_TOKEN` API token.

The token is **not** committed. `mcp.json` references it with
`${env:NCB_TOKEN}`, which Cursor resolves from your environment at startup.
Set it before launching Cursor:

```sh
# add to ~/.zshrc / ~/.bashrc (or your OS-level env so GUI launches inherit it)
export NCB_TOKEN="ncb_your_token_here"
```

Verify it is visible to Cursor with `echo $NCB_TOKEN` in the same shell you
launch Cursor from, then restart Cursor so it re-reads the config.

> Never paste a live `NCB_TOKEN` directly into `mcp.json` or any other tracked
> file. If a token has been exposed, rotate it in NoCodeBackend.
