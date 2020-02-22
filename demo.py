import datetime

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
                pyui.Image("images/python.svg").height(30),
                pyui.Text("Update"),
            )
        )
        # fmt: on


def random_bars():
    import random

    return [random.randint(20, 400) for i in range(10)]


class BarChartView(pyui.View):
    bars = pyui.State(default=random_bars)

    def randomize(self):
        self.bars = random_bars()

    def content(self):
        # fmt: off
        bars = [pyui.Rectangle(height=h) for h in self.bars.value]
        yield pyui.VStack(spacing=20)(
            pyui.Text("Bar Chart"),
            pyui.Spacer(),
            pyui.HStack(alignment=pyui.Alignment.TRAILING)(*bars),
            pyui.Button("Randomize", action=self.randomize),
        )
        # fmt: on


class ImageSizerView(pyui.View):
    scale = pyui.State(int, default=100)

    def content(self):
        # fmt: off
        yield pyui.VStack(
            pyui.Slider(self.scale, 0, 100),
            pyui.Image("images/python.png").scale(self.scale.value / 100),
        )
        # fmt: on


class DemoView(pyui.View):
    def content(self):
        # fmt: off
        yield pyui.TabView()(
            TimestampView().pad(40).item("Timestamp"),
            BarChartView().pad(40).item("Bar Chart"),
            ImageSizerView().pad(40).item("Image"),
        ).pad(40)
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.temp.PyUI")
    app.window("PyUI Demo", DemoView())
    app.run()
