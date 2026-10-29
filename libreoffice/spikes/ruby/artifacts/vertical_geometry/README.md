# Vertical ruby geometry spike

Compares `CENTER` / `BLOCK` / `INDENT_BLOCK` for `本文`/`もと` in vertical writing:

- Hiragino Mincho ProN and Hiragino Sans
- Document grid ON and OFF
- Large body size (28pt) for inspection

Rebuild:

```bash
./run_ruby_vertical_geometry_spike.sh
```

Report: [docs/ruby/08-VERTICAL-FRAME-VS-OPTICAL.md](../../../../../docs/ruby/08-VERTICAL-FRAME-VS-OPTICAL.md)

**Note:** PDF text extraction often omits body ruby; trust on-screen/PDF *paint* and ODF `ruby-align`, not PDF string positions for も/と.
