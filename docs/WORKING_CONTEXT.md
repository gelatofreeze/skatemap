# Frutiger Air: working context for handover

Written 13 Nov 2026 at the end of the cloud session, for continuing in the
local Claude conversation "Frutiger Air skate map setup". Everything here
describes the state at commit `d508d59` on branch
`claude/beautiful-curie-srnd7y` of `gelatofreeze/skatemap`.

**Read this first, then `README.md`, then `docs/RESEARCH_REPORT.md`.**

Status in one line: the map is fully generated and passes its own
collision checks, but **has never been loaded in the game**. Nothing about
how it rides, looks or builds in ReSkate Studio is confirmed.

---

## 1. What the user asked for, in their words

Original brief (11 Nov):
- A map for the new EA *skate.*, for the modded version (ReSkate).
- "Lots of mega ramps, medium ramps, small ramps, street spots."
- Ramps "colorful and abstract". The park should "flow in a way that just
  makes sense and works".
- "A disgustingly over the top Frutiger Aero aesthetic." Park name:
  **Frutiger Air**. "Dive deep into what constitutes that viral aesthetic."
  "A futuristic utopia in HD." "I want to be absolutely blown away."

Added during planning:
- Island mood from early Kingdom Hearts: "tropical beautiful Frutiger Aero
  paradise in HD high poly". (Mood only; the island must be original.)
- "If it's easy why not a day and night cycle."
- "I need you to do all of this for me wherever possible." The user is not
  technical and did not have Blender or ReSkate Studio installed.

Second-pass requests (12 Nov), with a reference image (retro Windows
window with pool water and a rubber duck, goldfish, glass atrium aquarium,
glossy media player, CD, bubbles, palms):
- "The big fish tank needs realistic clown fish."
- "Way more skate features and ramps."
- "Long megaramp highway with pump opportunities and jumps that then
  U-turns downhill back to the island."
- "The middle tower can be taller, hollow, that functions as an 85° or so
  steep drop in and has an output at the bottom that launches you, you're
  caught by a ramp that takes you back to the island."
- "I want a second island." "Less wasted space." "More realism" (twice).
- "Guaranteed flawless collision, no ability for invisible things to knock
  you off your board."
- "Way heavier Frutiger Aero elements."
- "Old Windows interface looking things that are skateable, a billboard
  with an old MS Paint interface for instance."
- "Make it a true utopia for Frutiger Aero."

Later asks:
- "Find the game's physics and calc landings on that too."
- "Can the game handle a script that tells a billboard to play a
  web-hosted video?" (Answer: no. See section 6.)
- A deep-research prompt "designed for a Claude" on maximising the map,
  which the user then handed back to be run.
- "Please install it for me, use my PC if needed." (Not possible from the
  cloud session. See section 9.)

### Pending intent, NOT executed

The user had an unsent draft: **"do all of it"**. It answers the last
question the cloud session asked: which of the five not-done items to do
next. Treat it as the user's likely next instruction, and confirm before
starting. The five items are listed in section 8 under "Pending".
The migration request said explicitly: do not implement new map features
during migration.

---

## 2. Decisions and why

| Decision | Choice | Why |
|---|---|---|
| Setting | Lagoon eco-city on one island (user picked over sky archipelago and biodome) | User's choice |
| Size | About 400 m main island | User's choice ("District") |
| Skate feel | Hybrid: real proportions for street and small ramps, physics-defying megas | User's choice |
| Time of day | Design for both; noon first | ReSkate has its own morning/noon/evening/night switch in its world menu; nothing in the map sets it |
| Pipeline | Python generator on headless Blender (`bpy`) writes a `.blend`; ReSkate Studio compiles it | Studio accepts `.blend`, `.fbx`, `.glb`. Code makes every ramp a number that can be re-tuned after testing |
| Preview | three.js page published as a Claude artifact | Lets the user see the map without the game. Artifacts cannot host `.glb`, so models are packed as base64 inside JSON |
| Object naming | `SK_` skate, `GR_` rails, `SC_` solid scenery, `NC_` no collision, `OP_` optional | Collision and surfaces are set per object in Studio's Map view; prefixes make that quick |
| Retro windows | Generic paint program, dialogs and player; no Microsoft names, logos or artwork | Avoid copying real branded UI |
| Island mood | Colour and atmosphere of early-2000s tropical adventure games only | Do not recreate a specific game's island |
| Aurora | In an `OP_` object, visible only at night in the preview | Risk that translucent sheets look wrong in game |
| Second island | "Desktop Cay", east at (430, 60), reached by a causeway and circled by the highway | Gives the highway something to U-turn around and a home for the retro-desktop set |
| Drain exit direction | 244° (south-south-west) | Only clear corridor between Bliss Drop (225°) and the minis (270°) |
| Highway direction | Leaves the crown at 22° | Clear corridor between the plaza and the gardens |
| Physics constants | In-air gravity 11.0 m/s², energy kept 0.62 | Gravity measured by the ReSkate Trainer authors; energy inferred from one play-tested map. Both replaceable by `tools/calibrate.py` |
| Coping | Visual only, sunk flush | A released map found protruding coping trips the board |
| Decals | Separate `NC_decals` objects | Avoid 1 cm lips on ride surfaces |

