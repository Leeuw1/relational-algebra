import sys

COMPARISON_OPERATORS = [
    ">",
    "<",
    ">=",
    "<=",
    "==",
    "!=",
]


RELATIONAL_OPERATORS = [
    "union",
    "intersect",
    "minus",
    "join",
    "theta_join",
    "left_join",
    "right_join",
    "full_join",
]


def type_check(op, value):
    if (
        op in COMPARISON_OPERATORS
        and not isinstance(value, IntegerLiteral)
        and not isinstance(value, StringLiteral)
    ):
        raise EvaluationException(
            f"Operator {op} expected integers or strings but got type: {type(value)}"
        )
    if op in RELATIONAL_OPERATORS and not isinstance(value, Relation):
        raise EvaluationException(
            f"Operator {op} expected relations but got type: {type(value)}"
        )
    if op in ["&&", "||"] and not isinstance(value, bool):
        raise EvaluationException(
            f"Operator {op} expected booleans but got type: {type(value)}"
        )


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
        if type(left_value) != type(right_value):
            raise EvaluationException(f"Type mismatch for operands of {self.operator}")
        type_check(self.operator, left_value)
        match self.operator:
            case ">":
                return left_value > right_value
            case "<":
                return left_value < right_value
            case ">=":
                return left_value >= right_value
            case "<=":
                return left_value <= right_value
            case "==":
                return left_value == right_value
            case "!=":
                return left_value != right_value
            case "&&":
                return left_value and right_value
            case "||":
                return left_value or right_value
            case "union":
                return union(left_value, right_value)
            case "intersect":
                return intersect(left_value, right_value)
            case "minus":
                return subtract(left_value, right_value)
            case "join":
                return natural_join(left_value, right_value)
            case ("theta_join", condition):
                return theta_join(left_value, right_value, condition)
            case ("left_join", condition):
                return theta_join(left_value, right_value, condition, left_outer=True)
            case ("right_join", condition):
                return theta_join(left_value, right_value, condition, right_outer=True)
            case ("full_join", condition):
                return theta_join(
                    left_value,
                    right_value,
                    condition,
                    left_outer=True,
                    right_outer=True,
                )


class UnaryExpression:
    def __init__(self, expression, operator):
        self.expression = expression
        self.operator = operator

    def __repr__(self):
        return f"UnaryExpression{{{self.operator} {self.expression}}}"

    def evaluate(self, assignments):
        value = self.expression.evaluate(assignments)
        if self.operator == "!" and not isinstance(value, bool):
            raise EvaluationException(
                f"Operator ! expected a boolean but got type: {type(value)}"
            )
        if self.operator in ["select", "project"] and not isinstance(value, Relation):
            raise EvaluationException(
                f"Operator {self.operator} expected a relation but got type: {type(value)}"
            )
        match self.operator:
            case "!":
                return not value
            case "is_null":
                return value == "NULL"
            case ("select", condition):
                return select(value, condition)
            case ("project", column_names):
                return project(value, column_names)


class EvaluationException(Exception):
    pass


class Identifier(str):
    def evaluate(self, assignments):
        try:
            return assignments[self]
        except KeyError:
            pass
        raise EvaluationException(f"Unknown identifier '{self}'")


class IntegerLiteral(int):
    def evaluate(self, assignments):
        return self


class StringLiteral(str):
    def evaluate(self, assignments):
        return self


class Relation:
    def __init__(self, column_names, tuples):
        self.column_names = column_names
        self.tuples = tuples

    def __repr__(self):
        widths = [len(name) for name in self.column_names]
        for tup in self.tuples:
            for i, value in enumerate(tup):
                length = len(str(value))
                if length > widths[i]:
                    widths[i] = length

        line = "".join("+" + "-" * (w + 2) for w in widths) + "+\n"
        output = line
        output += (
            "".join(
                f"| {name:<{widths[i]}} " for i, name in enumerate(self.column_names)
            )
            + "|\n"
        )
        output += line
        for tup in self.tuples:
            output += (
                "".join(f"| {value:<{widths[i]}} " for i, value in enumerate(tup))
                + "|\n"
            )
        output += line
        return output[:-1]


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


def index_of(tup, value):
    for i, x in enumerate(tup):
        if x == value:
            return i
    raise ValueError


