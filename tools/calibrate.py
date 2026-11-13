"""Fit the generator's physics to measurements from the game.

    python3 tools/calibrate.py path/to/telemetry.json

Reads the file the frutiger-air-telemetry plugin saves and rewrites
frutiger/physics.json:
  gravity     from each jump's takeoff speed, angle and apex height
  speed_keep  share of drop energy the skater still has at a mega-line lip
              (jumps labelled with `fa mark <line>`; start height is the Spire deck)
"""
import json, math, os, statistics, sys

DECKS = {"bliss": 45.0, "aurora": 45.0, "splash": 45.0, "aqueduct": 45.0, "drain": 85.0, "highway": 85.0}
doc = json.load(open(sys.argv[1]))
g, keep = [], []
for j in doc.get("jumps", []):
    v, a, h = j["takeoff_speed"], math.radians(j["takeoff_angle"]), j["height"]
    if h > 0.5 and v > 3 and abs(math.sin(a)) > 0.1:
        g.append((v * math.sin(a)) ** 2 / (2 * h))
for j in doc.get("jumps", []):
    top = DECKS.get(j.get("label", ""))
    if top and g:
        fall = top - j["takeoff"]["y"]
        if fall > 5:
            keep.append(j["takeoff_speed"] ** 2 / (2 * statistics.median(g) * fall))
out = {"gravity": round(statistics.median(g), 3) if g else 9.81,
       "speed_keep": round(min(1.0, statistics.median(keep)), 3) if keep else 0.7,
       "source": "measured from %d jumps (%d on labelled mega lines); top speed %.1f m/s"
                 % (len(g), len(keep), doc.get("top_speed", 0))}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frutiger", "physics.json")
json.dump(out, open(path, "w"), indent=4)
print(out)
