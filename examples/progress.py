import pyui


class ProgressTest(pyui.View):
    current = pyui.State(default=50)

    def content(self):
        yield pyui.VStack()(
            pyui.Slider(self.current),
            pyui.ProgressBar(self.current),
            pyui.Text(self.current.value),
        ).padding(20)


if __name__ == "__main__":
    app = pyui.Application("io.temp.ProgressTest")
    app.window("Progress Test", ProgressTest(), width=640, height=200)
    app.run()