def project(relation, column_names):
    indices = []
    for name in column_names:
        indices.append(index_of(relation.column_names, name))
    indices.sort()

    column_names_sorted = tuple()
    for i in indices:
        column_names_sorted += (relation.column_names[i],)

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


def union(relation_a, relation_b):
    if relation_a.column_names != relation_b.column_names:
        raise EvaluationException("Column names do not match")
    tuples = relation_a.tuples.copy()
    for tup in relation_b.tuples:
        if not contains(relation_a.tuples, tup):
            tuples.append(tup)
    return Relation(relation_a.column_names, tuples)


def intersect(relation_a, relation_b):
    if relation_a.column_names != relation_b.column_names:
        raise EvaluationException("Column names do not match")
    tuples = []
    for tup in relation_a.tuples:
        if contains(relation_b.tuples, tup):
            tuples.append(tup)
    return Relation(relation_a.column_names, tuples)


def subtract(relation_a, relation_b):
    if relation_a.column_names != relation_b.column_names:
        raise EvaluationException("Column names do not match")
    tuples = []
    for tup in relation_a.tuples:
        if not contains(relation_b.tuples, tup):
            tuples.append(tup)
    return Relation(relation_a.column_names, tuples)


# NOTE: Returns None if common columns do not match
def natural_join_tuples(tuple_a, tuple_b, common_columns):
    indices = []
    for i in range(len(tuple_b)):
        indices.append(i)

    for i, j in common_columns:
        if tuple_a[i] != tuple_b[j]:
            return None
        indices[j] = None

    joined_tuple = tuple_a
    for i in indices:
        if i != None:
            joined_tuple += (tuple_b[i],)

    return joined_tuple


def natural_join(relation_a, relation_b):
    common_columns = []
    for i in range(len(relation_a.column_names)):
        try:
            name = relation_a.column_names[i]
            j = index_of(relation_b.column_names, name)
        except ValueError:
            continue
        common_columns.append((i, j))

    tuples = []
    for tuple_a in relation_a.tuples:
        for tuple_b in relation_b.tuples:
            joined_tuple = natural_join_tuples(tuple_a, tuple_b, common_columns)
            if joined_tuple != None:
                tuples.append(joined_tuple)

    column_names = natural_join_tuples(
        relation_a.column_names, relation_b.column_names, common_columns
    )
    return Relation(column_names, tuples)


def disjoint_column_names(names_a, names_b):
    for name_a in names_a:
        for name_b in names_b:
            if name_a == name_b:
                return False
    return True


def theta_join(relation_a, relation_b, condition, left_outer=False, right_outer=False):
    if not disjoint_column_names(relation_a.column_names, relation_b.column_names):
        raise EvaluationException(
            "When using join with a condition the column names must be disjoint"
        )

    tuples = []
    column_names = relation_a.column_names + relation_b.column_names
    assignments = {}

    b_matches = []
    for _ in relation_b.tuples:
        b_matches.append(False)

    if left_outer:
        null_tuple_b = tuple()
        for _ in range(len(relation_b.column_names)):
            null_tuple_b += ("NULL",)
    if right_outer:
        null_tuple_a = tuple()
        for _ in range(len(relation_a.column_names)):
            null_tuple_a += ("NULL",)

    for tuple_a in relation_a.tuples:
        match_found = False
        for i, tuple_b in enumerate(relation_b.tuples):
            joined_tuple = tuple_a + tuple_b

            for j in range(len(column_names)):
                name = column_names[j]
                value = joined_tuple[j]
                assignments[name] = value

            if condition.evaluate(assignments):
                tuples.append(joined_tuple)
                match_found = True
                b_matches[i] = True
        if left_outer and not match_found:
            tuples.append(tuple_a + null_tuple_b)

    if right_outer:
        for i, tuple_b in enumerate(relation_b.tuples):
            if not b_matches[i]:
                tuples.append(null_tuple_a + tuple_b)

    return Relation(column_names, tuples)


class ParseException(Exception):
    pass


