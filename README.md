# Installation
1. `git clone` this repo and `cd` into it
2. To run the program, use `python main.py` (Python 3 should work, the specific version used to develop the program is 3.13.7)
3. To run the program in debug mode, use `python main.py -d` or `python main.py --debug`
4. To run the tests, use `python tests.py`

# Usage
1. Start the program in a terminal
2. The progam runs as a [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop)
3. Each time you submit input, it will be evaluated and printed (e.g. entering `1 == 2` and then hitting `<Enter>` will print `False`)
4. Each time you submit input it can be either a relation or a query
5. Hitting `<Enter>` will submit your input only if it is a *complete* relation/query, this means that you can spread your input across multiple lines (e.g. when entering a relation with many tuples)
6. If the program is running in debug mode, there will be some relations already initialized (their names are Employees, Employees2, Departments, Departments2) and also the intermediate computations (i.e. tokens and syntax tree) will be printed for every input
7. Stop the program using `<Ctrl+C>` or `<Ctrl+D>`

# Syntax
To view the syntax in BNF format see [grammar.bnf](grammar.bnf)

## Examples
Note: These examples will work in debug mode
- `select Age > 30 Employees`
- `Employees join Departments`
- `project Name,NumberOfPeople (Employees full_join Age > NumberOfPeople Departments2)`

## Notes
Keep these in mind when using the program
- [Operator precedence](https://en.wikipedia.org/wiki/Order_of_operations#Programming_languages) is *not* enforced
- Binary operators are [right associative](https://en.wikipedia.org/wiki/Operator_associativity) when no parentheses are used
- To ensure the desired order of operations, use parentheses (e.g. `(A join B) join C` if you want `join C` to be the last operation)

## Literals
There are two types of literals, integer and string
- Integer literals should contain only digits `0` to `9` and may optionally begin with `-` e.g. `13`, `-20`
- String literals must use double quotes e.g. `"an example string"`

## Operators
Here is a list of all available operators

| Operator | Description | Example |
| --- | --- | --- |
| `>` | Greater than | `1 > 2` |
| `<` | Less than | `1 < 2` |
| `>=` | Greater than or equal to | `1 >= 2` |
| `<=` | Less than or equal to | `1 <= 2`|
| `==` | Equals | `1 == 2` |
| `!=` | Not equals | `1 != 2` |
| `&&` | Boolean AND | `(1 == 2) && (1 != 2)` |
| `\|\|` | Boolean OR | `(1 == 2) \|\| (1 != 2)` |
| `!` | Boolean NOT | `!(1 == 2)` |
| `union` | Set union | `A union B` |
| `intersect` | Set intersect | `A intersect B` |
| `minus` | Set minus | `A minus B` |
| `join` | Natural join | `A join B` |
| `theta_join` | Theta join | `A theta_join ColumnX < ColumnY B` |
| `left_join` | Left outer join | `A left_join ColumnX < ColumnY B` |
| `right_join` | Right outer join | `A right_join ColumnX < ColumnY B` |
| `full_join` | Full outer join | `A full_join ColumnX < ColumnY B` |
| `select` | Select (a.k.a. sigma) | `select ColumnX < ColumnY A` |
| `project` | Project (a.k.a. pi) | `project ColumnX, ColumnY A` |
| `is_null` | Check if value is NULL | `select is_null ColumnX (A full_join ColumnX < ColumnY B)` |

## Relations
Here is an example demonstrating the relation syntax: `A { C1, C2 1, 2 3, 4  }`
- This will initialize a relation called `A`
- `A` has two columns, `C1` and `C2`
- `A` contains two tuples, `(1, 2)` and `(3, 4)`

# How it works
For each input the program does the following
1. Convert input text into tokens (this is done by the lexer)
2. Convert tokens into a syntax tree (this is done by the parser)
3. Recursively evaluate every node of the syntax tree to get the final result

## Example
Here is an example where the input is `select Age > 30 Employees`
1. The lexer will convert the input into tokens: `['select', 'Age', '>', 30, 'Employees']`
2. The parser will convert the tokens into a syntax tree: `UnaryExpression{('select', BinaryExpression{Age > 30}) Employees}`
3. Evaluating the tree will lead to the function `select()` being called with `Employees` and `BinaryExpression{Age > 30}` as its arguments, and this will return a new relation containing only the employees whose age is greater than 30

Bonus information: `select()` will evaluate the condition `Age > 30` for each tuple of `Employees`
