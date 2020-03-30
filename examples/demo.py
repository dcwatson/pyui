import datetime
import random

import sdl2

import pyui


class TimestampView(pyui.View):
    timestamp = pyui.State(datetime.datetime, default=datetime.datetime.now)

    def update_timestamp(self):
        self.timestamp = datetime.datetime.now()

    def content(self):
        # fmt: off
        yield pyui.VStack()(
            pyui.HStack()(
                pyui.Text(self.timestamp.value.strftime("%H:%M:%S.%f")),
                pyui.Button(action=self.update_timestamp)(
                    pyui.Image("images/python.svg").size(height=14),
                    pyui.Text("Update"),
                ),
            ),
        )
        # fmt: on


def random_bars(num=5):
    return [0.1 + (random.random() * 0.9) for i in range(num)]


class BarChartView(pyui.View):
    bars = pyui.State(default=random_bars)

    def randomize(self):
        self.bars = random_bars(len(self.bars.value))

    def more_bars(self):
        self.bars = random_bars(len(self.bars.value) + 1)

    def fewer_bars(self):
        self.bars = random_bars(len(self.bars.value) - 1)

    def content(self):
        # fmt: off
        yield pyui.VStack(spacing=10)(
            pyui.Text("Bar Chart"),
            pyui.Spacer(),
            pyui.HStack(alignment=pyui.Alignment.TRAILING)(
                pyui.ForEach(self.bars.value, lambda height, idx: (
                    pyui.Rectangle()(
                        pyui.Text("{:.0f}%".format(height * 100.0))
                            .color(230, 230, 230)
                            .background(0, 0, 0, 160)
                            .padding(3)
                            .font(size=11)
                            .radius(2)
                    ).background(
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    ).size(height=height).animate(pyui.spring(), 0.3, delay=0.03 * idx)
                ))
            ).priority(pyui.Priority.HIGH),
            pyui.HStack()(
                pyui.Button("Fewer Bars", action=self.fewer_bars),
                pyui.Button("Randomize", action=self.randomize),
                pyui.Button("More Bars", action=self.more_bars),
            ),
        )
        # fmt: on


class ImageSizerView(pyui.View):
    scale = pyui.State(int, default=50)

    @property
    def pct(self):
        return self.scale.value / 100

    def content(self):
        # fmt: off
        yield pyui.VStack(
            pyui.Slider(self.scale, 1, 100),
            pyui.Image("images/python.png").size(width=self.pct, height=self.pct),
        )
        # fmt: on


class DescriptionView(pyui.View):
    description = pyui.State(str, default="")

    def content(self):
        # fmt: off
        yield pyui.VStack(alignment=pyui.Alignment.LEADING, spacing=5)(
            pyui.Text(self.lang),
            pyui.TextField(self.description, "Description for {}".format(self.lang)),
        )
        # fmt: on


class FormView(pyui.View):
    language = pyui.State(str, default="")
    languages = pyui.State(default=["Python"])

    def new_language(self):
        self.languages = self.languages.value + [self.language.value]
        self.language = ""

    def content(self):
        # fmt: off
        fg = pyui.Environment("text").color if self.language.value else sdl2.SDL_Color(150, 150, 150)
        yield pyui.VStack(spacing=20)(
            pyui.HStack()(
                pyui.TextField(self.language, "Add a new language"),
                pyui.Button(action=self.new_language)(
                    pyui.Text("Add {}".format(self.language.value)).color(fg),
                ).disable(self.language.value == ""),
                pyui.Spacer(),
            ),
            pyui.ForEach(self.languages.value, lambda lang: (
                DescriptionView(lang=lang)
            )),
        )
        # fmt: on


class ListView(pyui.View):
    dynamic_items = pyui.State(default=[i + 1 for i in range(30)])
    selection = pyui.State(default=list)

    def create_row(self):
        self.dynamic_items.value = self.dynamic_items.value + ["New Item"]

    def clear(self):
        self.dynamic_items.value = []
        self.selection.value = []

    def content(self):
        # fmt: off
        yield pyui.HStack(alignment=pyui.Alignment.LEADING, spacing=20)(
            pyui.VStack(spacing=10, alignment=pyui.Alignment.LEADING)(
                pyui.ScrollView()(
                    pyui.List(selection=self.selection)(
                        pyui.Text("First Row"),
                        pyui.ForEach(self.dynamic_items.value, lambda item: (
                            pyui.Text(item),
                        )),
                    ),
                ).priority(pyui.Priority.HIGH),
                pyui.HStack()(
                    pyui.Spacer(),
                    pyui.Button("Clear", action=self.clear),
                    pyui.Button("+", action=self.create_row),
                ),
            ),
            pyui.Text("Selected rows: {}".format(self.selection.value)),
            pyui.Spacer(),
        )
        # fmt: on


class DemoView(pyui.View):
    def content(self):
        # fmt: off
        yield pyui.TabView()(
            TimestampView().padding(20).item("Time"),
            BarChartView().padding(20).item("Bar Chart"),
            ImageSizerView().padding(20).item("Image"),
            FormView().padding(20).item("Form"),
            ListView().padding(20).item("Lists"),
        )
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.temp.PyUI")
    app.window("PyUI Demo", DemoView())
    app.run()
