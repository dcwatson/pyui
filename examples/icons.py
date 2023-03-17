import pyui


class SearchView(pyui.View):
    # Separate state since live-searching is slow.
    current_text = pyui.State(default="")

    def __init__(self, search_binding):
        super().__init__()
        self.search_binding = search_binding

    def search(self, text=None):
        self.search_binding.value = self.current_text.value

    def content(self):
        yield pyui.HStack()(
            pyui.TextField(
                self.current_text, placeholder="Search icons", action=self.search
            ),
            pyui.Button("Search", action=self.search, asset="button.primary").priority(
                "high"
            ),
        ).padding(10)


class IconsView(pyui.View):
    search_text = pyui.State(default="")

    def filtered_icons(self):
        search = self.search_text.value.lower()
        for name in pyui.Icon.data["icons"]:
            if search == "" or search in name:
                yield name

    def content(self):
        yield pyui.VStack(spacing=0)(
            SearchView(self.search_text),
            pyui.ScrollView()(
                pyui.Grid(size=100, flex=True)(
                    pyui.ForEach(
                        self.filtered_icons(),
                        lambda name: (
                            pyui.Rectangle(
                                pyui.VStack()(
                                    pyui.Icon(name, size=32),
                                    pyui.Text(name).font(size=11),
                                )
                            )
                            .background(30, 30, 30)
                            .padding(5)
                        ),
                    )
                ).position(pyui.Position.TOP_LEADING)
            ),
        )


if __name__ == "__main__":
    app = pyui.Application("io.temp.IconViewer")
    app.window("Icon Viewer", IconsView())
    app.run()