def parse_input(tokens):
    if len(tokens) >= 2:
        if tokens[1] == "{":
            relation = parse_relation(tokens)
            if len(tokens) != 0:
                raise ParseException(f"Extraneous tokens after relation '{relation}'")
            return relation
    query = parse_binary_expression(tokens)
    if query == None:
        raise ParseException("Expected an expression")
    if len(tokens) != 0:
        raise ParseException(f"Extraneous tokens after query '{query}'")
    return query


def parse_relation(tokens):
    relation_name = parse_identifier(tokens)
    if relation_name == None:
        raise ParseException("Expected an identifier before '{'")
    parse_token(tokens, "{")
    column_names = parse_column_names(tokens)
    if column_names == None:
        raise ParseException("Expected column names after '{'")

    tuples = []
    while True:
        tup = parse_tuple(tokens)
        if tup == None:
            break
        if len(tup) != len(column_names):
            raise ParseException(
                f"Tuple size mismatch, expected {len(column_names)} values but got {len(tup)}"
            )
        tuples.append(tup)

    if parse_token(tokens, "}") == None:
        raise ParseException("Expected '}' after tuples")
    relation = Relation(column_names, tuples)
    global_assignments[relation_name] = relation
    return relation_name


def parse_binary_expression(tokens):
    left = parse_unary_expression(tokens)
    if left == None:
        return None
    operator = parse_binary_operator(tokens)
    if operator == None:
        return left
    right = parse_binary_expression(tokens)
    if right == None:
        raise ParseException(f"Expected an expression after '{operator}'")
    return BinaryExpression(left, right, operator)


def parse_unary_expression(tokens):
    operator = parse_unary_operator(tokens)
    if operator == None:
        return parse_primary_expression(tokens)
    expression = parse_unary_expression(tokens)
    if expression == None:
        raise ParseException(f"Expected an expression after '{operator}'")
    return UnaryExpression(expression, operator)


def parse_primary_expression(tokens):
    identifier = parse_identifier(tokens)
    if identifier != None:
        return identifier

    literal = parse_literal(tokens)
    if literal != None:
        return literal

    if parse_token(tokens, "(") == None:
        return None
    expression = parse_binary_expression(tokens)
    if expression == None:
        raise ParseException("Expected an expression after '('")
    if parse_token(tokens, ")") == None:
        raise ParseException("Expected ')' after '(' <expression>")
    return expression


SIMPLE_BINARY_OPERATORS = [
    "<",
    ">",
    "<=",
    ">=",
    "==",
    "!=",
    "&&",
    "||",
    "union",
    "intersect",
    "minus",
    "join",
]


CONDITION_BINARY_OPERATORS = [
    "theta_join",
    "left_join",
    "right_join",
    "full_join",
]


def parse_binary_operator(tokens):
    operator = parse_tokens(tokens, SIMPLE_BINARY_OPERATORS, can_end=True)
    if operator != None:
        return operator
    operator = parse_tokens(tokens, CONDITION_BINARY_OPERATORS, can_end=True)
    if operator == None:
        return None
    condition = parse_binary_expression(tokens)
    if condition == None:
        raise ParseException(f"Expected condition after '{operator}'")
    return (operator, condition)


def parse_unary_operator(tokens):
    operator = parse_tokens(tokens, ["!", "is_null"], can_end=True)
    if operator != None:
        return operator
    if parse_token(tokens, "select", can_end=True) != None:
        condition = parse_binary_expression(tokens)
        if condition == None:
            raise ParseException("Expected condition after 'select'")
        return ("select", condition)
    if parse_token(tokens, "project", can_end=True) != None:
        column_names = parse_column_names(tokens)
        if column_names == None:
            raise ParseException("Expected column names after 'project'")
        return ("project", column_names)
    return None


# TODO: is the minimum number of columns zero or one?
def parse_column_names(tokens):
    column_names = (parse_identifier(tokens),)
    if column_names[0] == None:
        return None
    while True:
        if parse_token(tokens, ",") == None:
            return column_names
        column_names += (parse_identifier(tokens),)
        if column_names[-1] == None:
            raise ParseException("Expected a column name after ','")


def parse_tuple(tokens):
    tup = (parse_literal(tokens),)
    if tup[0] == None:
        return None
    while True:
        if parse_token(tokens, ",") == None:
            return tup
        tup += (parse_literal(tokens),)
        if tup[-1] == None:
            raise ParseException("Expected a value after ','")