Coordinates: metres, x east, y north, z up. Angles are degrees
anticlockwise from east. The main island is centred on the origin.

---

## 3. Chronology

11 Nov
1. Research: confirmed ReSkate is the mod platform and maps are built in
   Blender and compiled with ReSkate Studio. Wrote `BRIEF.md`.
2. User chose lagoon eco-city, about 400 m, hybrid feel.
3. Created the `skatemap` cloud environment allowing `docs.reskate.dev`
   and `re-skate.wiki`. (The first approval prompt was declined by
   accident and re-sent.)
4. Read the ReSkate docs. Wrote the generator (`frutiger/mesh.py`,
   `terrain.py`, `mega.py`, `skate.py`, `scenery.py`, `layout.py`,
   `export.py`, `build.py`) and the viewer. First full build, published
   the preview, committed `5645615` and `3cdf648`.

12 to 13 Nov
5. User's second-pass requests plus reference image. Allowed the image
   host and viewed it.
6. Wrote `tools/textures.html` and rendered 13 textures with headless
   Chromium into `frutiger/textures/`.
7. User asked about physics, video billboards, and a research prompt.
   Read more ReSkate docs. Wrote the telemetry plugin,
   `frutiger/physics.json`, `tools/calibrate.py`, and
   `docs/RESEARCH_PROMPT.md`. Commit `d6c6790`.
8. Built the second pass in `frutiger/v2.py`: hollow Spire, the Drain,
   the highway, Desktop Cay, spot scatter, clownfish tank, ducks, lamps,
   rainbow. Added `tools/validate.py` and fixed everything it flagged.
   Commit `f75f726`.
9. User asked to install on their PC. The PC ("G") was visible but did
   not offer its folders to cloud sessions. A local-install task card was
   queued instead.
10. User handed back the research prompt. Ran the research, wrote
    `docs/RESEARCH_REPORT.md`, applied measured gravity, flush coping,
    4 mm junctions and two tighter bowls. Commit `d508d59`. Republished
    the preview (version 3).
11. This migration bundle.

---

## 4. What exists in the map

Main island, about 370 m across, coast radius about 185 m.

