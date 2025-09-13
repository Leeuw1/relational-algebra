from main import *


def same(a, b):
    return a.column_names == b.column_names and set(a.tuples) == set(b.tuples)


def run_set_operator_tests():
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


def run_unary_operator_tests():
    a = Relation(("ID", "Department", "Manager"), [])
    b = Relation(("ID", "Department", "Manager"), [])
    c = Relation(("ID", "Manager"), [])
    for i in range(100):
        t = (IntegerLiteral(i), StringLiteral(f"dept{i}"), StringLiteral(f"manager{i}"))
        a.tuples.append(t)
        if i < 50:
            b.tuples.append(t)
        t = (IntegerLiteral(i), StringLiteral(f"manager{i}"))
        c.tuples.append(t)

    condition = BinaryExpression(Identifier("ID"), IntegerLiteral(50), "<")
    assert same(select(a, condition), b)
    assert same(project(a, ["ID", "Manager"]), c)


def run_join_tests():
    a = Relation(("Student", "CourseID"), [])
    b = Relation(("CourseID", "Code"), [])
    c = Relation(("Student", "CourseID", "Code"), [])
    for i in range(100):
        t = (StringLiteral(f"student{i}"), IntegerLiteral(i))
        a.tuples.append(t)
        t = (IntegerLiteral(i), StringLiteral(f"course{i}"))
        b.tuples.append(t)
        t = (
            StringLiteral(f"student{i}"),
            IntegerLiteral(i),
            StringLiteral(f"course{i}"),
        )
        c.tuples.append(t)
    for i in range(20):
        t = (StringLiteral(f"extra_student{i}"), IntegerLiteral(1000 + i))
        a.tuples.append(t)
        t = (IntegerLiteral(2000 + i), StringLiteral(f"extra_course{i}"))
        b.tuples.append(t)

    assert same(natural_join(a, b), c)

    a = Relation(("Student", "CourseID"), [])
    b = Relation(("ID", "Code"), [])
    c = Relation(("Student", "CourseID", "ID", "Code"), [])
    for i in range(100):
        t = (StringLiteral(f"student{i}"), IntegerLiteral(i))
        a.tuples.append(t)
        t = (IntegerLiteral(i), StringLiteral(f"course{i}"))
        b.tuples.append(t)
        t = (
            StringLiteral(f"student{i}"),
            IntegerLiteral(i),
            IntegerLiteral(i),
            StringLiteral(f"course{i}"),
        )
        c.tuples.append(t)
    for i in range(20):
        t = (StringLiteral(f"extra_student{i}"), IntegerLiteral(1000 + i))
        a.tuples.append(t)
        t = (IntegerLiteral(2000 + i), StringLiteral(f"extra_course{i}"))
        b.tuples.append(t)

    condition = BinaryExpression(Identifier("CourseID"), Identifier("ID"), "==")
    assert same(theta_join(a, b, condition), c)

    for i in range(20):
        t = (
            StringLiteral(f"extra_student{i}"),
            IntegerLiteral(1000 + i),
            "NULL",
            "NULL",
        )
        c.tuples.append(t)
    assert same(theta_join(a, b, condition, left_outer=True), c)

    c.tuples = c.tuples[:-20]
    for i in range(20):
        t = (
            "NULL",
            "NULL",
            IntegerLiteral(2000 + i),
            StringLiteral(f"extra_course{i}"),
        )
        c.tuples.append(t)
    assert same(theta_join(a, b, condition, right_outer=True), c)

    for i in range(20):
        t = (
            StringLiteral(f"extra_student{i}"),
            IntegerLiteral(1000 + i),
            "NULL",
            "NULL",
        )
        c.tuples.append(t)
    assert same(theta_join(a, b, condition, left_outer=True, right_outer=True), c)


def run_operator_tests():
    run_set_operator_tests()
    run_unary_operator_tests()
    run_join_tests()


run_operator_tests()
print("All tests passed")
