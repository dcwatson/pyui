import base64
import io

import httpx
import sdl2

import pyui


class ThumbnailView(pyui.View):
    image = None

    def __init__(self, file):
        self.label = file["slug"]
        if file.get("thumbnail"):
            fp = io.BytesIO(base64.b64decode(file["thumbnail"]))
            self.image = sdl2.rw_from_object(fp)
        super().__init__()

    def content(self):
        # fmt: off
        inner = [pyui.Image(rw=self.image)] if self.image else []
        yield pyui.VStack(spacing=5)(
            pyui.Rectangle(*inner),
            pyui.Text(self.label).font(size=10),
        )
        # fmt: on


class TagView(pyui.View):
    files = pyui.State(default=list)
    loading = pyui.State(default=False)

    def __init__(self, tag):
        super().__init__()
        self.slug = tag["slug"]
        self.url = tag["api_url"]

    def reuse(self, other):
        return self.slug == other.slug

    async def built(self):
        await self.refresh()

    async def refresh(self):
        self.loading = True
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url)
            self.files = r.json().get("files", [])
            self.loading = False

    def content(self):
        # fmt: off
        yield pyui.VStack()(
            pyui.HStack()(
                pyui.Text(self.slug).font("bold", 24),
                pyui.Spacer(),
                pyui.Spinner() if self.loading.value else pyui.Spacer(),
                pyui.Button("Refresh", action=self.refresh),
            ).padding(10),
            pyui.ScrollView()(
                pyui.Grid(size=100, flex=True)(
                    pyui.ForEach(self.files.value, lambda file: (
                        ThumbnailView(file=file)
                    )),
                ).padding(10, 0, 10, 0).position(pyui.Position.TOP),
            ).priority(pyui.Priority.LOW),
        )
        # fmt: on


class FilesView(pyui.View):
    RECENT_TAG = {
        "slug": "Recent",
        "api_url": "https://temp.io/api/files/",
        "num_files": "",
    }

    tags = pyui.State(default=list)
    selected_tag = pyui.State(default=[0])

    async def built(self):
        async with httpx.AsyncClient() as client:
            r = await client.get("https://temp.io/api/files/", params={"n": 0})
            self.tags = [FilesView.RECENT_TAG] + r.json().get("tags", [])

    def content(self):
        # fmt: off
        yield pyui.HStack(spacing=0)(
            pyui.ScrollView()(
                pyui.List(selection=self.selected_tag)(
                    pyui.ForEach(self.tags.value, lambda tag, idx: (
                        pyui.HStack()(
                            pyui.Text(tag["slug"])
                                .font("bold" if self.selected_tag.value[0] == idx else "default"),
                            pyui.Spacer(),
                            (
                                pyui.Text(tag["num_files"])
                                    .font(size=11)
                                    .background(60, 60, 60)
                                    .padding(4, 7, 4, 7)
                                    .radius(4)
                                if tag["num_files"] else
                                pyui.Text("")
                            ),
                        )
                    )),
                ),
            ).size(width=200),
            (
                TagView(self.tags.value[self.selected_tag.value[0]])
                if self.tags.value and self.selected_tag.value else
                pyui.Rectangle()
            ),
        )
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.temp.Viewer")
    app.window("temp.io", FilesView(), width=600, height=350)
    app.run()
