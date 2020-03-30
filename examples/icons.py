import pyui


class SearchView(pyui.View):
    search_text = pyui.State(default="")

    def content(self):
        # fmt: off
        yield pyui.HStack()(
            pyui.TextField(self.search_text, placeholder="Search icons"),
            pyui.Button("Search", asset="button.primary").priority("high")
        ).padding(10)
        # fmt: on


class IconsView(pyui.View):
    def content(self):
        # fmt: off
        yield pyui.VStack(spacing=0)(
            SearchView(),
            pyui.ScrollView()(
                pyui.Grid(size=100, flex=True)(
                    pyui.ForEach(pyui.Icon.data["icons"], lambda name: (
                        pyui.Rectangle(
                            pyui.VStack()(
                                pyui.Icon(name, size=32),
                                pyui.Text(name).font(size=11)
                            )
                        ).background(30, 30, 30).radius(5).padding(5)
                    ))
                )
            )
        )
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.temp.IconViewer")
    app.window("Icon Viewer", IconsView())
    app.run()
