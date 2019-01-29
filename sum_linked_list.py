import sys


class Node:
    def __init__(self, value):
        self.value = value
        self.next_node = None

    def __str__(self):
        return f"Node[{self.value}]"


def dump(h: Node):
    while h is not None:
        print(f"{h}->", end='')
        h = h.next_node
    print('')


def build_linked_list(n_str):
    last = None
    for c_str in n_str:
        n = Node(int(c_str))
        if last is not None:
            n.next_node = last
        last = n
    return last


def sum_lists(n1: Node, n2: Node) -> Node:

    head = None
    last = None
    rem = 0

    while n1 is not None or n2 is not None or rem != 0:
        def safe_val(node):
            return (node.value, node.next_node) if node is not None else (0, None)
        v1, n1 = safe_val(n1)
        v2, n2 = safe_val(n2)
        tot = v1 + v2 + rem
        rem = tot // 10
        n = Node(tot % 10)
        if head is None:
            head = n
        if last is not None:
            last.next_node = n
        last = n

    return head


def main(args):
    print(args)
    res = [build_linked_list(n_str) for n_str in args]
    [dump(h) for h in res]
    sum_list = sum_lists(res[0], res[1])
    dump(sum_list)


if __name__ == "__main__":
    main(sys.argv[1:])
