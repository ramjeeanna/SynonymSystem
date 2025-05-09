# SynonymSystem
Synonym System using Flask with SQLServer with Pool and Cache configuration
Note: Any and all AI tools and software can be used to write and generate the code to meet this requirement.

Software Requirements Specification: Data Engine Synonym System
1. System Overview
The Data Engine Synonym System is designed to provide efficient access to synonym information with caching capabilities. The system interfaces with a SQL Server database and supports different caching strategies.
2. Functional Requirements
2.1 Synonym Retrieval
•	System shall retrieve synonym information from a SQL Server database
•	Each synonym record shall contain:
o	A unique word ID
o	The word itself
o	Associated synonyms
•	System shall support bulk retrieval of all synonym records. There is no single entry retrieval, only full table.
•	Results shall include metadata indicating whether they came from cache

Solultion Implemented:
=======================
The SQL Server Table is been created with three columns with id as a primary auto incrementable key
CREATE TABLE synonymsystem.dbo.dictionary (
    id INT IDENTITY(1,1) PRIMARY KEY,  -- Auto-incremented primary key
    word NVARCHAR(255) NOT NULL,       -- String column for words
    synonym NVARCHAR(255) NOT NULL     -- String column for synonyms
);

In the Flask, the db.Model is created with TblDictionary.Dictionary 

The Controller is implemented in controller.SynonymSystem.SynonymSystem with Flask Resource inherited with get,post, put, delete method.
API route is been added with api.add_resource(SynonymSystem, "/synonym", "/synonym/<inword>").  The Single as well as Bulk is achieved with this route defintion.

2.2 Caching System
•	System shall support multiple caching strategies:
o	Redis-based distributed caching
o	In-memory caching
•	Cache entries shall:
o	Have a configurable Time-To-Live (TTL)
o	Support automatic expiration
•	Cache shall store serialized synonym data for efficient retrieval

Solution Implemented
=====================
Flask App config is defined as app.cfg file with all config defition and Flask App is configured with Config_cache options.
At the time of application bringup, this file will be read and according to cache config, inmemroy (simple) or redis cache can be initialized.
TTL is configurable as well.
app.cfg file content is given below:
{
  "cache_config":{
    "cache_ttl":500,
    "cache_auto_expire":60,
    "type":"simple",
    "url": "redis://localhost:6379/0"
  },
  "db_config":{
    "pool_size": 10,
    "max_overflow":5,
    "pool_timeout":30,
    "pool_recycle":1800,
    "user_name":"root",
    "password":"rootpassword",
    "server_name":"DESKTOP-19I7FK3\\SQLEXPRESS",
    "db_name":"synonymsystem"
  }
}

3. Performance Requirements
•	System shall optimize database access by utilizing caching
•	Cache retrieval should be significantly faster than database queries
•	System shall handle connection pooling for database access
•	Cache operations should be atomic and thread-safe

Solution Implemented
====================
On API Endpoint, first the cache is referred with word or all combination.  for single word, the keys are created separately with word as a id in it.
So all the word based search will be handled by default as atomic search and addition/removal from cache with cache with auto delete timer.
The connection pool mechanism for SQL is impelemented via db_config in app.cfg file mentioned above.


APIs used for testing is given below:
=====================================

GET http://127.0.0.1:5000/api/v1/synonym

output
{
    "cached": false,
    "data": [
        {
            "id": 1,
            "synonym": "generate",
            "word": "create"
        },
        {
            "id": 2,
            "synonym": "glad",
            "word": "happy"
        },
        {
            "id": 3,
            "synonym": "joy",
            "word": "happy"
        },
        {
            "id": 5,
            "synonym": "sorrow",
            "word": "sad"
        },
        {
            "id": 6,
            "synonym": "enough",
            "word": "adequate"
        }
    ]
}

POST http://127.0.0.1:5000/api/v1/synonym
{
"word": "adequate",
"synonym":"enough"
}

Output:
{
    "result": "adequate:enough added successfully"
}

PUT http://127.0.0.1:5000/api/v1/synonym/adequate
{
"old_synonym":"sufficient",
"new_synonym":"enough"
}

Output:
{
    "message": "adequate is updated with  value enough"
}

DELETE http://127.0.0.1:5000/api/v1/synonym/sad

Output:
{
    "message": "Entries for all sad deleted successfully"
}
Architecture
App runs on FastAPI, so Django ORM is not ideal. Use SQLModel/SQLAlchemy.
