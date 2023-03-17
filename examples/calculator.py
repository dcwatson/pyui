import sdl2

import pyui


def BTN_DEFAULT(view):
    return view.background(128, 128, 128)


def BTN_TOP(view):
    return view.background(80, 80, 80)


def BTN_OPERATOR(view):
    return view.background(200, 148, 20)


class CalcButton(pyui.View):
    interactive = True

    def __init__(self, label, action, mod=None):
        super().__init__()
        self.label = label
        self.action = action
        self.mod = mod or BTN_DEFAULT

    def content(self):
        yield pyui.Rectangle()(pyui.Text(self.label)).modify(self.mod)

    async def click(self, pt):
        if self.action:
            self.action(self.label)


class CalculatorView(pyui.View):
    result = pyui.State(str, default="0")
    formula = pyui.State(str, default="")

    async def textinput(self, ch):
        if ch in "0123456789.+-/*()":
            self.add(ch)
        elif ch.lower() == "c":
            self.clear()
        elif ch == "=":
            self.compute()

    async def keydown(self, key, mods):
        if key == sdl2.SDLK_RETURN:
            self.compute()

    def add(self, ch):
        self.formula = self.formula.value + ch

    def group(self, ch):
        self.formula = "(" + self.formula.value + ")"

    def compute(self, ch=None):
        try:
            num = eval(self.formula.value)
            if isinstance(num, float):
                self.result = "{:.3f}".format(num)
            elif isinstance(num, int):
                self.result = str(num)
            else:
                self.result = "NOPE"
        except Exception:
            self.result = "???"

    def clear(self, ch=None):
        self.formula = ""
        self.result = "0"

    def content(self):
        yield pyui.VStack(spacing=0)(
            pyui.HStack()(
                pyui.Spacer(),
                pyui.Text(self.formula.value)
                .font(size=11)
                .color(180, 180, 180)
                .padding(5, 10, 0, 5),
            ),
            pyui.HStack()(
                pyui.Spacer(),
                pyui.Text(self.result.value).font(size=42).padding(5),
            ),
            pyui.Grid(axis=pyui.Axis.VERTICAL, spacing=2, num=4, cram=True)(
                CalcButton("C", self.clear, BTN_TOP),
                CalcButton("(", self.add, BTN_TOP),
                CalcButton(")", self.add, BTN_TOP),
                CalcButton("/", self.add, BTN_OPERATOR),
                CalcButton("7", self.add),
                CalcButton("8", self.add),
                CalcButton("9", self.add),
                CalcButton("*", self.add, BTN_OPERATOR),
                CalcButton("4", self.add),
                CalcButton("5", self.add),
                CalcButton("6", self.add),
                CalcButton("-", self.add, BTN_OPERATOR),
                CalcButton("1", self.add),
                CalcButton("2", self.add),
                CalcButton("3", self.add),
                CalcButton("+", self.add, BTN_OPERATOR),
                CalcButton("(…)", self.group),
                CalcButton("0", self.add),
                CalcButton(".", self.add),
                CalcButton("=", self.compute, BTN_OPERATOR),
            ),
        )


if __name__ == "__main__":
    app = pyui.Application("io.temp.Calculator")
    app.window("Calculator", CalculatorView(), width=250, height=300, resize=True)
    app.run()
