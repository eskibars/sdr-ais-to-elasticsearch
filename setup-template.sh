curl -XPUT "http://127.0.0.1:9200" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["ais-*", "ships-*"],
  "mappings": {
    "_doc": {
      "properties": {
        "name": {
          "type": "text"
        },
        "position_accuracy": {
          "type": "integer"
        },
        "location": {
          "type": "geo_point"
        },
        "curtime": {
          "type": "date"
        }
      }
    }
  },
  "settings": {
    "number_of_shards": 1
  }
}'
