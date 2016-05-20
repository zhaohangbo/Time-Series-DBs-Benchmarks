from itertools import cycle, islice
import sys


def roundrobin(*iterables):
    "roundrobin(['10.10','10.11'], ['10.12'], ['10.13']) --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))



if __name__ == "__main__":
    # Main runner
    roundRobin= roundrobin(['10.10','10.11'], ['10.12'], ['10.13'])

    while roundRobin.h:
        try:
            print roundRobin.next()
        except Exception as e:
            roundRobin = roundrobin(['10.10','10.11'], ['10.12'], ['10.13'])

    # iterables=['ABC', 'D', 'EF']
    # for it in iterables:
    #     for i in iter(it):
    #         print i
    sys.exit(1)