| Zone | Where | Contents |
|---|---|---|
| The Spire | origin | Hollow glass tower on 8 legs. Crown deck z = 85 (Empty `spawn`). Mid deck z = 45, an annulus at radius about 17 (Empty `spawn_mid`). Halo and orb above |
| The Drain | inside Spire, exits 244° | 85° drop from the crown opening, 24 m radius transition, out through the legs, viaduct to the shore, kicker at 22°, about a 76 m gap, catch ramp, 55 m radius banked U-turn (195°), return to the boardwalk at 268° |
| Highway | crown at 22°, round Desktop Cay, to the plaza beach | 1,040 m, 9 m wide, rainbow segments. Roller sections at s = 95 to 175, 330 to 400, 560 to 640, 790 to 850. Table-tops at s = 200, 232, 420, 452, 484, 670, 702 (8 m up, 7 m table, 10 m down, 1.9 m high). Banked from curvature |
| Bliss Drop | mid deck, 225° | Roll-in, about a 36 m gap, landing, 7.5 m quarter |
| Aurora Loop | mid deck, 135° | Roll-in, full loop (13 m and 6.5 m radii), about a 38 m gap through three rings, landing on the beach, quarter |
| Splash | mid deck, 90° | Long runway to the shore, about a 37 m gap over water to a floating pad, quarter, "reef walk" bridge back to the boardwalk at 58° |
| Aqueduct | mid deck, 315° | Roll-in morphing into a U-channel then a glass full-pipe (4 m radius) through the clownfish aquarium, then a snake run to the boardwalk near 288° |
| Aero Plaza | east, x = 56 to 172, y = ±36 | Four terraces joined by 12, 8, 5 and 3 stair sets; banks, quarters, hubbas, rails, globe fountain, funbox, water gap, curved ledges, one long rail |
| Bubble Bowls | centre (-96, 10), deck z = 4.4, radius 40 | Four bowls (1.2 to 3.0 m deep), 4 m vert ramp with waterfall wall, spine, quarter, six kit spots |
| Dewdrop Minis | centre (5, -100), deck z = 3.5, radius 38 | Two mini ramps, spine, pyramid, four quarters, bumps, pump track, five kit spots |
| Gardens | centre (76, 76), z = 3.2 | Pool with lily-pad pads, ducks, goldfish, crescent waterfall wall, three domes, three pod towers |
| Ring path | radius 52 | 6 m wide loop, four hill runs to the Spire plaza, eight pocket spots |
| Boardwalk | coast minus 22 m | 9 m wide ring, grindable seawall, a street spot about every 20 m on the inner lane, orb lamps |
| Islet | (-236, -72) | Rope bridge, deck, volcano bump, giant duck |
| Desktop Cay | (430, 60), deck radius 39, z = 2.6 | Three window wallrides, taskbar ledge, cascading error-dialog ledges, media-player quarter, CD pads, cursor kickers, progress-bar pads, mini ramp, quarter, funbox, glass atrium with goldfish, shore walk |
| Causeway | boardwalk at 6° to Desktop Cay | 6 m wide with grindable side walls, rainbow arch |

Scenery: about 215 palms, rocks, bushes, bubbles, seven wind turbines,
sailboats, dolphins, aurora ribbons (optional).

---

## 5. Architecture and how to build

```
BRIEF.md                    design brief (first-pass; partly superseded by this file)
README.md                   how to get the map into the game; layout; collision rules
build.py                    entry point
frutiger/
  mesh.py                   Scene collector and primitives (grid, lathe, sweep, tube...)
  terrain.py                heightfield, both islands, pads, texture
  mega.py                   Prof (side-profile turtle with energy and gap maths), ribbon, pylons
  skate.py                  quarter, halfpipe, spine, bank, bowl, stairs, rail, ledge...
  scenery.py                palm, rock, dome, tower, turbine, torus, boat, dolphin
  layout.py                 first-pass zones and build() which assembles everything
  v2.py                     Spire, Drain, highway, Desktop Cay, spots, fish, ducks, lamps
  export.py                 materials, Blender scene, weld, .blend and .glb export
  physics.json              gravity and energy retention used for gap sizing
  textures/*.png            13 rendered textures
tools/
  textures.html             source artwork for the textures
  render_textures.js        renders it with Playwright/Chromium
  validate.py               collision checks
  calibrate.py              refits physics.json from telemetry.json
plugin/frutiger-air-telemetry/   ReSkate plugin (Luau) that logs jumps. Untested
viewer/index.html           three.js preview (published as an artifact)
viewer/assets/*.json        generated preview models (git-ignored; included in the bundle)
dist/FrutigerAir.blend      the map for ReSkate Studio (35.6 MB)
docs/RESEARCH_PROMPT.md     the research brief
docs/RESEARCH_REPORT.md     the research results
docs/WORKING_CONTEXT.md     this file
```

Build:

```
pip install bpy numpy scipy mapbox-earcut pillow
python tools/validate.py        # must print "all checks passed"
python build.py                 # dist/FrutigerAir.blend + viewer/assets
python build.py --preview       # viewer assets only
node tools/render_textures.js   # only if tools/textures.html changed; needs playwright
```

Built and tested with Python 3.13, `bpy` 5.3.0, numpy 2.5, scipy 1.18 on
Linux. Not run on Windows. `bpy` wheels are tied to specific Python
versions; if `pip install bpy` fails locally, match the Python version
the wheel needs. A full build takes about 40 seconds and peaks under
4 GB of memory.

How the generator is organised:
- Pieces are authored in local space and placed with `S.push(pos, yaw)`
  / `S.pop()`.
- Zones register terrain pads. `Terrain.height()` applies, in order:
  deck pads, path pads, deck cores again, then digs. Terrain sits 0.35 m
  below slabs (`CLEAR`).
