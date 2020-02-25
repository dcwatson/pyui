import datetime
import random

import pyui


class TimestampView(pyui.View):
    timestamp = pyui.State(datetime.datetime, default=datetime.datetime.now)

    def update_timestamp(self):
        self.timestamp = datetime.datetime.now()

    def content(self):
        # fmt: off
        yield pyui.HStack()(
            pyui.Text(self.timestamp.value.strftime("%H:%M:%S.%f")),
            pyui.Button(action=self.update_timestamp)(
                pyui.Image("images/python.svg").height(14),
                pyui.Text("Update"),
            )
        )
        # fmt: on


def random_bars(num=10):
    return [random.randint(20, 200) for i in range(num)]


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
                pyui.ForEach(self.bars.value, lambda height: (
                    pyui.Rectangle(height=height).background(
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    )
                )),
            ),
            pyui.HStack()(
                pyui.Button("Fewer Bars", action=self.fewer_bars),
                pyui.Button("Randomize", action=self.randomize),
                pyui.Button("More Bars", action=self.more_bars),
            ),
        )
        # fmt: on


class ImageSizerView(pyui.View):
    scale = pyui.State(int, default=50)

    def content(self):
        # fmt: off
        yield pyui.VStack(
            pyui.Slider(self.scale, 0, 100),
            pyui.Image("images/python.png").scale(self.scale.value / 100),
        )
        # fmt: on


class FormView(pyui.View):
    languages = pyui.State(default=["Python", "Jengascript", "Other"])
    selection = pyui.State(default=0)

    def new_language(self):
        self.languages = self.languages.value + ["New"]

    def content(self):
        # fmt: off
        yield pyui.VStack(spacing=20)(
            pyui.Button("New Language", action=self.new_language),
            pyui.ForEach(self.languages.value, lambda lang: (
                pyui.VStack(alignment=pyui.Alignment.LEADING, spacing=5)(
                    pyui.Text(lang),
                    pyui.TextField("Description for {}".format(lang)),
                    pyui.SegmentedButton(self.selection)(
                        pyui.ForEach(self.languages.value, lambda lang: (
                            pyui.Text(lang)
                        ))
                    )
                )
            ))
        )
        # fmt: on


class ListView(pyui.View):
    dynamic_items = pyui.State(default=list)
    selection = pyui.State(default=list)

    def create_row(self):
        self.dynamic_items.value = self.dynamic_items.value + ["New Item"]

    def clear(self):
        self.dynamic_items.value = []
        self.selection.value = []

    def content(self):
        # fmt: off
        yield pyui.HStack()(
            pyui.VStack(spacing=10, alignment=pyui.Alignment.LEADING)(
                pyui.List(selection=self.selection)(
                    pyui.Text("First Row"),
                    pyui.ForEach(self.dynamic_items.value, lambda item: (
                        pyui.Text(item),
                    )),
                ),
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
            TimestampView().pad(20).item("Timestamp"),
            BarChartView().pad(20).item("Bar Chart"),
            ImageSizerView().pad(20).item("Image"),
            FormView().pad(20).item("Form"),
            ListView().pad(20).item("Lists"),
        ).pad(20)
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.temp.PyUI")
    app.window("PyUI Demo", DemoView())
    app.run()
