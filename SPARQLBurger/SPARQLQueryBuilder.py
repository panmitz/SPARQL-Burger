"""
SPARQL Burger - A Python SPARQL query builder for programmatically generating SPARQL graph patterns and queries.
Version 0.1
Official webpage: http://pmitzias.com/SPARQLBurger
Documentation: http://pmitzias.com/SPARQLBurger/docs.html
Created by Panos Mitzias (http://www.pmitzias.com)
Powered by Catalink Ltd (http://catalink.eu)
"""


from SPARQLBurger.SPARQLSyntaxTerms import *


class SPARQLGraphPattern:
    def __init__(self, optional=False, union=False):
        """
        The SPARQLGraphPattern class constructor.
        :param optional: <bool> Indicates if graph pattern should be marked as OPTIONAL.
        :param union: <bool> Indicates if graph pattern should have a UNION clause that associates it with the previous.
        graph pattern
        """
        self.is_optional = optional
        self.is_union = union
        self.graph = []
        self.filters = []
        self.bindings = []
        self.values = []

    def add_triples(self, triples):
        """
        Adds a list of triples to the graph pattern.
        :param triples: <list> A list of SPARQLSyntaxTerms.Triple objects.
        :return: <bool> True if addition succeeded, False if given argument was not a list of Triple objects.
        """
        if type(triples) is list and all(isinstance(element, Triple) for element in triples):
            self.graph.extend(triples)
            return True
        else:
            return False

    def add_nested_graph_pattern(self, graph_pattern):
        """
        Adds another graph pattern as nested to the main graph pattern.
        :param graph_pattern: <obj> The SPARQLGraphPattern object to be nested.
        :return: <bool> True if addition succeeded, False if given argument was not a SPARQLGraphPattern object.
        """
        if type(graph_pattern) is SPARQLGraphPattern:
            self.graph.append(graph_pattern)
            return True
        else:
            return False

    def add_nested_select_query(self, select_query):
        """
        Adds a select query as nested to the main graph pattern.
        :param select_query: <obj> The SPARQLSelectQuery object to be nested.
        :return: <bool> True if addition succeeded, False if given argument was not a SPARQLGraphPattern object.
        """
        if type(select_query) is SPARQLSelectQuery:
            self.graph.append(select_query)
            return True
        else:
            return False

    def add_filter(self, filter):
        """
        Adds a FILTER expression to the graph pattern.
        :param filter: <obj> The Filter to be added.
        :return: <bool> True if addition succeeded, False if given argument was not a Filter object.
        """
        if type(filter) is Filter:
            self.filters.append(filter)
            return True
        else:
            return False

    def add_having(self, filter):
        """
        Adds a HAVING expression to the graph pattern.
        :param filter: <obj> The HAVING expression to be added.
        :return: <bool> True if addition succeeded, False if given argument was not a Having object.
        """
        if type(filter) is Having:
            self.filters.append(filter)
            return True
        else:
            return False

    def add_binding(self, binding):
        """
        Adds a BIND expression to the graph pattern.
        :param binding: <obj> The Binding object to be added.
        :return: <bool> True if addition succeeded, False if given argument was not a Binding object.
        """
        if type(binding) is Binding:
            self.bindings.append(binding)
            return True
        else:
            return False

    def add_value(self, value):
        """
        Adds a VALUES expression to the graph pattern.
        :param value: <Value> A Value object to be added.
        :return: <bool> True if addition succeeded, False otherwise.
        """
        if isinstance(value, Values):
            self.values.append(value)
            return True
        else:
            return False

    def get_text(self, indentation_depth=0):
        """
        Generates the text for the SPARQL graph pattern.
        :param indentation_depth: <int> A value that facilitates the appropriate addition of indents to the text. Defaults at 0.
        :return: <str> The SPARQL graph pattern text. Returns empty string if an exception was raised.
        """
        try:
            # Calculate indentations
            outer_indentation = indentation_depth * "   "
            inner_indentation = (indentation_depth + 1) * "   "

            # Initialize string
            if self.is_optional:
                query_text = "%sOPTIONAL {\n" % (outer_indentation, )
            elif self.is_union:
                query_text = "%sUNION\n%s{\n" % (outer_indentation, outer_indentation)
            else:
                query_text = "%s{\n" % (outer_indentation, )

            for value in self.values:
                query_text += "%s%s\n" % (inner_indentation, value.get_text())

            # Add triples
            for entry in self.graph:
                # If entry is a Triple object
                if type(entry) is Triple:
                    query_text += "%s%s" % (inner_indentation, entry.get_text())

                # If entry is a nested SPARQLGraphPattern object
                elif type(entry) is SPARQLGraphPattern:

                    # Get text for nested graph pattern
                    nested_graph_text = entry.get_text(indentation_depth=indentation_depth + 1)

                    # Append nested text to graph text
                    if nested_graph_text:
                        query_text += nested_graph_text
                    else:
                        return False

                # If entry is a nested SPARQLSelectQuery object
                elif type(entry) is SPARQLSelectQuery:

                    # Get the text for the nested select query
                    nested_select_text = entry.get_text(indentation_depth=indentation_depth + 2)

                    # Append nested text to graph text
                    if nested_select_text:
                        query_text += "%s{%s%s}\n" % (inner_indentation, nested_select_text, inner_indentation)
                    else:
                        return False

            # Add binding texts
            for binding in self.bindings:
                query_text += "%s%s\n" % (inner_indentation, binding.get_text())

            # Add filter texts
            for filter in self.filters:
                query_text += "%s%s\n" % (inner_indentation, filter.get_text())

            # Finalize graph text
            query_text += "%s}\n" % (outer_indentation, )

            return query_text

        except Exception as e:
            print("Error 1 @ SPARQLGraphPattern.get_text()", e)
            return ""


