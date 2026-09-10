#!/usr/bin/env python3
"""Convert simulator JSON exports into a compact CircuitPython data module."""

import argparse
import json
from pathlib import Path


def load_catalog(export_dir, module):
    path = export_dir / (module + "-catalog.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data["target"] != "rev-d-dev" or data["module"] != module:
        raise ValueError("%s is not a Rev D %s catalog" % (path, module))
    return data


def bytes_literal(values):
    return "bytes((%s))" % ",".join(str(value) for value in values)


def write_module(output, eyes, mouth):
    lines = [
        '"""Generated from Bender Expression Lab catalogs; do not hand edit."""',
        "",
        "DEFAULT_ANIMATION_FPS = %d" % eyes["settings"]["defaultAnimationFPS"],
        "MAX_DISPLAY_FPS = %d" % eyes["settings"]["maxDisplayFPS"],
        "",
    ]
    for constant, catalog in (("EYES", eyes), ("MOUTH", mouth)):
        frames = sorted(catalog["frames"], key=lambda frame: frame["id"])
        animations = sorted(catalog["animations"], key=lambda animation: animation["id"])
        if not animations or not animations[0]["entry"]:
            raise ValueError("%s catalog has no usable animations" % catalog["module"])
        lines.append("%s_WIDTH = %d" % (constant, frames[0]["width"]))
        lines.append("%s_HEIGHT = %d" % (constant, frames[0]["height"]))
        lines.append("%s_NORMAL_FRAME = %d" % (constant, animations[0]["entry"][0]))
        lines.append("%s_FRAMES = (" % constant)
        for frame in frames:
            lines.append("    %s," % bytes_literal(frame["data"]))
        lines.append(")")
        lines.append("%s_ANIMATIONS = {" % constant)
        for animation in animations:
            lines.append(
                "    %d: (%r, %r, %r, %r)," % (
                    animation["id"], animation["name"],
                    tuple(animation["entry"]),
                    tuple(animation.get("exit") or ()), animation["exitMode"],
                )
            )
        lines.append("}")
        lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def expanded_frame_count(animation):
    entry_count = len(animation["entry"])
    if animation["exitMode"] == "custom":
        return entry_count + len(animation.get("exit") or ())
    if animation["exitMode"] == "reverse":
        return entry_count * 2 - 1
    return entry_count


def write_brain_module(output, eyes, mouth, performances, audio_catalog,
                       audio_manifest):
    animations = []
    for target, catalog in (("eyes", eyes), ("mouth", mouth)):
        for animation in catalog["animations"]:
            animations.append((
                animation["id"], target, animation["name"],
                expanded_frame_count(animation),
            ))
    animations.sort()
    lines = [
        '"""Generated display-animation index for the Brain; do not hand edit."""',
        "",
        "DEFAULT_ANIMATION_FPS = %d" % eyes["settings"]["defaultAnimationFPS"],
        "# (animation ID, target, display name, complete entry/exit frame count)",
        "ANIMATIONS = (",
    ]
    lines.extend("    %r," % (animation,) for animation in animations)
    lines.extend((")", ""))
    audio_slots = {
        item["audioID"]: item["slot"] for item in audio_manifest["audio"]
    }
    audio_durations = {
        item["id"]: item["duration"] for item in audio_catalog["audio"]
    }
    lines.append("AUDIO_SLOTS = %r" % audio_slots)
    lines.append("# Event: (start ms, kind, target/audio ID, animation ID/slot, entry, hold, exit)")
    lines.append("# kind 0 = animation; kind 1 = audio")
    lines.append("PERFORMANCES = (")
    for performance in sorted(performances["performances"], key=lambda item: item["id"]):
        events = []
        duration = 0
        for event in performance["animations"]:
            target = 1 if event["target"] == "eyes" else 2
            values = (event["startTime"], 0, target, event["animationID"],
                      event["entryDuration"], event["holdDuration"],
                      event["exitDuration"])
            events.append(values)
            duration = max(duration, event["startTime"]
                           + event["entryDuration"] + event["holdDuration"]
                           + event["exitDuration"])
        for event in performance["audio"]:
            audio_id = event["audioID"]
            if audio_id not in audio_slots:
                raise ValueError("audio ID %d has no Audio FX slot" % audio_id)
            events.append((event["startTime"], 1, audio_id,
                           audio_slots[audio_id], 0, 0, 0))
            duration = max(duration, event["startTime"]
                           + audio_durations.get(audio_id, 0))
        events.sort(key=lambda event: (event[0], event[1]))
        lines.append("    (%d, %r, %d, (" % (
            performance["id"], performance["name"], duration))
        lines.extend("        %r," % (event,) for event in events)
        lines.append("    )),")
    lines.extend((")", ""))
    output.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("export_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--brain-output", type=Path)
    args = parser.parse_args()
    eyes = load_catalog(args.export_dir, "eyes")
    mouth = load_catalog(args.export_dir, "mouth")
    if eyes["settings"] != mouth["settings"]:
        raise ValueError("Eyes and Mouth playback settings differ")
    write_module(args.output, eyes, mouth)
    if args.brain_output is not None:
        performances = json.loads((args.export_dir / "performance-catalog.json")
                                  .read_text(encoding="utf-8"))
        audio_catalog = json.loads((args.export_dir / "audio-catalog.json")
                                   .read_text(encoding="utf-8"))
        audio_manifest = json.loads((args.export_dir / "audiofx-manifest.json")
                                    .read_text(encoding="utf-8"))
        write_brain_module(args.brain_output, eyes, mouth, performances,
                           audio_catalog, audio_manifest)


if __name__ == "__main__":
    main()
