import json
import os

from .asset import SlicedAsset


class Theme:
    def __init__(self, config_path):
        self.path = os.path.dirname(config_path)
        self.config = json.load(open(config_path))

    def load_asset(self, name):
        asset_path = os.path.join(self.path, self.config["assets"][name]["file"])
        center = self.config["assets"][name].get("slice")
        return SlicedAsset(asset_path, center)
