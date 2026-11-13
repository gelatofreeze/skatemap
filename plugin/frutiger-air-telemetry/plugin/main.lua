-- Frutiger Air telemetry: records every jump and the game's physics tuning,
-- and saves them to telemetry.json in this plugin's data folder.
-- Console: "fa save" writes the file now, "fa open" shows the folder,
-- "fa mark <name>" labels the next jumps (e.g. fa mark bliss).

local jumps = {}
local seen = 0
local label = "unlabelled"
local top_speed = 0
local samples = {}        -- speed while rolling, for drag estimates

local function vec(v)
    return {x = v.x, y = v.y, z = v.z}
end

local function tuning()
    local out, have = {}, {}
    -- find() returns at most 64 values a call, so ask by keyword.
    for _, words in {"", "jump", "speed", "gravity", "friction", "push", "air", "roll",
                     "pump", "max", "accel", "drag", "slope", "land", "pop", "ollie",
                     "transition", "vert", "grind", "carve", "brake", "bail"} do
        for _, v in reskate.physics.find(words) do
            if not have[v.id] then
                have[v.id] = true
                table.insert(out, {id = v.id, label = v.label, group = v.group,
                                   kind = v.kind, value = v.value, stock = v.stock})
            end
        end
    end
    return out
end

local function save()
    local level = reskate.level.current()
    local doc = {
        saved_at = reskate.time.now(),
        level = level,
        top_speed = top_speed,
        jumps = jumps,
        rolling = samples,
        tuning = tuning(),
    }
    local ok, why = reskate.files.write("telemetry.json", reskate.json.encode(doc, true))
    reskate.console.print(ok and ("fa: saved " .. #jumps .. " jumps") or ("fa: not saved: " .. tostring(why)))
end

reskate.on("tick", function()
    local t = reskate.skater.telemetry()
    if not t or not t.skater then return end
    if t.speed > top_speed then top_speed = t.speed end
    if t.last and t.last.serial ~= seen and t.last.serial ~= 0 then
        seen = t.last.serial
        local j = t.last
        if #jumps < 2000 then
            table.insert(jumps, {
                label = label,
                takeoff_speed = j.takeoff_speed, takeoff_angle = j.takeoff_angle,
                air_time = j.air_time, height = j.height, distance = j.distance,
                drop = j.drop, landing_speed = j.landing_speed, state = j.state,
                takeoff = vec(j.takeoff), landing = vec(j.landing),
            })
        end
    end
end)

-- Once a second, note position and speed while rolling: shows how much
-- speed a slope really gives and how fast it bleeds off on the flat.
reskate.time.every(1000, function()
    local t = reskate.skater.telemetry()
    if t and t.skater and not t.airborne and t.speed > 1 and #samples < 4000 then
        table.insert(samples, {label = label, speed = t.speed, p = vec(t.position), state = t.physics_state})
    end
end)

reskate.time.every(30000, function()
    if #jumps > 0 then save() end
end)

reskate.console.command("fa", "Frutiger Air telemetry: save, open, mark <name>", function(args)
    if args[1] == "save" then
        save()
    elseif args[1] == "open" then
        reskate.files.reveal()
    elseif args[1] == "mark" and args[2] then
        label = args[2]
        reskate.console.print("fa: jumps are now labelled " .. label)
    else
        reskate.console.print("fa save | fa open | fa mark <name>")
    end
end, {{name = "save", help = "Write telemetry.json now"},
      {name = "open", help = "Show the folder that holds telemetry.json"},
      {name = "mark", args = "<name>", help = "Label the jumps that follow"}})

reskate.log("Frutiger Air telemetry loaded")
