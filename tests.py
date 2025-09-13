from main import *


def same(a, b):
    return a.column_names == b.column_names and set(a.tuples) == set(b.tuples)


def run_operator_tests():
    a = Relation(("Name", "Age"), [])
    b = Relation(("Name", "Age"), [])
    c = Relation(("Name", "Age"), [])
    for i in range(100):
        t = (StringLiteral(f"a{i}"), IntegerLiteral(i))
        a.tuples.append(t)
        c.tuples.append(t)
        t = (StringLiteral(f"b{i}"), IntegerLiteral(i))
        b.tuples.append(t)
        c.tuples.append(t)

    assert same(union(a, b), c)
    assert same(union(a, c), c)
    assert same(union(b, c), c)
    assert same(subtract(c, a), b)
    assert same(subtract(c, b), a)
    assert same(subtract(a, a), Relation(("Name", "Age"), []))
    assert same(intersect(a, c), a)
    assert same(intersect(b, c), b)
    assert same(intersect(c, c), c)


run_operator_tests()
print("All tests passed")
