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

- **Spawn**: an Empty named `spawn` sits on top of the tower.
- **Grinds**: the collection *Grind lines (reference curves)* holds 173
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
pip install bpy numpy scipy
python3 build.py            # dist/FrutigerAir.blend and the preview files
python3 build.py --preview  # preview files only
```

To view the preview locally, serve `viewer/` over HTTP and open
`index.html`.

## Layout

| Zone | Where | What |
|---|---|---|
| The Spire | centre | Spawn deck at 45 m; all four mega lines start here |
| Bliss Drop | south-west | Roll-in, 40 m gap, landing, 7.5 m quarter |
| Aurora Loop | north-west | Roll-in, full loop, 42 m gap through three rings over the boardwalk |
| Splash | north | Long runway, 42 m gap over water to a floating pad |
| Aqueduct | south-east | Roll-in into a glass full-pipe through an aquarium, then a snake run to the shore |
| Aero Plaza | east | Four terraces: 12, 8, 5 and 3 stair sets, hubbas, rails, banks, ledges, water gap |
| Bubble Bowls | west | Four bowls 1.2 to 3 m deep, 4 m vert ramp |
| Dewdrop Minis | south | Mini ramps, spine, pyramid, pump track, quarters |
| Gardens | north-east | Pool with lily-pad manual pads, domes, towers |
| Boardwalk | shore | Ring around the island with a grindable seawall |
