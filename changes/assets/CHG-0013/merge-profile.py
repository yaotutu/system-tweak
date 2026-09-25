#!/usr/bin/env python3
from configparser import RawConfigParser
from pathlib import Path
import re


def load(path: Path) -> RawConfigParser:
    config = RawConfigParser(interpolation=None, strict=False, delimiters=("=",))
    config.optionxform = str
    if path.exists():
        config.read(path, encoding="utf-8")
    return config


def save(config: RawConfigParser, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        config.write(stream, space_around_delimiters=False)


profile_path = Path.home() / ".config/fcitx5/profile"
profile = load(profile_path)
item_re = re.compile(r"Groups/0/Items/(\d+)$")
items: list[tuple[int, str, dict[str, str]]] = []
for section in list(profile.sections()):
    match = item_re.fullmatch(section)
    if not match:
        continue
    values = dict(profile.items(section))
    name = values.get("Name", "").strip()
    if name:
        items.append((int(match.group(1)), name, values))
    profile.remove_section(section)
items.sort()
by_name: dict[str, dict[str, str]] = {}
for _, name, values in items:
    by_name.setdefault(name, values)
ordered = ["keyboard-us", "rime"] + [
    name for _, name, _ in items if name not in {"keyboard-us", "rime"}
]
if not profile.has_section("Groups/0"):
    profile.add_section("Groups/0")
profile.set("Groups/0", "Name", profile.get("Groups/0", "Name", fallback="Default"))
profile.set(
    "Groups/0",
    "Default Layout",
    profile.get("Groups/0", "Default Layout", fallback="us"),
)
profile.set("Groups/0", "DefaultIM", "rime")
for index, name in enumerate(dict.fromkeys(ordered)):
    section = f"Groups/0/Items/{index}"
    profile.add_section(section)
    profile.set(section, "Name", name)
    layout = by_name.get(name, {}).get("Layout")
    if layout:
        profile.set(section, "Layout", layout)
if not profile.has_section("GroupOrder"):
    profile.add_section("GroupOrder")
profile.set("GroupOrder", "0", "Default")
save(profile, profile_path)

config_path = Path.home() / ".config/fcitx5/config"
config = load(config_path)
for section, value in (
    ("Hotkey/TriggerKeys", "Control+space"),
    ("Hotkey/AltTriggerKeys", ""),
):
    if config.has_section(section):
        config.remove_section(section)
    config.add_section(section)
    config.set(section, "0", value)
save(config, config_path)
