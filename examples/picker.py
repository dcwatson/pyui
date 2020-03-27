import pyui


class PickerTest(pyui.View):
    text = pyui.State(default="")
    selected = pyui.State(default=0)

    def content(self):
        # fmt: off
        yield pyui.VStack()(
            pyui.TextField(self.text, placeholder="Some text"),
            pyui.Picker(selection=self.selected)(
                pyui.Text("Item One"),
                pyui.Text("Item Two"),
                pyui.Text("Item Three"),
            )
        ).padding(20)
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.temp.PickerTest")
    app.window("Picker Test", PickerTest())
    app.run()
