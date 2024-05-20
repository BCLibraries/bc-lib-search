> [!IMPORTANT]
> Archived May 2024. No longer used or open for changes.


## bc-lib-search

Indexing support for the Boston College Libraries' "bento" search.

## Usage

    index-it.py index [--start START] source_dir sqlite_path elasticsearch_host
    index-it.py reindex sqlite_path elasticsearch_host 
    index-it.py publish  sqlite_path elasticsearch_host
    index-it.py autocomplete  sqlite_path elasticsearch_host

### Subcommands

* *`index`* – index new MARC records
* *`reindex`* – reindex existing MARC records
* *`publish`* – publish from SQLite database to ElasticSearch
* *`autocomplete`* – build autocomplete index

### Positional arguments
* *`source_dir`* – source directory
* *`sqlite_path`* – SQLite database
* *`elasticsearch_host`* – ElasticSearch host name

### Optional arguments
*  *`--start START`* – timestamp to import from
