# Frutiger Air research report

Answers the brief in `docs/RESEARCH_PROMPT.md`. Researched 13 Nov 2026 from
web search plus four primary sources read in full: the ReSkate docs, the
official ReSkate Trainer README, the Porterino map-checker docs, and the
SkateTanic map's build notes.

Confidence labels: **measured** (someone measured it in this game),
**sourced** (a credible published source), **consensus** (community
agreement, no measurement), **guess** (my inference).

What I could not get: any published top speed for the game, Reddit and
Discord threads (not reachable), and the Consumer Aesthetics Research
Institute's own text (only second-hand summaries).

---

## 1. Ten changes that would improve the map most

| # | Change | Why | Confidence |
|---|---|---|---|
| 1 | Make every coping flush. No tube standing proud at all. | SkateTanic's author found "the board tripped on the coping" with protruding tubes on bowls and ramps and fixed it with a smooth lip. Our coping stands 8 mm proud. | measured |
| 2 | Remove every step at a junction, including 2 to 3 cm ones. | Porterino flags steps of 3.5 cm and up as able to "catch the wheels and stop you dead". SkateTanic had to fix a 2 cm floor step. Our paths join decks 3 cm high. | measured |
| 3 | Shorten the mega gaps by about a quarter and use 11 m/s² in the air. | The trainer authors measured in-air gravity near 11 m/s². A released, play-tested mega ramp gets a 12 m gap from a 22 m roll-in at 48°, which implies the skater keeps roughly 60% of drop energy. We assumed 9.81 and 70%. | measured gravity, guess on energy |
| 4 | Do not rely on emission. Add real lights for anything meant to glow. | Confirmed in game: emission colour, strength and textures render as plain base colour. An area light 30 cm in front of a bright panel reads as glowing. Lights need `sk8_light_range` and `sk8_light_tod` properties. | measured |
| 5 | Ship a `trainer.json` with named teleport spots and recommended tuning. | The trainer shows a map's spots on its MAP tab. That solves "how do I get back to the top" for every line without geometry. | sourced |
| 6 | Make bowl and quarter lips at least 75° or accept that they launch outward. | Porterino reports under 75° as "you launch outward, not up". Four of our transitions are 60 to 70°. | measured threshold, still being ride-tested |
| 7 | Convert the grind reference curves to real grind curves: under 10° turn per point, segments 0.45 m or shorter on bowls. | Studio grinds are curve objects, and Porterino checks them to those limits. Our bowl copings are 120-point loops, which passes; long straight rails are fine. | sourced |
| 8 | Build the main island as a loop of chained lines, and cut lawn. | Skater XL's own team and a top community mapper both describe circular layouts that let lines chain without end as the thing that works. The clearest complaint about bad maps is "no design flow". | consensus |
| 9 | Treat glass as a build risk: test one glass object before trusting any. | SkateTanic's build stopped on a lamp-glass conversion error until the glass was changed to a "surface" type. Our look leans on glass. | measured |
| 10 | Colour-code lines with lightness as well as hue, and give each line a landmark at its start. | Colour coding only works when each colour has one fixed meaning; colour-blind players read lightness, not hue. | sourced |

---

## 2. Parameter table

