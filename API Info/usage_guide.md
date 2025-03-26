# openFDA API Usage Guide

This guide provides an overview of how to effectively utilize the openFDA API, focusing on search, sort, and count functionalities, including combining multiple parameters and performing exact searches.

## 1. Query Parameters

The openFDA API supports several query parameters to filter and manipulate data:

- `search`: Filters records based on specific field values.
- `sort`: Orders the results by a specified field in ascending (`:asc`) or descending (`:desc`) order.
- `count`: Aggregates the number of unique values for a specified field.
- `limit`: Specifies the number of records to return (maximum is 1000).
- `skip`: Skips a specified number of records, useful for pagination (maximum is 25,000).

## 2. Searching with Multiple Criteria

To filter data based on multiple conditions, use the `search` parameter with logical operators:

- **AND (`+AND+`)**: Retrieves records that match all specified conditions.

  *Example*: To find records where the `proprietary_name` is "FOO" and the `manufacturer_name` is "BAR":

  ```
  search=proprietary_name:"FOO"+AND+manufacturer_name:"BAR"
  ```

- **OR (`+OR+`)**: Retrieves records that match any of the specified conditions.

  *Example*: To find records where the `proprietary_name` is either "FOO" or "BAR":

  ```
  search=proprietary_name:"FOO"+OR+proprietary_name:"BAR"
  ```

## 3. Sorting Results

Use the `sort` parameter to order search results:

- **Ascending Order**: Append `:asc` to the field name.

  *Example*: To sort by `approval_date` in ascending order:

  ```
  sort=approval_date:asc
  ```

- **Descending Order**: Append `:desc` to the field name.

  *Example*: To sort by `approval_date` in descending order:

  ```
  sort=approval_date:desc
  ```

## 4. Counting Records

The `count` parameter aggregates data based on unique values of a specified field:

*Example*: To count occurrences of each `proprietary_name`:

```
count=proprietary_name
```

For exact matches (considering the entire phrase):

```
count=proprietary_name.exact
```

## 5. Combining Search, Sort, and Count

These parameters can be combined to refine queries:

*Example*: To find records where the `proprietary_name` is "FOO" and sort them by `approval_date` in descending order:

```
search=proprietary_name:"FOO"&sort=approval_date:desc
```

## 6. Exact vs. Tokenized Searches

Understanding the difference between tokenized and exact searches is crucial:

- **Tokenized Search**: Breaks down the search term into individual words and retrieves records containing any of those words.

  *Example*: `search=proprietary_name:"FOO BAR"` returns records containing either "FOO" or "BAR" anywhere in the `proprietary_name` field.

- **Exact Search**: Looks for the exact phrase as a whole.

  *Example*: `search=proprietary_name.exact:"FOO BAR"` returns records where the `proprietary_name` field matches exactly "FOO BAR".

By mastering these parameters and their combinations, you can craft precise queries to navigate the openFDA API effectively. 