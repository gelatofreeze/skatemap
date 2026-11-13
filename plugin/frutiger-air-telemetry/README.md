# Frutiger Air telemetry

A small ReSkate plugin that measures the game's real physics so the map's
jumps can be sized from data. Untested: it was written from the ReSkate
plugin docs without the game to run it.

## Use

1. Copy this folder into the game's `Mods` folder.
2. Start ReSkate. Allow the plugin when the game asks.
3. Load any map, skate, and hit jumps. On Frutiger Air, type
   `fa mark bliss` (or `aurora`, `splash`, `drain`, `highway`) in the
   console before each mega line so its jumps are labelled.
4. Type `fa save`, then `fa open`. Send back `telemetry.json`.

It records, for every jump: takeoff speed and angle, air time, height,
distance, drop and landing speed. It also records rolling speed once a
second and the game's physics tuning values.
