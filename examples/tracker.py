import pyui

game = {
    "address": "127.0.0.1",
    "port": 19567,
    "players": ["Vertigo", "silverfox", "poverty", "croc", "Seven", "grimm"],
    "description": "AA only. ISDN+",
}


class GameItemView(pyui.View):
    def content(self):
        # fmt: off
        yield pyui.HStack()(
            pyui.VStack(spacing=5, alignment=pyui.Alignment.LEADING)(
                pyui.Text(self.game["address"]).font("bold"),
                pyui.Text(self.game["description"]),
                pyui.HStack()(
                    pyui.ForEach(self.game["players"], lambda player, idx: (
                        pyui.Text(player) if idx > 0 else
                        pyui.Text(player).background(80, 80, 100).padding(2, 6, 2, 6).radius(4)
                    ))
                )
            ),
            pyui.Spacer(),
            pyui.Button("Join"),
        )
        # fmt: on


class TrackerView(pyui.View):
    address = pyui.State(default="avara.io")
    games = pyui.State(default=[game])
    selected = pyui.State()

    def content(self):
        # fmt: off
        yield pyui.VStack()(
            pyui.HStack()(
                pyui.TextField(self.address, placeholder="Tracker Address").priority("high"),
                pyui.Button("Refresh", asset="button.primary"),
            ),
            pyui.HStack()(
                pyui.ScrollView()(
                    pyui.List(self.games.value, selection=self.selected, builder=lambda game: (
                        GameItemView(game=game)
                    )) if self.games.value else pyui.Text("No games found")
                ),
            ),
        ).padding(20)
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.avara.MicroTracker")
    app.window("Avara MicroTracker", TrackerView())
    app.run()