def parse_identifier(tokens):
    if len(tokens) == 0:
        tokens.extend(tokenize(input()))
        if len(tokens) == 0:
            return None
    if not isinstance(tokens[0], Identifier):
        return None
    return tokens.pop(0)


def parse_literal(tokens):
    if len(tokens) == 0:
        tokens.extend(tokenize(input()))
        if len(tokens) == 0:
            return None
    if not isinstance(tokens[0], IntegerLiteral) and not isinstance(
        tokens[0], StringLiteral
    ):
        return None
    return tokens.pop(0)


def parse_tokens(tokens, candidates, can_end=False):
    if can_end and len(tokens) == 0:
        return None
    if not can_end and len(tokens) == 0:
        tokens.extend(tokenize(input()))
        if len(tokens) == 0:
            return None
    if tokens[0] not in candidates:
        return None
    return tokens.pop(0)


def parse_token(tokens, token, can_end=False):
    if can_end and len(tokens) == 0:
        return None
    if not can_end and len(tokens) == 0:
        tokens.extend(tokenize(input()))
        if len(tokens) == 0:
            return None
    if tokens[0] != token:
        return None
    return tokens.pop(0)


KEYWORDS = [
    "select",
    "project",
    "union",
    "intersect",
    "minus",
    "join",
    "theta_join",
    "left_join",
    "right_join",
    "full_join",
    "is_null",
]


class TokenizeException(Exception):
    pass


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
        if c == '"':
            string, input_str = read_string(input_str)
            tokens.append(StringLiteral(string))
            continue
        if c in [",", "{", "}", "(", ")"]:
            tokens.append(c)
            input_str = input_str[1:]
            continue
        if c in [">", "<", "=", "!", "&", "|"]:
            op, input_str = read_operator(input_str)
            tokens.append(op)
            continue
        if c.isspace():
            input_str = input_str[1:]
            continue
        raise TokenizeException(f"Invalid character '{c}'")
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


def read_string(input_str):
    i = input_str[1:].index('"') + 2
    return input_str[:i], input_str[i:]


def read_operator(input_str):
    if len(input_str) > 1:
        if input_str[:2] in [">=", "<=", "==", "!=", "&&", "||"]:
            return input_str[:2], input_str[2:]
    if input_str[:1] in [">", "<", "!"]:
        return input_str[:1], input_str[1:]
    # TODO: raise exception


def add_debug_relations():
    parse_input(
        tokenize(
            """
        Employees {
            Name, Age, Department
            "Alice", 32, "Finance"
            "Bob", 30, "Finance"
            "Joe", 60, "Media"
        }
    """
        )
    ).evaluate(global_assignments)
    parse_input(
        tokenize(
            """
        Employees2 {
            Name, Age, Department
            "Charlie", 20, "H.R."
            "Bob", 30, "Finance"
        }
    """
        )
    ).evaluate(global_assignments)
    parse_input(
        tokenize(
            """
        Departments {
            Department, NumberOfPeople, Manager
            "Finance", 55, "John"
            "H.R.", 40, "Alex"
            "Media", 82, "William"
        }
    """
        )
    ).evaluate(global_assignments)
    parse_input(
        tokenize(
            """
        Departments2 {
            DeptName, NumberOfPeople, Manager
            "Finance", 55, "John"
            "H.R.", 40, "Alex"
            "Media", 82, "William"
        }
    """
        )
    ).evaluate(global_assignments)


global_assignments = {}


def repl():
    debug_mode = "-d" in sys.argv or "--debug" in sys.argv
    if debug_mode:
        add_debug_relations()

    while True:
        try:
            tokens = tokenize(input(": "))
        except TokenizeException as exception:
            print(f"Could not tokenize query due to exception: {exception}")
            continue
        if debug_mode:
            print(f"Tokens: {tokens}")

        try:
            syntax_tree = parse_input(tokens)
        except ParseException as exception:
            print(f"Could not parse query due to exception: {exception}")
            continue
        if debug_mode:
            print(f"Syntax tree: {syntax_tree}")

        try:
            print(syntax_tree.evaluate(global_assignments))
        except EvaluationException as exception:
            print(f"Could not evaluate query due to exception: {exception}")


def main():
    try:
        repl()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