class SPARQLQuery:
    def __init__(self, include_popular_prefixes=False):
        """
        The SPARQLQuery class constructor.
        :param include_popular_prefixes: <bool> If True, a list of popular namespaces will be added automatically
        """
        self.prefixes = []
        self.where = None

        if include_popular_prefixes:
            self.add_popular_prefixes()

    def add_prefix(self, prefix):
        """
        Adds a PREFIX expression to the query.
        :param prefix: <obj> The Prefix object to be added.
        :return: <bool> True if addition succeeded, False if given argument was not a Prefix object.
        """
        if type(prefix) is Prefix:
            self.prefixes.append(prefix)
            return True
        else:
            return False

    def add_popular_prefixes(self):
        popular_prefixes = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xml": "http://www.w3.org/2001/XMLSchema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "prov": "http://www.w3.org/ns/prov#",
            "foaf": "http://xmlns.com/foaf/0.1/"
        }

        for prefix in popular_prefixes:
            self.add_prefix(
                prefix=Prefix(
                    prefix=prefix,
                    namespace=popular_prefixes[prefix]
                )
            )

    def set_where_pattern(self, graph_pattern):
        """
        Sets the SPARQLGraphPattern object to be used at the WHERE part
        :param graph_pattern: <obj> The SPARQLGraphPattern object to be used.
        :return: <bool> True if setting succeeded, False if given argument was not a SPARQLGraphPattern object.
        """
        if type(graph_pattern) is SPARQLGraphPattern:
            self.where = graph_pattern
            return True
        else:
            return False


