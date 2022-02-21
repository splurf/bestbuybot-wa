class Counter:
    def __init__(self, content: str = None, age=250):
        self.content = content
        self.age = age
        self.t = 0
        self.v = 0

    def run(self) -> bool:
        if self.content != None:
            Counter.rprint(self.content + "." * self.v)

        if self.v == 2:
            self.t += 1
            self.v = 0
            return False
        else:
            self.v += 1
            return True

    def old(self) -> bool:
        if self.t == self.age:
            self.t = 0
            return True
        else:
            return False

    @staticmethod
    def rprint(content: str):
        print(content + " " * 25, end="\r")
