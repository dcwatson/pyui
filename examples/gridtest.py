import pyui


class ItemGridView(pyui.View):
    def content(self):
        # fmt: off
        yield pyui.ScrollView(axis=self.axis)(
            pyui.Grid(num=self.num, size=self.size, axis=self.axis, flex=self.flex)(
                pyui.ForEach(range(self.item_count), lambda num: (
                    pyui.Rectangle()(
                        pyui.Text(num + 1).color(255, 255, 255)
                    ).background(120, 120, 120).radius(5).animate()
                ))
            )
        )
        # fmt: on


class GridTest(pyui.View):
    axis = pyui.State(default=1)
    item_count = pyui.State(int, default=50)
    size = pyui.State(default=100)
    num = pyui.State(default=4)
    size_or_num = pyui.State(default=0)
    flex = pyui.State(default=0)

    def content(self):
        # fmt: off
        if self.size_or_num.value == 0:
            size = None
            num = self.num.value
        else:
            size = self.size.value
            num = None
        yield pyui.HStack(alignment=pyui.Alignment.LEADING)(
            pyui.VStack(alignment=pyui.Alignment.LEADING)(
                pyui.Text("Axis"),
                pyui.SegmentedButton(self.axis)(
                    pyui.Text(pyui.Axis.HORIZONTAL.name),
                    pyui.Text(pyui.Axis.VERTICAL.name),
                ),
                pyui.HStack(
                    pyui.Text("Number of items"),
                    pyui.Spacer(),
                    pyui.Text(self.item_count.value).color(128, 128, 128).priority("high"),
                ),
                pyui.Slider(self.item_count, maximum=200),
                pyui.Text("Fill rows/columns by"),
                pyui.SegmentedButton(self.size_or_num)(
                    pyui.Text("Number"),
                    pyui.Text("Size"),
                ),
                pyui.HStack(
                    pyui.Text("Items per row/column"),
                    pyui.Spacer(),
                    pyui.Text(self.num.value).color(128, 128, 128).priority("high"),
                ),
                pyui.Slider(self.num, minimum=1, maximum=10).disable(self.size_or_num.value == 1),
                pyui.HStack(
                    pyui.Text("Item size"),
                    pyui.Spacer(),
                    pyui.Text(self.size.value).color(128, 128, 128).priority("high"),
                ),
                pyui.Slider(self.size, minimum=50, maximum=200).disable(self.size_or_num.value == 0),
                pyui.Text("Adjust size to fit"),
                pyui.SegmentedButton(self.flex)(
                    pyui.Text("No"),
                    pyui.Text("Yes"),
                ).disable(self.size_or_num.value == 0),
            ).padding(10).size(width=300),
            ItemGridView(
                item_count=self.item_count.value,
                size=size,
                num=num,
                axis=self.axis.value,
                flex=self.flex.value,
            ),
        )
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("io.temp.GridTest")
    app.window("Grid Tester", GridTest())
    app.run()
