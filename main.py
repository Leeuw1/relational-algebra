class BinaryExpression:
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator

    def __repr__(self):
        return f"BinaryExpression{{{self.left} {self.operator} {self.right}}}"

    def evaluate(self, assignments):
        left_value = self.left.evaluate(assignments)
        right_value = self.right.evaluate(assignments)
        # TODO: some type checking is probably required
        # TODO: implement all operators
        match self.operator:
            case ">":
                return left_value > right_value
            case "<":
                return left_value < right_value


class UnaryExpression:
    def __init__(self, expression, operator):
        self.expression = expression
        self.operator = operator

    def __repr__(self):
        return f"UnaryExpression{{{self.operator} {self.expression}}}"

    def evaluate(self, assignments):
        value = self.expression.evaluate(assignments)
        # TODO: implement all operators
        match self.operator:
            case ("select", condition):
                return select(value, condition)


class Identifier(str):
    def evaluate(self, assignments):
        return assignments[self]


class IntegerLiteral(int):
    def evaluate(self, assignments):
        return self


class Relation:
    def __init__(self, column_names, tuples):
        self.column_names = column_names
        self.tuples = tuples

    def __repr__(self):
        return f"Relation{{{self.column_names} {self.tuples}}}"


def test_condition(column_names, tup, condition):
    assignments = dict()
    for name, value in zip(column_names, tup):
        assignments[name] = value
    return condition.evaluate(assignments)


def select(relation, condition):
    return Relation(
        relation.column_names,
        [
            tup
            for tup in relation.tuples
            if test_condition(relation.column_names, tup, condition)
        ],
    )


class ParseException(Exception):
    pass


def parse_binary_expression(tokens):
    left = parse_unary_expression(tokens)
    try:
        operator = parse_binary_operator(tokens)
        right = parse_binary_expression(tokens)
    except ParseException:
        return left
    return BinaryExpression(left, right, operator)


def parse_unary_expression(tokens):
    try:
        operator = parse_unary_operator(tokens)
    except ParseException:
        return parse_primary_expression(tokens)
    expression = parse_unary_expression(tokens)
    return UnaryExpression(expression, operator)


def parse_primary_expression(tokens):
    try:
        parse_token(tokens, "(")
        expression = parse_binary_expression(tokens)
        parse_token(tokens, ")")
        return expression
    except ParseException:
        return parse_identifier(tokens)


def parse_binary_operator(tokens):
    try:
        return parse_token(tokens, "<")
    except ParseException:
        return parse_token(tokens, ">")


def parse_unary_operator(tokens):
    parse_token(tokens, "select")
    condition = parse_binary_expression(tokens)
    return ("select", condition)


# TODO: keywords, operators, punctuation cannot be used as identifiers
def parse_identifier(tokens):
    if len(tokens) == 0:
        raise ParseException
    return tokens.pop(0)


def parse_token(tokens, token):
    if len(tokens) == 0:
        raise ParseException
    if tokens[0] == token:
        return tokens.pop(0)
    raise ParseException


# TODO: read tables as input
global_assignments = {
    "Employees": Relation(
        ("Name", "Age", "Department"),
        [("Alice", 32, "Finance"), ("Bob", 30, "Finance")],
    )
}


def main():
    # TODO: read queries as input
    tokens = [
        "select",
        Identifier("Age"),
        ">",
        IntegerLiteral(30),
        Identifier("Employees"),
    ]
    syntax_tree = parse_binary_expression(tokens)
    print(global_assignments["Employees"])
    print(syntax_tree)
    print(syntax_tree.evaluate(global_assignments))


if __name__ == "__main__":
    main()
