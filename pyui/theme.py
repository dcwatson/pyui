import json
import os

import sdl2
from sdl2.sdlimage import IMG_Load

from .asset import SlicedAsset
from .font import Font


class Theme:
    def __init__(self, config_path):
        self.path = os.path.dirname(config_path)
        self.config = json.load(open(config_path))
        self.surface_cache = {}

    def __del__(self):
        for asset_path, surface in self.surface_cache.items():
            sdl2.SDL_FreeSurface(surface)

    def load_asset(self, name):
        asset_path = os.path.join(self.path, self.config["assets"][name]["file"])
        center = self.config["assets"][name].get("slice")
        if asset_path not in self.surface_cache:
            self.surface_cache[asset_path] = IMG_Load(asset_path.encode("utf-8"))
        return SlicedAsset(self.surface_cache[asset_path], center)

    def font(self, name="default", size=None):
        info = self.config["fonts"].get(name)
        filename = info["file"] if info else name
        fontsize = size or info["size"]
        return Font.load(filename, fontsize)

    def env(self, name="default"):
        return self.config.get("env", {}).get(name, {})