class SPARQLSelectQuery(SPARQLQuery):
    def __init__(self, distinct=False, limit=False, include_popular_prefixes=False):
        """
        The SPARQLSelectQuery class constructor.
        :param distinct: <bool> Indicates if the select should be SELECT DISTINCT.
        :param limit: <int> A limit to be used for the select query results.
        """
        SPARQLQuery.__init__(self, include_popular_prefixes)

        self.distinct = distinct
        self.limit = limit
        self.variables = []
        self.group_by = []

    def add_variables(self, variables):
        """
        Adds a list of variables to be selected by the select query
        :param variables: <list> A list of variables as strings.
        :return: <bool> True if addition succeeded, False if given argument was not a list of strings.
        """
        if type(variables) is list and all(isinstance(element, str) for element in variables):
            self.variables.extend(variables)
            return True
        else:
            return False

    def add_group_by(self, group):
        """
        Adds a GROUP BY expression to the query
        :param group: <obj> The GroupBy object to be added
        :return: <bool> True if addition succeeded, False if given argument was not a GroupBy object.
        """
        if type(group) is GroupBy:
            self.group_by.append(group)
            return True
        else:
            return False

    def get_text(self, indentation_depth=0):
        """
        Generates the text for the SPARQL select query.
        :param indentation_depth: <int> A value that facilitates the appropriate addition of indents to the text. Defaults at 0.
        :return: <str> The SPARQL Select query text. Returns empty string if an exception was raised.
        """
        try:
            # Calculate indentation
            outer_indentation = indentation_depth * "   "

            # Initialize text string
            query_text = ""

            # Add prefixes
            for prefix in self.prefixes:
                query_text += prefix.get_text()

            # Add SELECT token
            if self.distinct:
                distinct_token = "DISTINCT "
            else:
                distinct_token = ""
            query_text += "\n%sSELECT %s" % (outer_indentation, distinct_token)

            # If some variables have been defined, add them
            if self.variables:
                query_text += " ".join(self.variables)

            # If no variable has been defined, use *
            else:
                query_text += " *"

            # Add WHERE token
            query_text += "\n%sWHERE " % (outer_indentation, )

            # Add WHERE pattern graph
            if self.where is not None:
                query_text += self.where.get_text(indentation_depth=indentation_depth)[:-1]

            # Add group by expressions
            for group in self.group_by:
                query_text += "\n%s%s" % (outer_indentation, group.get_text())

            # Add limit if required
            if self.limit:
                query_text += "\nLIMIT %s" % (str(self.limit))

            return query_text

        except Exception as e:
            print("Error 1 @ SPARQLSelectQuery.get_text()", e)
            return ""


class SPARQLUpdateQuery(SPARQLQuery):
    def __init__(self, include_popular_prefixes=False):
        """
        The SPARQLUpdateQuery class constructor.
        """
        SPARQLQuery.__init__(self, include_popular_prefixes)
        self.delete = None
        self.insert = None

    def set_delete_pattern(self, graph_pattern):
        """
        Sets the SPARQLGraphPattern object to be used at the DELETE part
        :param graph_pattern: <obj> The SPARQLGraphPattern object to be used.
        :return: <bool> True if setting succeeded, False if given argument was not a SPARQLGraphPattern object.
        """
        if type(graph_pattern) is SPARQLGraphPattern:
            self.delete = graph_pattern
            return True
        else:
            return False

    def set_insert_pattern(self, graph_pattern):
        """
        Sets the SPARQLGraphPattern object to be used at the INSERT part.
        :param graph_pattern: <obj> The SPARQLGraphPattern object to be used.
        :return: <bool> True if setting succeeded, False if given argument was not a SPARQLGraphPattern object.
        """
        if type(graph_pattern) is SPARQLGraphPattern:
            self.insert = graph_pattern
            return True
        else:
            return False

    def get_text(self, indentation_depth=0):
        """
        Generates the text for the SPARQL update query.
        :param indentation_depth: <int> A value that facilitates the appropriate addition of indents to the text. Defaults at 0.
        :return: <str> The SPARQL Update query text. Returns empty string if an exception was raised.
        """

        try:
            # Calculate indentation
            outer_indentation = indentation_depth * "   "

            # Initialize text string
            query_text = ""

            # Add prefixes
            for prefix in self.prefixes:
                query_text += prefix.get_text()

            # If a delete graph pattern has been defined
            if self.delete is not None:

                # Add DELETE token
                query_text += "\n%sDELETE " % (outer_indentation,)

                # Add DELETE pattern graph
                query_text += self.delete.get_text(indentation_depth=indentation_depth)[:-1]

            # If an insert graph pattern has been defined
            if self.insert is not None:
                # Add INSERT token
                query_text += "\n%sINSERT " % (outer_indentation,)

                # Add INSERT pattern graph
                query_text += self.insert.get_text(indentation_depth=indentation_depth)[:-1]

            # If a where graph pattern has been defined
            if self.where is not None:
                # Add WHERE token
                query_text += "\n%sWHERE " % (outer_indentation,)

                # Add WHERE pattern graph
                query_text += self.where.get_text(indentation_depth=indentation_depth)[:-1]

            return query_text

        except Exception as e:
            print("Error 1 @ SPARQLUpdateQuery.get_text()", e)
            return ""
