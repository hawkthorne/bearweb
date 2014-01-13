# StackMachine API

## api.stackmachine.com


## sdk.stackmachine.com

This is the API game clients use.

### POST /games/{id}/metrics

```
{ 
  "metrics": [{
    "event": "foobar",
    "properties": {
      "key": "value"
    }
  }]
}
```

### POST /games/{id}/errors

```
{ 
  "errors": [{
    "message": "foobar",
    "tags": {
      "os": "windows|osx|linux",
      "version": "0.0.0",
      "distinct_id": "client-id"
    }
  }]
}
```

### GET /games/{id}/appcast

