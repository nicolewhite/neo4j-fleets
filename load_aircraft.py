from py2neo import neo4j
from csvthings import import_csv_to_list

# Start GraphDatabaseService and the batch writer.
graph = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
batch = neo4j.WriteBatch(graph)

# Load data from CSV into a list called aircraft.
aircraft = import_csv_to_list('aircraft_clean.csv', headers = True)

# MODELS.
# Add uniqueness constraint.
neo4j.CypherQuery(graph, "CREATE CONSTRAINT ON (m:Model) ASSERT m.name IS UNIQUE").run()

# Put all of the model names into a list called models.
models = []

for i in range(len(aircraft)):
    models.append(aircraft[i][1])

# Convert list of model names to a set to get a unique set of values.
models = set(models)

# Create Model nodes.
cypher = "MERGE (:Model {name:{model}})"

for model in models:
    params = dict(model = model)
    batch.append_cypher(cypher, params)

batch.run()

# SERIES.
# Add uniqueness constraint.
neo4j.CypherQuery(graph, "CREATE CONSTRAINT ON (s:Series) ASSERT s.name IS UNIQUE").run()

# Get a list of tuples (model, series) from the aircraft list.
model_series = []

for i in range(len(aircraft)):
    model_series.append((aircraft[i][1], aircraft[i][2]))

# Convert list of tuples to a set to get a unique set of (model, series) tuples.
model_series = set(model_series)

# Create Series nodes.
cypher = "MATCH (m:Model {name:{model}})" \
         "MERGE (:Series {name:{series}})-[:MODEL]->(m)"

vars = ['model', 'series']

for model, series in model_series:
    params = dict(zip(vars, [model, series]))
    batch.append_cypher(cypher, params)

batch.run()

# AIRCRAFT.
# Create Aircraft nodes.
cypher = "MATCH (a:Airline {name:{airline}}), (s:Series {name:{series}})" \
         "MERGE (s)<-[:SERIES]-(:Aircraft {registration:{registration}, msn:{msn}, ff_day:{day}, ff_month:{month}, ff_year:{year}, status:{status}})-[:OWNED_BY]->(a)"

vars = ['msn', 'series', 'airline', 'day', 'month', 'year', 'registration', 'status']

# Execute in batches of 1000.
BATCH_SIZE = 1000
start = 0
end = BATCH_SIZE

for i, e in enumerate(aircraft):
    params = dict(zip(vars, [e[0], e[2], e[3], e[4], e[5], e[6], e[7], e[8]])) # e[1] is model, which we don't need for this.
    if i in range(start, end):
        batch.append_cypher(cypher, params)
    else:
        batch.append_cypher(cypher, params)
        batch.run()
        print("Batch %s complete." % (end / BATCH_SIZE))
        start = end + 1
        end += BATCH_SIZE

batch.run()
print("Batch %s complete." % (end / BATCH_SIZE))
print("All done!")
