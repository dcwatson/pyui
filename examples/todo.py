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

    @pyui.mutating
    def add(self, title):
        self.items.append(TodoItem(title))

    @pyui.mutating
    def toggle(self, checked, item):
        item.complete = checked

    @pyui.mutating
    def toggle_all(self, checked):
        for item in self.items:
            item.complete = checked

    @pyui.mutating
    def delete(self, item):
        self.items.remove(item)

    @pyui.mutating
    def clear_complete(self):
        self.items = [item for item in self.items if not item.complete]

    @property
    def all_complete(self):
        return len(self.items) > 0 and all(item.complete for item in self.items)

    @property
    def any_complete(self):
        return any(item.complete for item in self.items)

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
            pyui.HStack()(
                pyui.Toggle(self.items.all_complete, action=self.items.toggle_all),
                pyui.TextField(self.new_item, "What needs to be done?", action=self.add),
            ),
            pyui.ScrollView()(
                pyui.List(self.selected, builder=lambda item: (
                    pyui.HStack()(
                        pyui.Toggle(item.complete, label=item.text, action=(self.items.toggle, item))
                            .modify(ITEM_COMPLETE if item.complete else ITEM_ACTIVE),
                        pyui.Spacer(),
                        pyui.Button(action=(self.items.delete, item), asset=None)(
                            pyui.Icon("trash-alt")
                        ).font(size=12).padding(0)
                    )
                )),
            ).priority(pyui.Priority.HIGH),
            pyui.HStack(
                pyui.Text(self.remaining_text),
                pyui.Button(action=self.items.clear_complete, asset=None)(
                    pyui.Text("Clear Completed").color(60, 150, 255)
                ).padding(5).disable(not self.items.any_complete),
                pyui.Spacer(),
                # TODO: would be nice to pass SegmentedButton an enum?
                pyui.SegmentedButton(self.selected_filter)(
                    pyui.Text("All"),
                    pyui.Text("Active"),
                    pyui.Text("Completed"),
                ),
            )
        ).padding(20)
        # fmt: on


if __name__ == "__main__":
    app = pyui.Application("net.pyui.TodoMVC")
    app.window("TodoMVC", TodoMVC(), height=320)
    app.run()
