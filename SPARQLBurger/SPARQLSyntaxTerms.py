"""
SPARQL Burger - A Python SPARQL query builder for programmatically generating SPARQL graph patterns and queries.
Version 0.1
Official webpage: http://pmitzias.com/SPARQLBurger
Documentation: http://pmitzias.com/SPARQLBurger/docs.html
Created by Panos Mitzias (http://www.pmitzias.com)
Powered by Catalink Ltd (http://catalink.eu)
"""


class Prefix:
    def __init__(self, prefix, namespace):
        """
        The Prefix class constructor.
        :param prefix: <str> The prefix (e.g. "ex").
        :param namespace: <str> The namespace (e.g. "http://www.example.com#").
        """
        self.prefix = prefix
        self.namespace = namespace

    def get_text(self):
        """
        Generates the text for the given prefix (e.g. "PREFIX ex: <http://www.example.com#>")
        :return: <str> The prefix definition text. Returns empty string if an exception was raised.
        """
        try:
            return "PREFIX %s: <%s>\n" % (self.prefix, self.namespace)
        except Exception as e:
            print("Error 1 @ Prefix.get_text()")
            return ""


class Triple:
    def __init__(self, subject, predicate, object):
        """
        The Triple class constructor.
        :param subject: <str> The subject string (e.g. "?person")
        :param predicate: <str> The predicate string (e.g. "ex:hasName")
        :param object: <str> The object string (e.g. "\'John\'@en")
        """
        self.subject = str(subject)
        self.predicate = str(predicate)
        self.object = str(object)

    def get_text(self):
        """
        Generates the text for the given triple.
        :return: <str> The triple definition text. Returns empty string if an exception was raised.
        """
        try:
            return "%s %s %s . \n" % (self.subject, self.predicate, self.object)
        except Exception as e:
            print("Error 1 @ Triple.get_text()")
            return ""


class Filter:
    def __init__(self, expression):
        """
        The Filter class constructor.
        :param expression: <str> The expression to get in the filter (e.g. "?age > 30")
        """
        self.expression = expression

    def get_text(self):
        """
        Generates the text for the given filter.
        :return: <str> The filter definition text. Returns empty string if an exception was raised.
        """
        try:
            return "FILTER (%s)" % (self.expression,)
        except Exception as e:
            print("Error 1 @ Filter.get_text()")
            return ""

class Having:
    def __init__(self, expression):
        """
        The Having class constructor.
        :param expression: <str> The expression to get in the having filter (e.g. "?age > 30")
        """
        self.expression = expression

    def get_text(self):
        """
        Generates the text for the given having filter.
        :return: <str> The filter definition text. Returns empty string if an exception was raised.
        """
        try:
            return "HAVING (%s)" % (self.expression,)
        except Exception as e:
            print("Error 1 @ Filter.get_text()")
            return ""

class Binding:
    def __init__(self, value, variable):
        """
        The Binding class constructor.
        :param value: <str> A string value to get in the BIND first part (e.g. "John")
         OR <obj> Another object (e.g. IfClause) to be nested.
        :param variable: <str> The variable to be bound to this value (e.g. "?name")
        """
        self.value = value
        self.variable = variable

    def get_text(self):
        """
        Generates the text for the given binding (e.g. "BIND('John' AS ?name)" or "BIND(IF(BOUND(...)) AS ?name") )
        :return: <str> The binding definition text. Returns empty string if an exception was raised.
        """
        try:
            if type(self.value) is str:
                value_text = self.value
            else:
                value_text = self.value.get_text()

            return "BIND (%s AS %s)" % (value_text, self.variable)

        except Exception as e:
            print("Error 1 @ Binding.get_text()")
            return ""


class Bound:
    def __init__(self, variable):
        """
        The Bound class constructor.
        :param variable: <str> The variable to be checked if it is bound (e.g. "?name")
         OR <obj> Another object to be nested.
        """
        self.variable = variable

    def get_text(self):
        """
        Generates the text for the given BOUND clause (e.g. "BOUND (?name)" )
        :return: <str> The bound definition text. Returns empty string if an exception was raised.
        """
        try:
            if type(self.variable) is str:
                variable_text = self.variable
            else:
                variable_text = self.variable.get_text()

            return "BOUND (%s)" % (variable_text, )

        except Exception as e:
            print("Error 1 @ Bound.get_text()")
            return ""


class IfClause:
    def __init__(self, condition, true_value, false_value):
        """
        The IfClause class constructor.
        :param condition: <str> The condition for the IF clause OR <obj> Another object to be nested.
        :param true_value: <str> The value for when IF condition is True OR <obj> Another object to be nested.
        :param false_value: <str> The value for when IF condition is False OR <obj> Another object to be nested.
        """
        self.condition = condition
        self.true_value = true_value
        self.false_value = false_value

    def get_text(self):
        """
        Generates the text for the given BOUND clause (e.g. "IF(?age > 18, 'adult', 'minor')" )
        :return: <str> The if clause definition text. Returns empty string if an exception was raised.
        """
        try:
            # Check for nested condition (e.g. a nested if condition)
            if type(self.condition) is str:
                condition_text = self.condition
            else:
                condition_text = self.condition.get_text()

            # Check for nested value (e.g. a nested if value)
            if type(self.true_value) is str:
                true_value_text = self.true_value
            else:
                true_value_text = self.true_value.get_text()

            # Check for nested value (e.g. a nested if value)
            if type(self.false_value) is str:
                false_value_text = self.false_value
            else:
                false_value_text = self.false_value.get_text()

            return "IF (%s, %s, %s)" % (condition_text, true_value_text, false_value_text)

        except Exception as e:
            print("Error 1 @ IfClause.get_text()")
            return ""


class GroupBy:
    def __init__(self, variables):
        """
        The GroupBy class constructor.
        :param variables: <list> A list of variables as strings that will be used for the grouping
        """
        self.variables = variables

    def get_text(self):
        """
        Generates the text for the given GROUP BY expression (e.g. "GROUP BY ?person ?age")
        :return: <str> The GROUP BY definition text. Returns empty string if an exception was raised.
        """
        try:
            return "GROUP BY %s" % (" ".join(self.variables), )

        except Exception as e:
            print("Error 1 @ GroupBy.get_text()")
            return ""


class Values:
    def __init__(self, values, name):
        """
        The Values class constructor.
        :param values: <list> A list of variables as strings that should be
                                gathered under the same variable.
        :param name: <str> The name of the resulting variable.
        """
        self.values = values
        self.name = name

    def get_text(self):
        """
        Generate the text for the given VALUES expression (e.g.
        "VALUES ?person {<"https://www.wikidata.org/entity/42">}
        :return: <str> The VALUES defenition text. Returns empty string if an
                        exception was raised.
        """
        try:
            enclosed_values = [in_brackets(value) for value in self.values]
            return "VALUES %s {%s}" % (self.name, ' '.join(enclosed_values))
        except Exception as e:
            print("Error 1 @ Values.get_text()")
            return ""


def in_brackets(uri: str) -> str:
    """Encloses a given URI in brackets (i.e. "<" and ">").
    If the uri already has brackets, nothing happens.
    :returns: <str> A URI string enclosed in brackets.
    """
    if uri.startswith("<"):
        return uri
    elif uri.startswith("http"):
        return "<%s>" % uri
    else:
        return uri
