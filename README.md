# Installation
1. `git clone` this repo and `cd` into it
2. To run the program, use `python main.py` (Python 3 should work, the specific version used to develop the program is 3.13.7)
3. To run the program in debug mode, use `python main.py -d` or `python main.py --debug`
4. To run the tests, use `python tests.py`

# Usage
1. Start the program in a terminal
2. The progam runs as a REPL (read-eval-print loop)
3. Each time you submit input, it will be evaluated and printed (e.g. entering `1 == 2` and then hitting `<Enter>` will print `False`)
4. Each time you submit input it can be either a relation or a query
5. Hitting `<Enter>` will submit your input only if it is a *complete* relation/query, this means that you can spread your input across multiple lines (e.g. when entering a relation with many tuples)
6. If the program is running in debug mode, there will be some relations already initialized (their names are Employees, Employees2, Departments, Departments2) and also the intermediate computations (i.e. tokens and syntax tree) will be printed for every input
7. Stop the program using `<Ctrl+C>` or `<Ctrl+D>`

# Syntax
TODO
