# Frutiger Air — project brief

A custom map for EA's *skate.* (2025), delivered as a ReSkate mod.
Status: **planning**. Nothing is built yet.

## 1. The pitch

A 400 m tropical island in an aqua lagoon, built as a 2007 vision of the
future: white swooping eco-architecture, glass domes, wind turbines, koi
pools and lawns so green they look rendered. A glass tower stands in the
middle. Every mega ramp starts at the top of it and runs downhill to the
sea, and everything on the way down is skateable.

Decisions already made:

| Decision | Choice |
|---|---|
| Name | Frutiger Air |
| Setting | Lagoon eco-city (single island) |
| Size | District, about 400 m across |
| Skate feel | Hybrid: real proportions for street and small/medium ramps, physics-defying mega ramps |
| Ramp look | Colourful, abstract, glossy |

## 2. What Frutiger Aero actually is

The look of consumer tech from roughly 2004 to 2013: Windows Vista and 7
(Aero), Mac OS X Aqua, the Wii menu, MSN, Sony Ericsson and Nokia
packaging, stock-photo corporate optimism. It was named retroactively
(after the Frutiger typeface plus Windows Aero) and went viral as
nostalgia for a future that felt clean, friendly and solvable.

What makes an image read as Frutiger Aero, in order of importance:

1. **Gloss and glass.** Everything looks wet, gel-coated or made of
   glass. Hard specular highlight across the top half of every object,
   soft glow at the bottom, a mirrored reflection underneath.
2. **Sky and water.** Saturated blue sky with fluffy clouds, aqua water,
   droplets, splashes, bubbles, lens flare, bokeh.
3. **Hyper-real nature.** Macro grass, lily pads, palm fronds, tropical
   fish, dolphins, butterflies, rolling Bliss-wallpaper hills.
4. **Optimistic technology.** White curvy buildings, wind turbines, solar
   petals, monorails, globes, floating orbs. Tech and nature in harmony.
5. **Light as ornament.** Aurora ribbons, swooshes, light streaks, rings.
6. **Humanist type and round icons.** Frutiger / Segoe-style lettering,
   glossy circular buttons, skeuomorphic detail.

Palette: cyan `#00AEEF`, sky `#7FD4FF`, aqua `#19E3D0`, lime `#8DC63F`,
grass `#3FB618`, white, brushed silver. Accent gels for ramps: tangerine
`#FF8A00`, sun yellow `#FFD400`, magenta `#FF2D95`, violet `#7A4DFF`.

"Disgustingly over the top" means stacking all six at once, everywhere.

## 3. How that becomes a skatepark

| Aesthetic element | In the map |
|---|---|
| Glossy gel buttons | Ramps are translucent candy-coloured gel slabs with white rims; each line has its own colour so you can read it from the tower |
| Aero glass | Glass full-pipes, glass bridges, frosted-glass ledges with glowing edges |
| Bubbles | Bowls shaped as bubble clusters; giant floating bubbles as gap targets |
| Water | Fountain gaps, a waterfall behind the vert wall, a full-pipe through an aquarium |
| Bliss hills | Grass rollers and pump bumps that are actually skateable |
| Aurora and swooshes | Rails and grind ribbons that arc through the air and glow |
| Globes and orbs | Rideable sphere and half-sphere obstacles, a rotating Earth sculpture at the plaza |
| Eco-tech | Wind-turbine blades as kickers, solar petals as wallrides, a monorail beam as the longest grind on the map |

## 4. Layout and flow

Gravity does the work. The tower is the high point; lines radiate
downhill; the shoreline boardwalk is a ring that collects every run-out
and feeds the next zone. Two uphill spiral ramps and the monorail grind
get you back to the middle without a teleport.

```
                 N
         [Splash Pier]         mega launch into the lagoon
              |
  [Bubble Bowls]--(Spire)--[Aero Plaza]     W: medium / E: street
              |      \
       [Dewdrop Minis] [Aqueduct]           S: small / SE: full-pipe
   ~~~~~~~~ boardwalk ring all the way round ~~~~~~~~
```

**The Spire (hub, +45 m).** Spawn on a glass disc at the top. Four
mega lines leave from here:

- **Bliss Drop** (lime): 40 m roll-in, 25 m gap, 8 m quarter. The
  classic MegaRamp, scaled up.
- **Aurora Loop** (violet to magenta): roll-in, full loop, corkscrew
  gap over the lagoon to a floating landing pad.
- **Aqueduct** (cyan glass): full-pipe through the aquarium, opening
  into a long downhill snake run.
- **Splash** (tangerine): pier launch across open water onto a chain
  of floating pads.

**Bubble Bowls (medium, west).** Cloverleaf bowls 2 to 3.5 m deep, a
4 m vert halfpipe with the waterfall behind it, hips, spines, a
snake run linking them.

