#!/usr/bin/env python3

"""
Query the XKB registry via xkbcommon and process the results, e.g. filter and
export (non-)Latin layouts.
"""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, Union

ROOT = Path(__file__).parent.parent
# Add our internal xkbcommon test lib to the PATH
sys.path.append(str(ROOT / "tests"))
# Add scripts to the PATH
sys.path.append(str(ROOT / "scripts"))

import xkbcommon
from registry import Registry

logger = logging.getLogger()
logging.basicConfig(
    stream=sys.stderr, level=logging.INFO, format="[%(levelname)s] %(message)s"
)

Keycode: TypeAlias = str
Keysym: TypeAlias = str
ModifierMask: TypeAlias = int
LevelMapping: TypeAlias = Union[tuple[Keysym, ...], str]
KeyMapping: TypeAlias = list[LevelMapping]
FullKeyMapping: TypeAlias = dict[ModifierMask, LevelMapping]
Keymap: TypeAlias = dict[Keycode, KeyMapping | FullKeyMapping]


@dataclass(frozen=True, order=True)
class Layout:
    layout: str
    variant: str

    def __str__(self) -> str:
        if self.variant:
            return f"{self.layout}({self.variant})"
        else:
            return self.layout


def discardable_level(key_mapping: KeyMapping, level: int) -> bool:
    # Reset levels identical to base levels
    x = key_mapping[level]
    return not (
        level == 0
        or (
            bool(x)
            and x != key_mapping[0]
            and (level < 2 or x != key_mapping[level % 2])
            and (level < 4 or x != key_mapping[level % 4])
        )
    )


def discard_masks(key_mapping: FullKeyMapping) -> KeyMapping:
    return [e[min(e)] for e in key_mapping]


METADATA_KEY_NAME = "__name__"
METADATA_KEY_ISO639 = "__iso639___"
METADATA_KEY_ISO3166 = "__iso3166___"
METADATA_KEYS = (METADATA_KEY_NAME, METADATA_KEY_ISO639, METADATA_KEY_ISO3166)


def process_layouts(xkb_root: Path, registry: Registry, args: argparse.Namespace):
    """
    Process layouts from a given registry, depending on the CLI arguments.
    """
    keymaps: dict[Layout, Keymap] = defaultdict(lambda: defaultdict(dict))
    for layout in registry.layouts:
        layout_ref = Layout(layout.layout, layout.variant)
        try:
            with xkbcommon.ForeignKeymap(
                xkb_base=xkb_root,
                rules=rules,
                layout=layout.layout,
                variant=layout.variant,
            ) as keymap:
                layout_ref_str = str(layout_ref)
                keymaps[layout_ref_str][METADATA_KEY_NAME] = (
                    layout.description or layout_ref_str
                )
                keymaps[layout_ref_str][METADATA_KEY_ISO639] = layout.iso639
                keymaps[layout_ref_str][METADATA_KEY_ISO3166] = layout.iso3166
                r: xkbcommon.KeyLevel
                for r in xkbcommon.ForeignKeymap.get_keys_levels(keymap):
                    # Skip high keycodes
                    if r.keycode > 255:
                        continue
                    key = xkbcommon.xkb_keymap_key_get_name(keymap, r.keycode)

                    entry_key = f"{r.level}:{','.join(map(str, r.masks)) or 0}"
                    keymaps[layout_ref_str][key][entry_key] = (
                        r.utf8
                        if r.utf8
                        and (
                            # len(r.utf8) > 1
                            # or unicodedata.category(r.utf8) != "Cc"
                            r.utf8.isprintable() and not r.utf8.isspace()
                        )
                        else tuple(map(xkbcommon.xkb_keysym_get_name, r.keysyms))
                    )
        except ValueError as err:
            # Log error message and skip
            logger.error(err)
            continue

    json.dump(keymaps, fp=sys.stdout, sort_keys=True, indent=None)


def parse_cli_args() -> argparse.Namespace:
    """
    Create CLI parser and parse corresponding arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--xkb-root", type=Path, required=True)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--rules", help="Rules set to use")
    subparsers = parser.add_subparsers(required=True)
    subparser = subparsers.add_parser("keymaps", help="Export keymaps")
    subparser.set_defaults(run=process_layouts)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    xkb_root: Path = args.xkb_root
    rules: str | None = args.rules
    registry = Registry.load(xkb_roots=(xkb_root,), rules=rules)
    args.run(xkb_root, registry, args)