| Parameter | Value | Safe range | Status |
|---|---|---|---|
| Gravity in the air | 11.0 m/s² | 10.5 to 11 | measured (trainer: half gravity fell at 5.5, 1.5x at 15.8) |
| Gravity while rolling | game's own, unknown | | not measured; trainer says rolling keeps its own |
| Stock ollie | 0.36 m high, 0.58 s | | measured |
| Share of drop energy kept at a mega lip | 0.62 | 0.5 to 0.7 | guess from one map; measure with telemetry |
| Mega roll-in angle | 45 to 48° | up to 85° untested | sourced (two tested ramps) |
| Mega kicker lip angle | 28° | 20 to 30° | sourced |
| Mega landing angle | 21° | 20 to 30° | sourced |
| Gap per metre of vertical drop | about 0.75 m | 0.6 to 0.9 | guess (12 m gap from 16 m drop) |
| Real MegaRamp, for scale | 60 to 82 ft tall, 25 to 70 ft gap, 27 ft quarter | | sourced |
| Top push speed | about 12 m/s | | sourced (trainer's `MaxPushableSpeed` example) |
| On-foot sprint | 10 m/s cut | | measured |
| Largest step the wheels tolerate | 0 cm at entrances | under 2 cm anywhere | measured |
| Transition lip angle | 75° or more | 75 to 90° | measured threshold |
| Transition facet turn | 14° or less between strips | ours is about 3° | measured threshold |
| Grind curve | 10° or less per point, 0.45 m or less per segment | | sourced |
| Vert ramp that works in game | 3.84 m deck, 0.41 m vert, 17.3 m wide, 6 cm coping | | measured |
| Small transition | 1.5 to 2.1 m radius for walls under 1.2 m | | sourced (real parks) |
| Larger transition | 1.8 to 2.7 m radius | | sourced |
| Flat between facing transitions | 3 m or more | | sourced |
| Rails | 0.3 to 0.6 m | | sourced |
| Stairs the character can walk | 34° or flatter, 17 to 20 cm rise, 25 to 30 cm tread | stalls at 42° | measured |
| Skateable stairs | invisible ramp with the game's "stairs" behaviour, not stepped collision | | measured |
| Doorways and passages | 1.4 m wide, 2.44 m high; never under 1.0 m | | measured |
| Clearance over a path | nothing lower than 2.6 m | | measured |
| Rail posts to handrail gap beside stairs | 22 cm | 7 cm snagged | measured |
| Pump rollers | spacing 10x height; turns 3 m radius or more | 0.3 to 0.8 m high, 3 to 10 m apart | sourced |
| Triangles | up to 2.5 million drawn, 520,000 collision | ours: about 1.1 million | measured (a map that ships) |
| Package size | 16 MB to 1.2 GB ship; ours is far under | | sourced |
| Light range | 6 to 60 m, 40 if unset | | measured |
| Light time-of-day mask | 127 always, 88 evening and night | | measured |
| Field of view | wider reads faster | | sourced (one study) |
| Motion blur | does not help; strong blur reads slower | | sourced |
| Palette | sky `#87CEEB`, aqua `#7EC8E3`, title blue `#0997FF`, deep blue `#0054E3`, grass `#7CFC00`, white, chrome `#C0C0C0`, plus sunny yellow | | consensus (fan palettes, no primary source) |
| Line colours for colour-blind players | Okabe-Ito set; pair each hue with a different lightness | avoid red against green | sourced |

---

## 3. Findings by section

### How the game rides
- **Gravity is heavier than Earth's in the air**, near 11 m/s². The game also steers an air off a ramp back toward the ramp using its own gravity, so vert airs are assisted. (measured)
- **Pumping is real and tunable.** The trainer's "pump power" scales what a pump gives; the game decides when you are pumping. Roller sections are worth having. (sourced)
- **Wallies exist but ship switched off**; the trainer can turn them on. Do not design a line that needs one. (sourced)
- **Very large gaps are playable.** One released map advertises a 150 m drop-in and canyon gaps up to 120 m; another has 3 roll-ins at different heights on one ramp. So our 40 to 85 m gaps are within what the game has been made to do, but only testing shows whether ours land. (consensus)
- **No published top speed.** The trainer has a speed HUD and a jump read-out (takeoff speed and angle, height, distance, drop, landing speed), and records telemetry to CSV. That is an easier way to get numbers than our own plugin. (sourced)
- **Custom maps commonly fail on**: floor with no collision, ramps drawn but not solid, anything hidden from render (it is dropped from the build, collision included), steps at ramp feet, and protruding coping. (measured)

### What gets a map replayed
- The most-downloaded ReSkate maps are ports of Skate 3 and Skate 2 cities: familiar, dense, endlessly re-routable. Originals that do well are single strong ideas: a 2.7 km downhill snake run, a mega-gap canyon. (consensus)
- Working designers say the same two things: test arrangements with players, and build a circuit so lines never dead-end. (sourced)
- Three roll-in heights on one mega ramp is a cheap difficulty ladder. (consensus)
- Evidence on "time to first good line" and ideal spot spacing does not exist. Thin.

### Reward science
- **Challenge matched to skill**: perceived balance drives enjoyment, but two recent pre-registered studies found objective difficulty balance did not change how long people played. Offer several difficulty rungs and let players choose, instead of tuning one line. (sourced, mixed)
- **Effectance and juice**: immediate, generous feedback to your own action is enjoyable even at low challenge. Too much can overwhelm. In static geometry this means big visible consequences: long air, clear landings, splashy landmarks. A plugin could add a landing chime. (sourced)
- **Near-miss**: do not design for it. A video-game experiment found near misses made players more bored, and reviews failed to reproduce the persistence effect. In a skill game a near miss is useful only as information, so make failures legible: a visible knuckle that shows you came up short. (sourced)
- **Speed feel**: wider field of view and a higher camera raise perceived speed; motion blur does not. For geometry, put repeating objects close beside fast lines: pylons, lamp posts, arches. (sourced, one study)
- Landmarks and visible goals: well supported in wayfinding work; see below.
- Collection and session-length research specific to movement games: thin.

### Frutiger Aero
- Roughly 2004 to 2013; named in 2017 or 2018 by Sofi Lee (Xian) of CARI, after the Frutiger typeface and Windows Aero. (sourced)
- **Motifs, strongest first**: glossy and glass surfaces, skeuomorphic interface chrome, sky and water, bubbles, grass macro, aurora, lens flare and bokeh, humanist sans type. (consensus)
- **Neighbours to keep out**: Frutiger Metro (Vectordelia) is flat vector art; DORFic is stark white cities with orange and grey, abstract and not natural; Technozen is minimal and meditative; Dark Aero is the same gloss on black. Helvetica Aqua is the beach-and-sea branch and fits this map exactly. (consensus)
- The retro grey window with a navy title bar in the reference image is Windows 9x, which predates Aero. It works as nostalgia, but the on-style chrome is glassy blue, like the media player. Lean on the player skin more than the grey windows. (guess)
- **Gloss in this engine**: emission is ignored, the sun and sky are the game's own, and bounce light only appears if the map is built with "Bake lighting". Gloss will come from the game's reflections and bake, so judge materials in game at the time of day you care about. (measured)
- **Readable skate surfaces**: keep ride surfaces one saturated colour with white edges, and keep texture detail off them. (guess)

### Wayfinding
- One tall landmark visible from everywhere, a fixed meaning for each colour, and sight lines that show the next obstacle are the supported tools. Open worlds are rarely navigable with no interface at all, so the trainer's named spots are worth shipping. (sourced)
- SkateTanic ships 20 fast-travel points on the pause map. (measured)
- Steam Deck: one custom map loaded with collision but almost no drawn geometry under Proton. Expect Deck problems that are not the map's fault. (consensus)

---

## 4. Spot list

Dimensions in metres. "Serves" names the finding.

| # | Spot | Size | Where | Serves |
|---|---|---|---|---|
| 1 | Three roll-in heights on Bliss Drop | decks at 15, 30, 45 | Spire | difficulty ladder |
| 2 | Knuckle paint line on every mega landing | 0.3 wide stripe | all megas | legible failure |
| 3 | Pylon slalom beside the highway | posts every 6 | highway straight | speed feel |
| 4 | Arch gates over fast lines | 5 high, every 25 | highway, Drain viaduct | speed feel |
| 5 | Media-player vert wall, flush lip | 3.84 deck, 0.41 vert, 17 wide | Desktop Cay | proven vert size |
| 6 | Volume-slider rail | 0.4 high, 12 long | beside player wall | on-style chrome |
| 7 | Play-button dome | 3 radius, 0.6 high | Desktop Cay | effectance |
| 8 | Progress-bar manual pad chain | 3 pads, 8 x 1.5 x 0.2, 3 apart | boardwalk | line chaining |
| 9 | Start-orb bowl | 6 radius, 1.6 deep, 80° lip | Desktop Cay centre | lip rule |
| 10 | Scrollbar box rail | 0.3 high, 10 long, 0.15 wide | Desktop Cay | grind |
| 11 | Dialog-box stair set as an invisible ramp | 6 steps, 0.17 rise | Desktop Cay | stair rule |
| 12 | Window wallride pair facing each other | 14 x 9, 8 apart | Desktop Cay | transfer line |
| 13 | CD half-buried arc ledge | 5 radius arc, 0.45 high | plaza | grind curve rule |
| 14 | Bubble pump line | 6 domes, 0.5 high, 5 apart | lawn between bowls and minis | 10:1 roller rule |
| 15 | Lawn pump track loop | rollers 0.4 high at 4 spacing, berms 4 radius | south-west lawn | fills dead space |
| 16 | Second pump loop | same | north lawn | fills dead space |
| 17 | Snake run from ring to boardwalk | 4 wide, 1.2 deep, 80 long | west lawn | circuit |
| 18 | Flow bowl link between Bubble Bowls | 2 deep channel, 3 wide | bowls deck | chaining |
| 19 | Spine transfer into the big bowl | 1.8 high | bowls deck | chaining |
| 20 | Mini-ramp extension with 80° lip | 1.5 high, 1.6 radius | minis | lip rule |
| 21 | Three-level ledge stack | 0.25, 0.45, 0.65 high | plaza top | difficulty ladder |
| 22 | Long flat-down rail | 6 flat, 4 down a 5-stair | plaza | street staple |
| 23 | Hubba pair on the 12-stair | 0.5 above steps | plaza | already built; make flush |
| 24 | Euro gap | 1.2 up bank, 2.5 gap | plaza L2 | street staple |
| 25 | Water gap with a longer landing | 3 gap, 4 landing | plaza L1 | legible failure |
| 26 | Bank-to-ledge | 1.0 bank, 0.4 ledge on top | boardwalk | street staple |
| 27 | Pole jam | 30° pole, 1.5 long | boardwalk | street staple |
| 28 | Wallride gel panel | 4 high, 70° | under the Aqueduct tank | uses dead wall |
| 29 | Pylon banks | 1 high bank ring round each mega pylon | lawns | turns obstacles into spots |
| 30 | Aquarium glass ledge | 0.5 high, 24 long | tank base | landmark spot |
| 31 | Lily-pad gap line, tighter | pads 2 apart | garden pool | chaining |
| 32 | Seawall drop to beach bank | 1.2 drop, 3 bank | 6 places on the shore | uses the beach |
| 33 | Pier kicker to sand landing | 0.8 kicker | north shore | effectance |
| 34 | Rope-bridge roller deck | 0.3 rollers | islet bridge | pump |
| 35 | Islet volcano with 80° lip | 1.5 high | islet | lip rule |
| 36 | Causeway hip pair | 1.0 high, both sides | causeway middle | chaining |
| 37 | Highway off-ramp to Desktop Cay | 6% grade, 80 long | U-turn apex | circuit |
| 38 | Highway return bowl | 3 deep, catches the end | plaza beach | run-out design |
| 39 | Drain exit bank choice | left bank to ring, straight to launch | Spire base | choice |
| 40 | Mid-deck spiral ramp to ground | 5 wide, 8% grade | Spire | no dead-end deck |
| 41 | Rainbow rail | 0.5 high, 30 long, arched 1.5 | causeway | landmark grind |
| 42 | Dolphin-arc gap marker | paired sculptures either side of Splash landing | lagoon | visible goal |

---

## 5. Things that would break it

- Coping that stands proud, and any step at a ramp foot or doorway.
- Geometry hidden from render in Blender: it is left out of the build with its collision.
- Trusting emission for glow, or judging lighting in a Blender render.
- Glass materials that fail conversion and stop the build.
- Stepped collision on stairs, stairs steeper than 34° on walking routes, passages under 1 m.
- Anything hanging lower than 2.6 m over a route, or a post within 22 cm of a handrail.
- Lines that end in a wall or a dead deck with no way down.
- A plugin bundled in the map package: players can then only get the map from the launcher, not in a multiplayer session.
- Too many always-on lights: SkateTanic had to cut night lighting to 35% of day.

---

## 6. Questions only a play-test settles

| Question | Test |
|---|---|
| How much speed does a slope really give? | Roll each mega line with the trainer's jump read-out on; note takeoff speed at each lip. |
| Do the gaps land? | Same run: compare read-out distance with the built gap. |
| Does the skater stay on an 85° drop? | Ride the Drain from the crown. |
| Does a full loop work? | Ride Aurora Loop at stock tuning. |
| Does a full pipe hold you at the top? | Carve high in the Aqueduct pipe. |
| What step height is actually felt? | Porterino's authors are still testing this; ride each deck junction slowly. |
| Is 75° the real lip threshold? | Air out of the 68° and 81° bowls and compare. |
| How do glass and water render? | Build once and look at the tank, the Spire and the lagoon at noon and night. |
| Do the grind curves register? | Grind the seawall and one bowl coping. |
| Frame rate on a weak PC? | Stand on the crown facing the island. |

---

## 7. Sources

Primary, read in full:
- [ReSkate docs](https://docs.reskate.dev/llms.txt): [Studio](https://docs.reskate.dev/mods/studio), [maps](https://docs.reskate.dev/mods/maps), [skater API](https://docs.reskate.dev/plugins/api/skater), [limits](https://docs.reskate.dev/plugins/limits)
- [ReSkate Trainer README](https://github.com/Dingo-Shenanigans/ReSkate/blob/main/Extension/Trainer/README.md)
- [Porterino map toolkit](https://github.com/Rinoversal/Porterino) and its checks and lighting docs
- [SkateTanic build notes](https://github.com/AlexanderPuglisi/Skate-Tanic)

Search results used:
- [Mega ramp, Wikipedia](https://en.wikipedia.org/wiki/Mega_ramp); [Star Tribune on the X Games MegaRamp](https://www.startribune.com/megaramp-has-big-air-competitors-contemplating-new-heights/488784201)
- [Elements of good skatepark design](https://framinghammatters.blogspot.com/2015/08/elements-of-good-skatepark-design.html); [Skatepark, Wikipedia](https://en.wikipedia.org/wiki/Skatepark)
- [USA Cycling: backyard pump track](https://usacycling.org/article/how-to-build-a-backyard-pump-track); [UCI pump track guide](https://manuals.plus/uci/pump-track-guide-manual.pdf)
- [Frutiger Aero, Wikipedia](https://en.wikipedia.org/wiki/Frutiger_Aero); [Aesthetics Wiki](https://aesthetics.fandom.com/wiki/Frutiger_Aero); [DORFic](https://aesthetics.fandom.com/wiki/DORFic); [Frutiger Metro](https://aesthetics.fandom.com/wiki/Frutiger_Metro); [DesignPieces palette](https://www.designpieces.com/palette/frutiger-aero-color-palette-hex-and-rgb/); [DaisyUI trend overview](https://trends.daisyui.com/trend/frutiger-aero/)
- [Challenge enjoyment in a shooter](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5954478/); [flow and SDT test](https://unpaywall.org/10.1145%2F3611065); [juicy feedback study](https://spiral.imperial.ac.uk/entities/publication/253c32f5-d124-4a23-88b5-9aaaf114608d); [effectance](https://people.csail.mit.edu/dkao/pdf/ballou2021effectance.pdf)
- [Near miss in a video game](https://bora.uib.no/bora-xmlui/handle/1956/23601); [Near-miss effect, Wikipedia](https://en.wikipedia.org/wiki/Near-miss_effect)
- [Perceived velocity in racing games](https://eudl.eu/doi/10.1007/978-3-319-55834-9_14); [motion blur study](https://studios.disneyresearch.com/2013/11/06/simulated-motion-blur-does-not-improve-player-experience-in-racing-game/)
- [Level design tricks](https://gamedeveloper.com/design/level-design-tricks-of-the-trade); [wayfinding thesis](https://era.library.ualberta.ca/files/cgh93gz674/Nisbet_Brett_A_201604_MA.pdf)
- [Skater XL community maps](https://blog.playstation.com/2020/06/30/community-created-maps-come-to-skater-xl-on-ps4-at-launch/); [Skater XL interview](https://gamingbolt.com/skater-xl-interview-early-access-post-launch-support-map-design-and-more)
- [skatemods maps](https://skatemods.com/reskate/maps/); [Timber Ridge Snake Run](https://thunderstore.io/c/reskate/p/Team_Rezlin/Timber_Ridge_Snake_Run); [re-skate.wiki maps guide](https://re-skate.wiki/guides/reskate-maps)
- [Colour-blind palettes](https://www.datawrapper.de/blog/colorblindness-part2); [game accessibility guidelines](https://gameaccessibilityguidelines.com/?p=3273)
