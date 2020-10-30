# SPARQL Burger
SPARQL Burger is a Python SPARQL query builder for programmatically generating SPARQL graph patterns and SPARQL Select and Update queries.

## Getting Started
SPARQL Burger is a minimal module for Python (2.x. and 3.x).

### Prerequisites

None

### Installation

* #### Manually
 
 1. Save the `SPARQLBurger` folder to your project's directory.

* #### From PyPi

 ```
 pip install SPARQL-Burger
 ```

## Usage examples
**1. Create a SPARQL graph pattern and add some triples**
```python
from SPARQLBurger.SPARQLQueryBuilder import *

# Create a graph pattern
pattern = SPARQLGraphPattern()

# Add a couple of triples to the pattern
pattern.add_triples(
        triples=[
            Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
            Triple(subject="?person", predicate="ex:hasName", object="?name")
        ]
    )

# Let's print this graph pattern
print(pattern.get_text())
```
The printout is:
```
{
   ?person rdf:type ex:Person . 
   ?person ex:hasName ?name . 
}
```
At this point we have generated a minimal [SPARQL graph pattern](http://https://www.w3.org/TR/rdf-sparql-query/#GraphPattern "SPARQL graph pattern"). A graph pattern, delimited with `{ }`, is a building block for SPARQL queries and more than one can be nested and/or united to form a more complex graph pattern.

**2. Create an optional pattern and nest it to the main pattern**
```python
from SPARQLBurger.SPARQLQueryBuilder import *

# Create a main graph pattern and add some triples
main_pattern = SPARQLGraphPattern()
main_pattern.add_triples(
        triples=[
            Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
            Triple(subject="?person", predicate="ex:hasName", object="?name")
        ]
    )

# Create an optional pattern and add a triple
optional_pattern = SPARQLGraphPattern(optional=True)
optional_pattern.add_triples(
        triples=[
            Triple(subject="?person", predicate="ex:hasAge", object="?age")
        ]
    )

# Nest the optional pattern to the main
main_pattern.add_nested_graph_pattern(optional_pattern)

# Let's print the main graph pattern
print(pattern.get_text())
```
The printout is:
```
{
   ?person rdf:type ex:Person . 
   ?person ex:hasName ?name . 
   OPTIONAL {
      ?person ex:hasAge ?age . 
   }
}
```
In this case, the main graph pattern contains another graph pattern that is declared as OPTIONAL. In general, graph patterns can contain as many nesting levels as necessary. Nesting a pattern to itself, though, would result to an error.

**3. Create a UNION of graph patterns**

In this example we will declare a main graph pattern that contains two other graph patterns associated with UNION.
```python
from SPARQLBurger.SPARQLQueryBuilder import *

# Create an empty graph pattern
main_pattern = SPARQLGraphPattern()

# Create the first graph pattern to be nested and add some triples
first_pattern = SPARQLGraphPattern()
first_pattern.add_triples(
        triples=[
            Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
            Triple(subject="?person", predicate="ex:hasName", object="?name")
        ]
    )

# Create the second graph pattern to be nested as a UNION to the first and add some triples
second_pattern = SPARQLGraphPattern(union=True)
second_pattern.add_triples(
        triples=[
            Triple(subject="?person", predicate="rdf:type", object="ex:User"),
            Triple(subject="?person", predicate="ex:hasNickname", object="?name")
        ]
    )

# Nest both patterns to the main one
main_pattern.add_nested_graph_pattern(graph_pattern=first_pattern)
main_pattern.add_nested_graph_pattern(graph_pattern=second_pattern)

# Let's print the main graph pattern
print(main_pattern.get_text())
```
The printout is:
```
{
   {
      ?person rdf:type ex:Person . 
      ?person ex:hasName ?name . 
   }
   UNION
   {
      ?person rdf:type ex:User . 
      ?person ex:hasNickname ?name . 
   }
}
```

**4. Adding FILTER, BIND and IF definitions**

OK, this far we have created simple and nested graph patterns. Now let's see how to add filters, bindings and if clauses.
```python
from SPARQLBurger.SPARQLQueryBuilder import *

# Create a graph pattern and add some triples
pattern = SPARQLGraphPattern()
pattern.add_triples(
        triples=[
            Triple(subject="?person", predicate="rdf:type", object="ex:Person"),
            Triple(subject="?person", predicate="ex:hasAge", object="?age")
        ]
    )

# Add a filter for variable ?age
pattern.add_filter(
    filter= Filter(
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

# Print the graph pattern
print(pattern.get_text())
```
The printout is:
```
{
   ?person rdf:type ex:Person . 
   ?person ex:hasAge ?age . 
   BIND (?age AS ?years_alive)
   BIND (IF (?age >= 18, 'adult', 'minor') AS ?status)
   FILTER (?age < 65)
}
```
In the first BIND we have only provided a value and a variable as string, but this is not always the case. In the second BIND we nested an IF clause. Therefore, the `Binding.value` also accepts objects of classes like `IfClause`. In a similar way, the arguments of `IfClause` can also be other objects of type `IfClause` and `Bound` in a nested format, as shown below. 
```python
from SPARQLBurger.SPARQLQueryBuilder import *

# Create a graph pattern and add a triple
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

# Print the graph pattern
print(pattern.get_text())
```
The printout is:
```
{
   ?person rdf:type ex:Person . 
   BIND (IF (BOUND (?address), ?address, 'Unknown') AS ?address)
}
```

**5. Create a SPARQL Select query**

Now that we have mastered the definition of graph patterns, let's create a simple Select query.
```python
from SPARQLBurger.SPARQLQueryBuilder import *

# Create an object of class SPARQLSelectQuery and set the limit for the results to 100
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

# Print the query we have defined
print(select_query.get_text())
```
The printout is:
```
PREFIX ex: <http://www.example.com#>

SELECT DISTINCT ?person ?age
WHERE {
   ?person rdf:type ex:Person . 
   ?person ex:hasAge ?age . 
   ?person ex:address ?address . 
}
GROUP BY ?age
LIMIT 100
```

**6. Create a SPARQL Update query**

Quite similarly we can exploit graph patterns to create a SPARQL Update query (in the DELETE/INSERT form)
```python
from SPARQLBurger.SPARQLQueryBuilder import *

# Create a SPARQLUpdateQuery object
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

# Print the query we have defined
print(update_query.get_text())
```
The printout is:
```
PREFIX ex: <http://www.example.com#>

DELETE {
   ?person ex:hasAge ?age . 
}
INSERT {
   ?person ex:hasAge 32 . 
}
WHERE {
   ?person rdf:type ex:Person . 
   ?person ex:hasAge ?age . 
}
```

## Documentation
[The official webpage](http://pmitzias.com/SPARQLBurger) - [The Docs](http://pmitzias.com/SPARQLBurger/docs.html)

## Authors
* [Panos Mitzias](http://pmitzias.com) - Design and development
* [Stratos Kontopoulos](http://stratoskontopoulos.com) - Contribution to the design

## Applications
SPARQL Burger has been deployed in the following projects:

* [CASPAR](https://www.linkedin.com/showcase/caspar-framework)
