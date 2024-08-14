from algebra.error import *
from sys import version_info

if version_info < (3, 10):
    raise OutdateError("To use this library, please have Python 3.10 or more. Your current Python version is Python " + version_info[0] + "." + version_info[1] + ".")

class Number:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"(Number {self.value})"

class Variable:
    def __init__(self, name, level=1):
        if len(name) != 1:
            raise OverAlphabetError("The name must only contain 1 character!")

        if name in "0123456789":
            raise OverAlphabetError("The name must not be a digit!")
        
        self.name = name
        self.level = level

    def __repr__(self):
        return f'(Variable "{self.name}" level {self.level})'
    
class Constant:
    def __init__(self, name, value=0, level=1):
        self.name = name
        self.value = value
        self.level = level

    def __repr__(self):
        return f'(Constant "{self.name}" value {self.value} level {self.level})'

class Term:
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        string = ""
        for value in self.values:
            string += value.__repr__()

        return f"[{string}]"

    def simplify(self):
        numbers = []
        variables = []
        constants = []
        for value in self.values:
            if isinstance(value, Number):
                numbers.append(value)
            else:
                variables.append(value)
                if isinstance(value, Constant):
                    constants.append(value.name)

        self.values = []
        product = 1
        for number in numbers:
            product *= number.value

        self.values.append(Number(product))
        variables_table = {}
        constants_table = {}
        for variable in variables:
            if variable.name in constants:
                if isinstance(variable, Variable):
                    raise ConstantError(f'Variable "{variable.name}" already exists as a constant. Cannot simplify the expression.')

                try:
                    constants_table[variable.name][1] += variable.level
                    if constants_table[variable.name][0] != variable.value:
                        raise ConstantError(f'Variable "{variable.name}" already has a value of {variable.value}. Cannot simplify the expression.')
                except KeyError:
                    constants_table[variable.name] = [variable.value, variable.level]
            else:
                try:
                    variables_table[variable.name] += variable.level
                except KeyError:
                    variables_table[variable.name] = variable.level

        for variable in variables_table:
            self.values.append(Variable(variable, variables_table[variable]))

        for constant in constants_table:
            self.values.append(Constant(constant, constants_table[constant][0], constants_table[constant][1]))

    def substitute(self, substitutions_values=None, **substitutions):
        if isinstance(substitutions_values, dict):
            subs = substitutions_values
        else:
            subs = substitutions

        self.simplify()
        values = []
        for value in self.values:
            if isinstance(value, (Variable, Constant)):
                try:
                    values.append(Constant(value.name, subs[value.name], value.level))
                except KeyError:
                    raise SubstitutionError(f'There are no {"variable" if isinstance(value, Variable) else "constant"} "{value.name}" in the substitution. Cannot calculate the term.')
                
                if isinstance(value, Constant):
                    if value.value != subs[value.name]:
                        raise SubstitutionError(f'Constant "{value.name}" has the wrong value substitution based on the input. Cannot calculate the term.')
            else:
                values.append(value)
        product = 1
        for value in values:
            level = 1
            if isinstance(value, Constant):
                level = value.level
            product *= value.value ** level

        return product
