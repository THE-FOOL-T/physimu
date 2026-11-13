# Public mechanics starter pack (2026-11-13)

The owner confirmed there is no reviewed gold/real-label pool and asked Codex to
find material. Seven local PNGs and seven **null-scene, unreviewed** authoring
scaffolds are prepared under ignored `.cache/m4-public-candidates-v1/`. Five fresh
diagrams are reasonable starting candidates, one pendulum was already used for
M3 QA, and one inconsistent projectile diagram is quarantined. None is a reviewed
label, training example, gold scene or benchmark. No image enters Git or the
frozen/real training folders.

Start with `images/atwood.png`, `images/incline_block.png` or
`images/incline_pulley.png`. Upload a PNG in the app's Mechanics workspace and
follow [authoring.md](authoring.md). The supplied `authoring/<id>/human-template.json`
records its exact hash and public reference, leaves scene null/review false, and
keeps the licence decision pending. Source groups are provisional: both UBC
images stay together, as do both projectile versions. Only independent human
scene/label review can turn appropriate material into frozen evaluation data.
The master brief explicitly says Codex never writes the gold scenes.

## Sources and local outcomes

Rights below are the individual publisher/uploader's stated terms, not a licence
choice or approval for the owner. Preserve attribution when required. SVGs were
rendered unchanged onto white PNGs in headless Edge at max dimension 1200; UBC
PNGs are the publisher's original bytes. No geometry or labels were edited.

| Local PNG | Source and credited author | Stated rights | Review/quality limit |
| --- | --- | --- | --- |
| `images/atwood.png` | [AtwoodMachine.svg](https://commons.wikimedia.org/wiki/File:AtwoodMachine.svg), Mpfiz | Author public-domain release | Colored force arrows and symbolic masses; physical values still require explicit assumptions/entries. |
| `images/spring_mass.png` | [Mass spring.svg](https://commons.wikimedia.org/wiki/File:Mass_spring.svg), SVG redraw Pbroks13, underlying author Lzyvzl | Page states Lzyvzl public-domain release | Compression spring supports mass from below; independently check intended equilibrium/regime and drawing conventions. |
| `images/incline_block.png` | [Block down wooden incline](https://commons.wikimedia.org/wiki/File:21-D-C12-S9-JK-1201-block-down-wooden-incline.png), Brina Schenk with UBC and Douglas College; downloaded from the [publisher repository](https://github.com/ubc-mech2/OER-mechanics-webwork/blob/master/Images/21-D-C12-S9-JK-1201-block-down-wooden-incline.png) | CC BY 4.0 | Artistic depth/texture; manual source geometry and masks required. Keep attribution badge. |
| `images/incline_pulley.png` | [Incline with hanging mass](https://commons.wikimedia.org/wiki/File:21-D-C12-S9-JK-1203-block-on-incline-with-hanging-mass.png), Brina Schenk with UBC and Douglas College; downloaded from the [publisher repository](https://github.com/ubc-mech2/OER-mechanics-webwork/blob/master/Images/21-D-C12-S9-JK-1203-block-on-incline-with-hanging-mass.png) | CC BY 4.0 | Shares the preceding source group; manually review rope tangency, attachments and physical regime. |
| `images/projectile_fixed.png` | [Projectile motion fixed.svg](https://commons.wikimedia.org/wiki/File:Projectile_motion_fixed.svg), Maxmath12 | CC0 1.0 | Spatial axes x/y and multiple time-position markers; a person must distinguish one moving body from its ghost positions. |
| `images/pendulum.png` | [Simple gravity pendulum.svg](https://commons.wikimedia.org/wiki/File:Simple_gravity_pendulum.svg), Chetvorno | Author public-domain release | Reused M3 manual-QA source. Reserve from independent gold; it has already informed workspace QA. |
| `images/projectile.png` | [Projectile motion.svg](https://commons.wikimedia.org/wiki/File:Projectile_motion.svg), Maxmath12 | CC0 1.0 | **Quarantined:** its horizontal axis says Time while its description claims a spatial projectile path. Use the fixed version above; do not silently relabel this source as valid gold/training. |

The original Commons downloads for incline, collision, table-pulley and another
incline-pulley returned HTTP 429. No repeated rate-limit bypass was attempted.
The two UBC originals were obtained from the actual publisher's repository
instead. GitHub's connector supplied file metadata; its fetch tool excludes
binary transfers, so the PNG originals were downloaded directly. Download URLs,
errors, authors, provisional groups and original/PNG hashes are in the local
JSON manifests. A [free-body diagram candidate](https://commons.wikimedia.org/wiki/File:Free_Body_Diagram.JPG)
was excluded because its source explicitly flags disputed accuracy.

The initial Python rendering attempt found no Python Playwright installation;
the existing Node Playwright/Edge installation rendered the SVGs instead. No
dependency was installed or pin changed. The actual starter contact sheet and
the corrected projectile PNG were opened for visual inspection. This catches
obvious source issues; it does not constitute independent HUMAN gold review.

## Exact local image hashes

| Candidate | PNG SHA-256 |
| --- | --- |
| atwood | `60b76987dbf347aa04827b308eba79d6978367a373456bfd80193918d8948ece` |
| spring_mass | `9329dab3eeb5b475473cf8f22e1a75cdfb0b808cb97e1c29bcdef53c7f425cb7` |
| incline_block | `1cfa28bad22b1ab9872afec9aedfc332959d5020cb5f76e915d56549f236c6cf` |
| incline_pulley | `28a23e3995ab86255d6e09a3bdcaeb43ac9a915ff3605fabd04893b64332af01` |
| projectile_fixed | `f20b2ff4cb97504167a72d28b68d9b81dc0a6a93ddeefd53ddfa31e5c25052da` |
| pendulum, prior QA | `1496aa14f232b0e6f0c066ff986d28ab356d8e30312ede4fad5959c8f3e648d7` |
| projectile, quarantined | `027a0ffd059fd2729748c51e12e6c56f49fec0409ad261883c2e970217595d83` |

## Existing annotated datasets checked

This targeted search did not establish a ready-to-import independently reviewed
gold dataset in this app's 21-class/physical-scene schema. This is a finding from
the sources examined, not a claim that no related dataset exists.

- [AI2D-RST, authors' repository](https://github.com/thiippal/AI2D-RST) describes
  1000 primary-school science diagrams with expert grouping/connectivity/discourse
  annotations, and states CC BY 4.0 for that corpus. Its element types and relation
  graphs differ from mechanics objects, SI Values, calibrated geometry and
  attachment/trajectory truth. The underlying image rights also need review;
  the annotation licence does not settle every source-image right. Not imported.
- [PhysScene, authors' repository](https://github.com/ZMH-SDUST/PhysScene) concerns
  experimental instruments/setups and functional relationships; its stated
  licence is CC BY-NC 4.0. This is not the project's eight diagram archetypes or
  v1 physical scene contract. No class mapping was guessed and no data imported.
- [OpenStax University Physics, current publisher licence](https://openstax.org/books/university-physics-volume-1/pages/preface)
  is another diagram source, currently stating CC BY-NC-SA 4.0. Do not assume old
  CC BY notices describe the current edition. No book or figure was downloaded
  into this starter pack or a dataset.

No verified real handwritten starter set was found/prepared in this small search.
The collection is far below the frozen 20 printed / 20 handwritten requirement,
and the candidate pool is still separate from reviewed training data. HUMAN
review, collection/source separation and licence decisions remain necessary.
Real metrics stay null; full/GPU training and M5 are not started.
