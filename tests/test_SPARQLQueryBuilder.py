import re

from SPARQLBurger.SPARQLQueryBuilder import SPARQLGraphPattern, SPARQLSelectQuery, SPARQLUpdateQuery
from SPARQLBurger.SPARQLSyntaxTerms import Triple, Binding, IfClause, Filter, Bound, \
    Prefix, GroupBy, Values


class TestSparqlQueryBuilder:
    def test_simple_pattern(self):
        pattern = SPARQLGraphPattern()

        # Add a couple of triples to the pattern
        pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
                Triple(subject="?person", predicate="ex:hasName", object="?name")
            ]
        )

        assert generate_assert_string(pattern) == \
               "{\n ?person rdf:type ex:Person . \n ?person ex:hasName ?name . \n}\n"

    def test_optional_pattern(self):
        main_pattern = SPARQLGraphPattern()
        main_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
                Triple(subject="?person", predicate="ex:hasName", object="?name")
            ]
        )

        optional_pattern = SPARQLGraphPattern(optional=True)
        optional_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="ex:hasAge", object="?age")
            ]
        )

        main_pattern.add_nested_graph_pattern(optional_pattern)

        assert generate_assert_string(main_pattern) == \
               "{\n ?person rdf:type ex:Person . \n ?person ex:hasName ?name . \n" \
               " OPTIONAL {\n ?person ex:hasAge ?age . \n }\n}\n"

    def test_binding_clause(self):
        main_pattern = SPARQLGraphPattern()

        first_pattern = SPARQLGraphPattern()
        first_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
                Triple(subject="?person", predicate="ex:hasName", object="?name")
            ]
        )

        second_pattern = SPARQLGraphPattern(union=True)
        second_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:User"),
                Triple(subject="?person", predicate="ex:hasNickname", object="?name")
            ]
        )

        main_pattern.add_nested_graph_pattern(graph_pattern=first_pattern)
        main_pattern.add_nested_graph_pattern(graph_pattern=second_pattern)

        assert generate_assert_string(main_pattern) == \
            "{\n {\n ?person rdf:type ex:Person . \n ?person ex:hasName ?name . \n }\n UNION\n" \
            " {\n ?person rdf:type ex:User . \n ?person ex:hasNickname ?name . \n }\n}\n"

    def test_values(self):
        pattern = SPARQLGraphPattern()

        uris = ["https://www.wikidata.org/entity/42",
                "https://www.wikidata.org/entity/108"]
        pattern.add_value(value=Values(values=uris, name="?friend"))

        pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
                Triple(subject="?person", predicate="foaf:knows", object="?friend")
            ]
        )

        assert generate_assert_string(pattern) == \
               "{\n VALUES ?friend {<https://www.wikidata.org/entity/42> " \
               "<https://www.wikidata.org/entity/108>}\n" \
               " ?person rdf:type ex:Person . \n ?person foaf:knows ?friend . \n}\n"

    def test_filter_bind_and_if_clauses(self):
        pattern = SPARQLGraphPattern()
        pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
                Triple(subject="?person", predicate="ex:hasAge", object="?age")
            ]
        )

        # Add a filter for variable ?age
        pattern.add_filter(
            filter=Filter(
                expression="?age < 65"
            )
        )

        # Add a binding for variable ?years_alive
        pattern.add_binding(
            binding=Binding(
                value="?age",
                variable="?years_alive"
            )
        )

        # Add a binding for variable ?status, that should be "minor" or "adult" based on the ?age value
        pattern.add_binding(
            binding=Binding(
                value=IfClause(
                    condition="?age >= 18",
                    true_value="'adult'",
                    false_value="'minor'"
                ),
                variable="?status"
            )
        )

        assert generate_assert_string(pattern) == \
            "{\n ?person rdf:type ex:Person . \n ?person ex:hasAge ?age . \n" \
            " BIND (?age AS ?years_alive)\n" \
            " BIND (IF (?age >= 18, 'adult', 'minor') AS ?status)\n" \
            " FILTER (?age < 65)\n}\n"

    def test_bind_with_recursive_nesting(self):
        pattern = SPARQLGraphPattern()
        pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
            ]
        )

        # Create an optional graph pattern and add a triple
        optional_pattern = SPARQLGraphPattern(optional=True)
        optional_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="ex:hasAddress", object="?address")
            ]
        )

        # Add a binding with nested a IF clause and a BOUND condition
        pattern.add_binding(
            binding=Binding(
                value=IfClause(
                    condition=Bound(
                        variable="?address"
                    ),
                    true_value="?address",
                    false_value="'Unknown'"
                ),
                variable="?address"
            )
        )

        assert generate_assert_string(pattern) == \
            "{\n ?person rdf:type ex:Person . \n BIND (IF (BOUND (?address), ?address, 'Unknown') AS ?address)\n}\n"

    def test_sparql_select_query(self):
        select_query = SPARQLSelectQuery(distinct=True, limit=100)

        # Add a prefix
        select_query.add_prefix(
            prefix=Prefix(prefix="ex", namespace="http://www.example.com#")
        )

        # Add the variables we want to select
        select_query.add_variables(variables=["?person", "?age"])

        # Create a graph pattern to use for the WHERE part and add some triples
        where_pattern = SPARQLGraphPattern()
        where_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
                Triple(subject="?person", predicate="ex:hasAge", object="?age"),
                Triple(subject="?person", predicate="ex:address", object="?address"),
            ]
        )

        # Set this graph pattern to the WHERE part
        select_query.set_where_pattern(graph_pattern=where_pattern)

        # Group the results by age
        select_query.add_group_by(
            group=GroupBy(
                variables=["?age"]
            )
        )

        assert generate_assert_string(select_query) == \
            "PREFIX ex: <http://www.example.com#>\n\nSELECT DISTINCT ?person ?age\nWHERE {\n" \
            " ?person rdf:type ex:Person . \n ?person ex:hasAge ?age . \n ?person ex:address ?address . \n}\n" \
            "GROUP BY ?age\n" \
            "LIMIT 100"

    def test_sparql_update_query(self):
        update_query = SPARQLUpdateQuery()

        # Add a prefix
        update_query.add_prefix(
            prefix=Prefix(prefix="ex", namespace="http://www.example.com#")
        )

        # Create a graph pattern for the DELETE part and add a triple
        delete_pattern = SPARQLGraphPattern()
        delete_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="ex:hasAge", object="?age")
            ]
        )

        # Create a graph pattern for the INSERT part and add a triple
        insert_pattern = SPARQLGraphPattern()
        insert_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="ex:hasAge", object="32")
            ]
        )

        # Create a graph pattern for the WHERE part and add some triples
        where_pattern = SPARQLGraphPattern()
        where_pattern.add_triples(
            triples=[
                Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
                Triple(subject="?person", predicate="ex:hasAge", object="?age")
            ]
        )

        # Now let's append these graph patterns to our query
        update_query.set_delete_pattern(graph_pattern=delete_pattern)
        update_query.set_insert_pattern(graph_pattern=insert_pattern)
        update_query.set_where_pattern(graph_pattern=where_pattern)

        assert generate_assert_string(update_query) == \
            "PREFIX ex: <http://www.example.com#>\n\nDELETE {\n ?person ex:hasAge ?age . \n}\n" \
            "INSERT {\n ?person ex:hasAge 32 . \n}\n" \
            "WHERE {\n ?person rdf:type ex:Person . \n ?person ex:hasAge ?age . \n}"


def generate_assert_string(sparql_pattern) -> str:
    """ Returns the string representation of the given pattern.
        Shrinks any multi-space to a single space.
    """
    return re.sub(r' {2,}', ' ', sparql_pattern.get_text())
