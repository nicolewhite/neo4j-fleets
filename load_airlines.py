from py2neo import neo4j
from csvthings import import_csv_to_list

# Start GraphDatabaseService and the batch writer.
graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
batch = neo4j.WriteBatch(graph)

# Load data from CSV into a list called airlines.
airlines = import_csv_to_list('airlines_clean.csv', headers = True)

# COUNTRIES.
# Add uniqueness constraint.
neo4j.CypherQuery(graph, "CREATE CONSTRAINT ON (c:Country) ASSERT c.name IS UNIQUE").run()

# Put all country names into a list called countries.
countries = []

for i in range(len(airlines)):
    countries.append(airlines[i][1])

# Convert list of country names to a set to get a unique set of values.
countries = set(countries)

# Create Country nodes.
cypher = "MERGE (c:Country {name:{country}})"

for country in countries:
    params = dict(country = country)
    batch.append_cypher(cypher, params)

batch.run()

# AIRLINES.
# Add uniqueness constraint.
neo4j.CypherQuery(graph, "CREATE CONSTRAINT ON (a:Airline) ASSERT a.name IS UNIQUE").run()

# Create Airline nodes.
cypher = "MATCH (c:Country {name:{country}})" \
         "MERGE (:Airline {name:{airline}, status:{status}})-[:BASED_IN]->(c)"

vars = ['airline', 'country', 'status']

for airline, country, status in airlines:
    params = dict(zip(vars, [airline, country, status]))
    batch.append_cypher(cypher, params)

batch.run()