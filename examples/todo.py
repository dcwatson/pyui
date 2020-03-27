import pyui

ITEM_ACTIVE = lambda view: view
ITEM_COMPLETE = lambda view: view.color(255, 255, 255, 128)


class TodoItem:
    def __init__(self, text, complete=False):
        self.text = text
        self.complete = complete


class TodoList(pyui.Observable):
    def __init__(self):
        self.items = []

    def add(self, title):
        self.items.append(TodoItem(title))
        self.changed()

    def toggle(self, item):
        item.complete = not item.complete
        self.changed()

    def delete(self, item):
        self.items.remove(item)
        self.changed()

    def clear_complete(self):
        self.items = [item for item in self.items if not item.complete]
        self.changed()

    @property
    def remaining(self):
        return len([item for item in self.items if not item.complete])

    def filter(self, which):
        for item in self.items:
            if which == 0:
                yield item
            elif bool(which - 1) == item.complete:
                yield item


class TodoMVC(pyui.View):
    items = pyui.State(default=TodoList)
    new_item = pyui.State(default="")
    selected_filter = pyui.State(default=0)

    @property
    def selected(self):
        yield from self.items.filter(self.selected_filter.value)

    @property
    def remaining_text(self):
        remain = self.items.remaining
        word = "item" if remain == 1 else "items"
        return "{} {} left".format(remain, word)

    async def add(self, title):
        self.items.add(title)
        self.new_item.value = ""

    def content(self):
        # fmt: off
        yield pyui.VStack(alignment=pyui.Alignment.LEADING)(
            pyui.TextField(self.new_item, "What needs to be done?", action=self.add),
            pyui.List(self.selected, builder=lambda item: (
                pyui.HStack()(
                    pyui.Toggle(item.complete, action=(self.items.toggle, item)),
                    pyui.Text(item.text).modify(ITEM_COMPLETE if item.complete else ITEM_ACTIVE),
                    pyui.Spacer(),
                    pyui.Button(pyui.Icon("times"), action=(self.items.delete, item)).font(size=12)
                )
            )).priority(pyui.Priority.HIGH),
            pyui.HStack(
                pyui.Text(self.remaining_text),
                pyui.Spacer(),
                # TODO: would be nice to pass SegmentedButton an enum?
                pyui.SegmentedButton(self.selected_filter)(
                    pyui.Text("All"),
                    pyui.Text("Active"),
                    pyui.Text("Completed"),
                ).priority("high"),
                pyui.Spacer(),
                pyui.Button("Clear Completed", action=self.items.clear_complete)
            )
        ).padding(20)
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("net.pyui.TodoMVC")
    app.window("TodoMVC", TodoMVC())
    app.run()
