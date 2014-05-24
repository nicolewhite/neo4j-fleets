# A neo4j database of airline fleets.

## Database structure.

The nodes and relationships in the graph are summarized below.

![Graph Structure](http://i.imgur.com/fknnxmi.png)

| Node Label | Node Properties                                        |
| ---------- | ---------------                                        |
| Airline    | `name`*, `status` (Active or Inactive)                 |
| Country    | `name`*                                                |
| Series     | `name`*                                                |
| Model      | `name`*                                                |
| Aircraft   | `msn` (manufacturer's serial number), `ff_day`, `ff_month`, `ff_year` (day, month, year of first flight), `registration` (registration code), `status` (Active, Scrapped, Stored, Written off, On order, or Unknown) |

<nowiki>*</nowiki> There is a uniqueness constraint on this property for the given node label.

None of the relationships in the graph have any properties.

## Get the database dump.
The already-created database is located in `fleets.graphdb.zip`.

## Create the database from scratch.
Alternatively, to create the database from scratch, do the following in the given order:

* Execute `scrape_airlines.py`. This will create a 180KB file `airlines_raw.csv` in the current directory.
* Execute `scrape_aircraft.py`. This will create a 2,181KB file `aircraft_raw.csv` in the current directory.
* Execute `clean.py`. This will create a 98KB file `airlines_clean.csv` and a 2,140KB file `aircraft_clean.csv` in the current directory. The raw datasets `airlines_raw.csv` and `aircraft_raw.csv` can be deleted by uncommenting `os.remove()` (lines 41 and 42) in `clean.py`. Or you can just delete them. :)

Before going on to the below steps, make sure Neo4j is up and running at [http://localhost:7474/db/data](http://localhost:7474/db/data). If the URL is something else, change the value of this string at line 5 of the following files.

* Execute `load_airlines.py`.<br>
* Execute `load_aircraft.py`.


After these scripts complete, the database should be fully populated.

## Example queries.

### Which airlines own the most active Boeing 747s (top 10)? How many do they own? In which countries are these airlines based?
```
MATCH (c:Country)<-[:BASED_IN]-(a:Airline)<-[:OWNED_BY]-(:Aircraft {status:'Active'})-[:SERIES]->()-[:MODEL]->(m:Model {name:'Boeing 747'})
WITH a, COUNT(m) AS count, c
ORDER BY count DESC
RETURN a.name AS Airline, c.name AS Country, count AS `Number of Boeing 747 Owned`
LIMIT 10
```

![Query 1](http://i.imgur.com/9qMNkfT.png)

### Visualize all the Airbus aircraft owned by Lufthansa.

```
MATCH p = (:Airline {name:'Lufthansa'})<-[:OWNED_BY]-(:Aircraft)-[:SERIES]->(:Series)-[:MODEL]->(m:Model)
WHERE substring(m.name, 0 , 6) = 'Airbus'
RETURN p
```

![Query 2](http://i.imgur.com/v09tJFN.png)
