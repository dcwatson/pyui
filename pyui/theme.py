import json
import os

from .asset import SlicedAsset
from .font import Font


class Theme:
    def __init__(self, config_path):
        self.path = os.path.dirname(config_path)
        self.config = json.load(open(config_path))
        self.name = self.config["name"]
        self.asset_cache = {}

    def load_asset(self, name):
        if name not in self.asset_cache:
            asset_path = os.path.join(self.path, self.config["assets"][name]["file"])
            center = self.config["assets"][name].get("slice")
            self.asset_cache[name] = SlicedAsset(asset_path, center)
        return self.asset_cache[name]

    def prepare(self, renderer):
        for name in self.config["fonts"]:
            self.font(name).prepare(renderer)

    def font(self, name="default", size=None):
        info = self.config["fonts"].get(name)
        filename = info["file"] if info else name
        fontsize = size or info["size"]
        return Font.load(filename, fontsize)

    def env(self, name="default"):
        return self.config.get("env", {}).get(name, {})
