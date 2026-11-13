# Frutiger Air

A custom map for EA's *skate.* (2025), built for ReSkate. A 400 m tropical
island in an aqua lagoon: a glass tower in the middle, four mega ramps
running from its top down to the sea, bowls, mini ramps, a terraced street
plaza and a boardwalk around the whole shore.

`BRIEF.md` has the design brief. This file is how to use what is built.

## What is here

| Path | What it is |
|---|---|
| `dist/FrutigerAir.blend` | The map, as a Blender scene. This is the file ReSkate Studio builds from. |
| `frutiger/`, `build.py` | The generator. Every ramp is code, so changing a size is changing a number. |
| `viewer/` | Browser fly-through of the map, for looking at it without the game. |

## Getting it into the game (Windows PC)

Not yet tested end to end. The map has never been loaded in game, so
expect the first try to turn up things to fix.

1. Install **Blender** (free, blender.org).
2. Get **ReSkate Studio** from the ReSkate Discord and install it.
3. In Studio, open **Settings**, point it at `blender.exe`, and install the
   **Skate Map** add-on from there.
4. Download `dist/FrutigerAir.blend` from this repository.
5. In Studio: **+** beside **Maps** (or **Create > Map from a Blender
   scene**) and pick `FrutigerAir.blend`.
6. In **Map view**, check collision, surfaces, grinds and the spawn (notes
   below), then press **BUILD & INSTALL**.
7. Start ReSkate. The map is under **CUSTOM MAPS**.

### What the object names mean

Objects are sorted into collections and prefixed so tagging is quick:

| Prefix | Meaning | Collision |
|---|---|---|
| `SK_` | Skate surface: ramps, decks, ledges, stairs | Yes, smooth/concrete |
| `GR_` | Rails and coping | Yes, grindable |
| `SC_` | Solid scenery: terrain, pylons, buildings, palm trunks | Yes |
| `NC_` | Decoration: water, bubbles, palm fronds, fish, boats | No |
| `OP_` | Optional: aurora ribbons. Delete if they look wrong in game. | No |

- **Spawn**: Empties named `spawn` (crown of the tower) and `spawn_mid` (mid deck).
- **Grinds**: the collection *Grind lines (reference curves)* holds about 270
  curves tracing every rail, coping and ledge edge. If Studio can take
  grinds from curves, use those; otherwise they show where each grind goes.
- **Time of day**: the game's own morning / noon / evening / night setting
  is switched from the ReSkate world menu. Nothing in the map file sets it.

### Things to report back after the first test

- Does the skater look the right size next to a ledge and a stair set?
- Do the mega-ramp gaps land? Each landing was sized from an energy
  estimate, not from the game's physics.
- Do glass and water show as see-through?
- Does the loop work at all?

## Rebuilding

```
pip install bpy numpy scipy mapbox-earcut
python3 build.py            # dist/FrutigerAir.blend and the preview files
python3 build.py --preview  # preview files only
```

To view the preview locally, serve `viewer/` over HTTP and open
`index.html`.

## Layout

| Zone | Where | What |
|---|---|---|
| The Spire | centre | Hollow glass tower. Crown deck at 85 m (spawn), mid deck at 45 m (`spawn_mid`) |
| The Drain | inside the Spire, exits south-west | 85 degree drop down the shaft, out through the base, viaduct to the shore, about an 85 m launch over the lagoon, catch ramp, banked U-turn back to the boardwalk |
| Highway | crown to second island and back | 1,040 m rainbow ramp: four roller sections, seven table-top jumps, banked turn round Desktop Cay, ends on the plaza beach |
| Desktop Cay | second island, east | Program-window wallrides, taskbar ledge, cascading error dialogs as stacked ledges, CD manual pads, cursor kickers, media-player quarter pipe, glass atrium with goldfish |
| Bliss Drop | south-west, mid deck | Roll-in, 40 m gap, landing, 7.5 m quarter |
| Aurora Loop | north-west, mid deck | Roll-in, full loop, 42 m gap through three rings |
| Splash | north, mid deck | Long runway, 42 m gap over water to a floating pad |
| Aqueduct | south-east, mid deck | Glass full-pipe through a clownfish aquarium, then a snake run |
| Aero Plaza | east | Four terraces: 12, 8, 5 and 3 stair sets, hubbas, rails, banks, ledges |
| Bubble Bowls | west | Four bowls 1.2 to 3 m deep, 4 m vert ramp, extra street spots |
| Dewdrop Minis | south | Mini ramps, spine, pyramid, pump track, quarters |
| Gardens | north-east | Pool with lily-pad manual pads, ducks and goldfish |
| Boardwalk | shore | Ring with a grindable seawall and a street spot roughly every 20 m |
| Causeway | east | Skateable bridge to Desktop Cay, under a rainbow |

## Collision rules the generator follows

`python3 tools/validate.py` checks these on every build and currently passes.
It cannot prove the map is flawless in game; only a play-test can.

- Terrain is kept at least 35 cm below every skate surface, and is
  re-flattened under each deck after paths are cut.
- Painted lines and inlays are separate `NC_decals` objects with no
  collision, so there are no 1 cm lips.
- Skate meshes are welded, and bowl decks are triangulated to meet the
  bowl aprons vertex for vertex.
- Coping is visual only and sunk flush; the lip is the smooth ramp edge. Paths meet decks within 4 mm.
- Palms, rocks and lamps are kept out of the space above skate surfaces.
- Bubbles, rings, fish, fronds, water and rainbows have no collision.

## Measuring the game's physics

`plugin/frutiger-air-telemetry` is a ReSkate plugin that logs every jump.
Copy it to `Mods`, skate, type `fa save`, and send back `telemetry.json`.
`python3 tools/calibrate.py telemetry.json` then refits gravity and speed
loss, and the next build re-sizes every gap. Until then gap lengths are
estimates. They currently use 11 m/s2 in-air gravity (measured by the
ReSkate Trainer's authors) and an energy figure inferred from one
play-tested map. The ReSkate Trainer's own jump read-out and CSV telemetry
(MAP & HUD tab) give the same numbers without this plugin.

`docs/RESEARCH_REPORT.md` has the research behind these choices. Two things
from it are not yet handled: glow materials will not glow in game (emission
is ignored, real lights are needed), and glass may need a material change
to build.