- Mega lines are side profiles (`Prof`) with energy-based speed; `gap()`
  places a landing tangent to the flight path.
- Work that needs the finished terrain (pylons, domes) goes in `W.late`.
- `W.keepout` holds paths scenery must avoid; `W.wall_gaps` opens the
  seawall where bridges leave.

Preview: https://claude.ai/artifact/FigRSBbse9RvevMEMqZFek (version 3).
To view locally, serve `viewer/` over HTTP. It loads three.js from
jsDelivr.

---

## 6. Research findings that drive the design

Full detail and links are in `docs/RESEARCH_REPORT.md`. The ones that
matter most:

From the ReSkate docs (docs.reskate.dev):
- Studio builds maps from `.blend`, `.fbx`, `.glb`. Collision, surfaces,
  grinds, lights and spawn are set in its Map view. BUILD & INSTALL
  writes `Mods\<map ID>`. Studio is Windows-only and is distributed in
  the ReSkate Discord.
- Time of day is a game setting (morning, noon, afternoon, evening,
  night), not a map property.
- Plugins are Luau. They can read telemetry, draw PNG/JPG in the world,
  play WAV, route the player's music to a placed speaker, and make HTTPS
  requests up to 1 MB. **No video.** A map package that also holds a
  plugin cannot be downloaded in a multiplayer session.
- Physics tuning values are readable by plugins
  (`reskate.physics.find`), not published.

From the ReSkate Trainer README:
- In-air gravity is about 11 m/s² (half gravity fell at 5.5, 1.5x at
  15.8). Stock ollie 0.36 m, 0.58 s.
- The trainer has a jump read-out and CSV telemetry, and reads a
  map-shipped `trainer.json` with named spots and recommended tuning.

From Porterino (a map-checking add-on) and SkateTanic (a released map):
- Steps of 3.5 cm and up at ramp feet can stop the skater; a 2 cm floor
  step had to be fixed.
- Protruding coping trips the board.
- Lips under 75° launch outward, not up. Facets should turn 14° or less.
- Grinds are curve objects: 10° or less per point, 0.45 m or less per
  segment on bowls.
- **Emission does not render.** Use area lights 30 cm in front of a
  bright panel; lights need `sk8_light_range` and `sk8_light_tod`.
- Anything hidden from render is dropped from the build, collision too.
- A glass material stopped a build until it was changed to a "surface"
  type.
- Empties named `spawn`, `start` or `playerstart` are read as the start.
- A working mega ramp: 22 m roll-in at 48°, 6 m kicker with a 28° lip,
  12 m gap, 21° landing. A working vert ramp: 3.84 m deck, 0.41 m vert.
- A shipped map runs at 2.46 million triangles, 520,000 collision
  triangles.

Not found: any published top speed; Reddit and Discord were unreachable;
the Consumer Aesthetics Research Institute's own text.

---

## 7. Test results

| Check | Result |
|---|---|
| `tools/validate.py` at `d508d59` | "all checks passed" (terrain below every upward skate face by 2 cm or more; no palm trunk, rock or lamp inside the space above a skate surface) |
| Full build | Succeeds. 35.6 MB `.blend`. About 370 mesh objects, roughly 270 grind reference curves |
| Preview, local headless Chromium | Loads and renders all views. Checked by screenshot: island overview, Spire, Drain U-turn, highway, Desktop Cay, tank, plaza, bowls, minis, gardens, megas, night |
| Published artifact page | Published three times; **not opened or verified by me** |
| ReSkate Studio import | **Never attempted** |
| In game | **Never loaded** |
| Telemetry plugin | **Never run** (written from the docs) |
| `tools/calibrate.py` | **Never run on real data** |
| Windows build of the generator | **Never run** |

Gap sizes at this commit: Bliss Drop 35.5 m, Aurora Loop 37.7 m,
Splash 37.3 m, Drain 75.6 m (lip speed about 32 m/s by the model).

---

## 8. Implemented, pending, known problems

Implemented: everything in section 4, the validator, the textures, the
plugin, the calibration script, the research report, and the fixes from
it (gravity, flush coping, 4 mm junctions, two tighter bowls).

Pending (the five items the "do all of it" draft refers to):
1. **Glow**: `glow_*`, `chrome_glow`, `aurora_*`, `orb`, `water_fall` and
   the rainbow use emission, which the game ignores. Add area lights with
   `sk8_light_range` and `sk8_light_tod`, and brighten base colours.
