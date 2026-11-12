# Optional cropped-label reader

Off by default. The UI checkbox discloses that **only cropped label regions** are
sent to **Google Gemini**, a third party. Neither selecting Handwritten nor
installing a key enables network use by itself. Each analysis request must set
`use_label_reader=true`. No key is accepted from or stored in the browser.

Server setup (choose a currently supported Gemini model for your account):

```sh
export CIRCUIT_LABEL_API_KEY='your-secret-key'
export CIRCUIT_LABEL_MODEL='your-supported-model-id'
python manage.py serve
```

PowerShell uses `$env:CIRCUIT_LABEL_API_KEY` and `$env:CIRCUIT_LABEL_MODEL`.
Do not put keys in config files, commits, request logs or screenshots.
The concrete adapter uses the official
[generateContent REST interface](https://ai.google.dev/api/generate-content),
inline PNG data and the `x-goog-api-key` header. Provider calls were **not run**
here: no key or user image consent was supplied. Tests use httpx MockTransport.

`LabelReader` is provider agnostic; a custom adapter may be supplied through
`configure_label_reader`. The enclosing crop gate still enforces the geometry
and vocabulary. Up to eight ambiguous regions, at most 640×160 px and at most
20% of the working raster area each, are considered. A whole-image box is
rejected. Region coordinates are mapped back on the server; provider boxes are
not trusted. Requests time out after eight seconds per crop. Responses must
match R/C/L/V/E/K identifiers, digits (including Bangla), known units or an
explicit unknown marker and must pass the local value parser. Prose is rejected.
The fixed 0.65 confidence ceiling is a conservative policy, not a measured model
probability. Reader failure leaves local evidence/assumptions editable and warns.

Automatic style classification is an **untrained heuristic**, using stroke-width
variation, line straightness and background texture; its 0.55 confidence is a
policy value, not measured accuracy. Printed/photo/handwritten accuracy remains
null without labeled style examples. The user can override Auto with Printed or
Handwritten. Faint periodic monochrome ruling is removed while dark ink is kept;
same-contrast black grids cannot be reliably distinguished and are left intact.
Perspective fallback uses document-like contours or warns and skips correction.
