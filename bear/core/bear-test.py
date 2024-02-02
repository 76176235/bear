from bear import command


def process(self, line):
    line = line.strip()
    return line + 'a'


if __name__ == '__main__':
    cm = command.MultiIO('/tmp/2', 5)
    a = cm.run(process)
    print(a)
    pass