2. **Glass**: `glass_blue`, `glass_frost`, `glass_pipe`, `tank_water`,
   `bubble`, `water` are alpha-blended Principled materials. One may stop
   the Studio build. Test one first; find what Studio's "surface" glass
   means.
3. **Mini-ramp and quarter lips** under 75°: minis quarters (1.0/2.0,
   1.4/2.4, 1.8/2.8, 1.2/2.2 height/radius), plaza transitions, spot-kit
   pieces. Left at real-park proportions.
4. **`trainer.json`** with teleport spots for each line start. Blocked on
   the coordinate order (the README example is ambiguous between game and
   Blender axes).
5. **The 42-spot list** in the research report. None built.

Also not done:
- Main island still has large lawns ("less wasted space" only addressed
  on Desktop Cay and along paths).
- "More realism": only planks, pavers and caustic water are textured.
  Palms, sand and grass are stylised.
- Grind reference curves are plain Blender curves; they are not tagged
  with whatever property Studio's Skate Map add-on uses.
- No loading-screen image (`assets/<scene>/load_screen.png`); Studio will
  show a checkerboard.
- No Thunderstore package (`manifest.json`, `icon.png`).
- Stairs are stepped collision; the research says skateable stairs should
  be an invisible ramp with the game's "stairs" behaviour.
- `BRIEF.md` describes the first pass and is out of date on the Spire.

Known problems and risks:
- Every gap length is a model estimate.
- Whether the skater holds an 85° drop, a full loop, or the top of a
  full pipe is unknown.
- The plaza beach slab sits 4 mm under the boardwalk where they overlap;
  possible z-fighting.
- `viewer/assets/terrain.json` is 14.6 MB and `palms2.json` 13.5 MB,
  close to the artifact host's 16 MB per-file limit.
- The second spawn name `spawn_mid` may or may not be picked up as a
  start point.
- `frutiger/v2.py` `island2()` has a leftover empty `S.push`/`S.pop`
  pair and `pool_life()` places one duck by a hard-coded plaza height.
  Harmless, untidy.
- `frutiger/skate.py` `bank()` has an unused `round_top` parameter.

Assumptions still in force: ReSkate Studio will accept a Blender 5.3
`.blend` (the community reports using 5.2); object-name prefixes are
only a convention for the person tagging; double-sided materials are
honoured; the game's sun lights the map.

---

## 9. Exact next steps

On the PC (needs the user):
1. Get the latest files (section 10).
2. Install Blender. Get ReSkate Studio from the ReSkate Discord.
3. In Studio: Settings, set the Blender path, install the Skate Map
   add-on. Add the map from `dist/FrutigerAir.blend`. BUILD & INSTALL.
4. Record what happens: build errors (especially glass), whether the
   spawn works, scale beside a ledge, each mega gap, the Drain, the loop,
   how glass and water look, whether grinds register.
5. Use the ReSkate Trainer's jump read-out or the telemetry plugin to get
   takeoff speeds; run `tools/calibrate.py`.

In the generator (after confirming the "do all of it" intent):
1. Lights for glow (pending 1).
2. Glass material fix once the build error, if any, is known (pending 2).
3. Lip angles (pending 3).
4. `trainer.json` (pending 4), once the axis order is confirmed.
5. Spot list (pending 5) and main-island density.

Open in the Skate Map add-on, once installed, and look at what custom
properties it writes for collision, surface and grinds. If they are plain
object properties, `frutiger/export.py` can write them and remove most of
the manual tagging.

---

## 10. Getting this onto the PC

The local folder `C:\Users\kablo\Documents\skatemap` is older. Two ways
to update it:

- **Git** (tracked files only; `viewer/assets` is regenerated by a build):
  `git fetch origin` then
  `git checkout claude/beautiful-curie-srnd7y` and `git pull`.
- **The ZIP**: unzip and copy the `skatemap` folder's contents over the
  local folder. It includes `viewer/assets` and `dist`.

A task card titled "Install Frutiger Air map tools on this PC" was queued
in the cloud session (task id `task_8329ca8c`). It may still be showing.

## 11. About the transcript

The bundle's `transcript/` folder holds the cloud session's own log file
(`session.jsonl`, the complete raw record from 11 Nov 19:19 UTC to the
moment of export, with no compaction summaries in it) and a readable
extract (`transcript.md`) of the user's and assistant's messages with
tool calls reduced to one line each. Tool outputs are in the raw file
only.
