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
            case "union":
                return union(left_value, right_value)
            case "intersect":
                return intersect(left_value, right_value)
            case "minus":
                return subtract(left_value, right_value)


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
            case ("project", column_names):
                return project(value, column_names)


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


def select(relation, condition):
    tuples = []
    assignments = {}

    for tup in relation.tuples:
        for i in range(len(relation.column_names)):
            name = relation.column_names[i]
            value = tup[i]
            assignments[name] = value
        if condition.evaluate(assignments):
            tuples.append(tup)

    return Relation(relation.column_names, tuples)


def project(relation, column_names):
    indices = []
    for name in column_names:
        indices.append(relation.column_names.index(name))
    indices.sort()

    column_names_sorted = []
    for i in indices:
        column_names_sorted.append(relation.column_names[i])

    tuples = []
    for tup in relation.tuples:
        new_tuple = tuple()
        for i in indices:
            new_tuple += (tup[i],)
        tuples.append(new_tuple)

    return Relation(column_names_sorted, tuples)


def contains(tuples, tup):
    for t in tuples:
        if t == tup:
            return True
    return False


class ColumnNamesMismatchException(Exception):
    pass


def union(relation_a, relation_b):
    if relation_a.column_names != relation_b.column_names:
        raise ColumnNamesMismatchException
    tuples = relation_a.tuples.copy()
    for tup in relation_b.tuples:
        if not contains(relation_a.tuples, tup):
            tuples.append(tup)
    return Relation(relation_a.column_names, tuples)


def intersect(relation_a, relation_b):
    if relation_a.column_names != relation_b.column_names:
        raise ColumnNamesMismatchException
    tuples = []
    for tup in relation_a.tuples:
        if contains(relation_b.tuples, tup):
            tuples.append(tup)
    return Relation(relation_a.column_names, tuples)


def subtract(relation_a, relation_b):
    if relation_a.column_names != relation_b.column_names:
        raise ColumnNamesMismatchException
    tuples = []
    for tup in relation_a.tuples:
        if not contains(relation_b.tuples, tup):
            tuples.append(tup)
    return Relation(relation_a.column_names, tuples)


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
        pass
    try:
        return parse_token(tokens, ">")
    except ParseException:
        pass
    try:
        return parse_token(tokens, "union")
    except ParseException:
        pass
    try:
        return parse_token(tokens, "intersect")
    except ParseException:
        return parse_token(tokens, "minus")


def parse_unary_operator(tokens):
    try:
        parse_token(tokens, "select")
        condition = parse_binary_expression(tokens)
        return ("select", condition)
    except ParseException:
        parse_token(tokens, "project")
        column_names = parse_column_names(tokens)
        return ("project", column_names)


# TODO: is the minimum number of columns zero or one?
def parse_column_names(tokens):
    identifiers = [parse_identifier(tokens)]
    while True:
        try:
            parse_token(tokens, ",")
        except ParseException:
            return identifiers
        identifiers.append(parse_identifier(tokens))


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


KEYWORDS = [
    "select",
    "project",
    "union",
    "intersect",
    "minus",
]


# TODO: negative numbers
def tokenize(input_str):
    tokens = []
    while len(input_str) > 0:
        c = input_str[0]
        if c.isalpha() or c == "_":
            word, input_str = read_word(input_str)
            if word in KEYWORDS:
                tokens.append(word)
            else:
                tokens.append(Identifier(word))
            continue
        if c.isdigit():
            number, input_str = read_number(input_str)
            tokens.append(IntegerLiteral(int(number)))
            continue
        if c in ["<", ">", ","]:
            tokens.append(c)
            input_str = input_str[1:]
            continue
        if c.isspace():
            input_str = input_str[1:]
            continue
        raise Exception("Unknown character")
    return tokens


def read_word(input_str):
    i = 0
    while i < len(input_str):
        c = input_str[i]
        if not c.isalnum() and c != "_":
            return input_str[:i], input_str[i:]
        i += 1
    return input_str, ""


def read_number(input_str):
    i = 0
    while i < len(input_str):
        c = input_str[i]
        if not c.isdigit():
            return input_str[:i], input_str[i:]
        i += 1
    return input_str, ""


# TODO: read tables as input
global_assignments = {
    "Employees": Relation(
        ("Name", "Age", "Department"),
        [("Alice", 32, "Finance"), ("Bob", 30, "Finance")],
    ),
    "Employees2": Relation(
        ("Name", "Age", "Department"),
        [("Charlie", 20, "H.R."), ("Bob", 30, "Finance")],
    ),
}


def main():
    try:
        while True:
            tokens = tokenize(input(": "))
            syntax_tree = parse_binary_expression(tokens)
            print(syntax_tree.evaluate(global_assignments))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