**Dewdrop Minis (small, south).** Mini ramps 1 to 1.5 m, pump track
over grass rollers, pyramids, quarter-to-bank transfers. The learn-here
zone and the warm-up loop.

**Aero Plaza (street, east).** Stair sets (3, 5, 8, 12) with rails and
hubbas, marble and frosted-glass ledges, manual pads, planters, kinked
rails, fountain gap, glass-brick banks.

**Boardwalk (street, perimeter).** Long ledges, benches, curb cuts and
gaps over the water, running the full circumference.

Flow rules the layout has to pass:

- Every run-out points at another obstacle, never at a wall.
- From any spot you can reach all four zone types without pushing uphill
  more than once.
- Mega landings and street lines never cross at speed.
- Each zone has an obvious beginner line and a hard line.

## 5. How it gets built

ReSkate maps are authored in Blender and compiled with **ReSkate
Studio**, which accepts a `.blend`, `.fbx` or `.glb` scene. Collision,
surfaces, grinds, lights and the spawn are set in Studio's Map view, and
Studio publishes an `.fbmod` or Thunderstore package.

So the map is generated from code:

1. A Python generator (headless Blender, `bpy`) builds every piece
   parametrically: transitions with exact radii, bowls, rails, ledges,
   terrain, buildings. Changing a ramp is changing a number.
2. It writes `FrutigerAir.blend` and `FrutigerAir.glb`.
3. A browser fly-through (three.js) is built from the same file so the
   park can be reviewed without launching the game. I check it with
   screenshots as I go.
4. You open the `.blend` in ReSkate Studio on your PC, confirm tagging,
   and compile.

**Step 4 cannot be done from here.** Studio and the game are Windows
desktop apps; the final compile and in-game test are yours.

## 6. Phases

| # | Phase | Output | Needs you |
|---|---|---|---|
| 0 | Brief | This file | Sign-off |
| 1 | Pipeline spike | Generator skeleton plus a tiny test map: one quarter pipe, one ledge, one rail, one glass panel, spawn | Round-trip it through Studio and tell me what scale, materials and grinds look like in game |
| 2 | Greybox | Whole island blocked out untextured, web preview | Skate it, flow notes |
| 3 | Ramp and street detail | Final geometry for every obstacle | Skate it, feel notes |
| 4 | Art pass | Gel, glass, water, grass materials; buildings, bubbles, aurora, fish | Look notes |
| 5 | Polish and ship | Lighting, optimisation, README, package | Publish |

Phase 1 exists because of the unknowns below. It is small on purpose.

## 7. Risks and unknowns

- **Docs are unreachable from this session.** `docs.reskate.dev` and
  `re-skate.wiki` are outside the network allowlist. Until they are
  allowed, naming conventions and add-on properties are inferred from
  search snippets.
- **Materials.** How Studio translates glass, emission and gloss is
  unconfirmed. A community add-on (Glass-Reshader) exists specifically
  to work around Studio's glass handling, which suggests glass is not
  automatic. The art direction leans on it heavily.
- **Grind tagging.** May have to be done by hand in Map view. If the
  Skate Map add-on stores it as object properties, the generator can
  write them; unverified.
- **Scale.** Real-world proportions can feel small at *skate.*'s
  speeds. Expect a global scale factor after the phase 1 test.
- **Blender version.** The generator would use Blender 5.3; the
  community workflow is reported on 5.2. May need pinning.
- **Transitions.** Lips at seams and faceted curves ruin the ride.
  Curves get dense segments and all pieces are welded.
- **Size.** Community maps run from about 16 MB to over 1 GB. Target
  under 150 MB so it loads quickly.

## 8. Answers so far

- **Art direction.** Early-2000s tropical island adventure games are
  the mood reference: saturated teal shallows, warm pale sand, leaning
  palms, weathered timber piers and rope bridges, a waterfall pool,
  a small offshore islet reached by a bridge. This is inspiration for
  colour and atmosphere only; the island, its landmarks and layout are
  original. The Frutiger Aero tech layer (glass, gel, white
  architecture) sits on top of that paradise base.
- **High poly.** Dense curved geometry everywhere: smooth transitions,
  round palms and rocks, real 3D foliage on hero plants. Budget is set
  by the 150 MB target, not by a low-poly style.
- **Time of day.** Day/night cycle is wanted if cheap. Whether a custom
  ReSkate map can drive time of day is unknown without the docs. Plan:
  design every glowing element (rails, gel rims, aurora, underwater
  lights) so the map works in both, ship a noon build first, and add a
  cycle or a separate night variant once Studio's lighting options are
  seen first-hand.
- **Toolchain.** ReSkate is installed. Still needed on the PC before
  any in-game test: Blender (free, blender.org) and ReSkate Studio
  (distributed through the ReSkate Discord, not GitHub).
- **Docs access.** Declined for this session. Conventions will be
  confirmed from the phase 1 round-trip instead.
