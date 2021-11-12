# Migration from jetfire-cli@v2 to transformations-cli@main

## Deploy Step Changes:
1. Deploy step should use `transformations-cli@main` instead of `jetfire-cli@v2`:
```yaml
# Github workflow
      - name: Transformations Deploy step
        uses: transformations-cli@main
```

2. `project-name` input should be renamed as `cdf-project-name`:

```yaml
# Github workflow
       with:
          path: <transformations_folder>
          ...
          cdf-project-name: extractor-bluefield-testing
          ...
```

3- Make sure `scopes` are space separated if you need multiple scopes:

```yaml
# Github workflow
       with:
          path: <transformations_folder>
          ...
          scopes: scope1 scope2 scope3
          ...
```

4- You can reference values as environment values or actual values in manifests, make sure you provide env variables you need in your manifests.
```yaml
# Github workflow
      env:
          TOKEN_URL: https://login.microsoftonline.com/someaad/oauth2/v2.0/token
          CLIENT_SECRET: ${{secrets.CLIENT_SECRET}}
          FIXED_TRANSFORMATION_NAME: example
```

```yaml
# Transformation manifest file

name: ${FIXED_TRANSFORMATION_NAME} # read from environment variable
externalId: hello # value is used directly
authentication:
   clientSecret: ${CLIENT_SECRET} # read from environment variable
   clientId: randomclientid # value is used directly 
   tokenUrl: ${TOKEN_URL} # read from environment variable
```

## Manifest Changes:
There are two options to achieve this: Set `legacy` flag on your existing manifest with no changes or start using the new format!

### Set legacy flag in your legacy manifest:
Add `legacy: true` to your legacy transformation manifests.

```yaml
# Legacy transformation manifest
legacy: true
name: hello
externalId: hello
...
```

### Start using the new manifest format:
Although we provide backward compatibility with the `legacy` flag, we recommend using the new manifest format as:
- it has an improved structure
- new functionality will only be made available in the new format
- it enables the use of environment variables

The following sections show the requirements for migrating the different fields of the manifest:

#### Migrate `name`:
- No changes required.

#### Migrate `externalId`:
- No changes required.

#### Migrate `destination`:
-  `assets`, `events`, `timeseries`, `datapoints`, `sequences`, `labels`, `relationships`, `files`, `raw` are now **case sensitive** and should be lower case.
- We now also support `data_sets`.
- These resource types change formatting:
<table>
<tr>
<th> Legacy (Case insensitive) </th>
<th> New (Case sensitive with underscores) </th>
</tr>
<tr>
<td>

`assethierarchy`

</td>
<td>

`asset_hierarchy`

</td>
</tr>
<tr>
<td>

`stringdatapoints`

</td>
<td>

`string_datapoints`

</td>
</tr>
</table>

#### Migrate `action`:
- No changes required.

#### Migrate `query`:
In the old version, the `query` field expected the path to a SQL file. Now you can either provide a SQL file path or provide the query directly as a string.


<table>
<tr>
<th> Legacy </th>
<th> New </th>
</tr>
<tr>
<td>

```yaml
# Legacy transformation manifest
query: my_query.sql
```

</td>
<td>

```yaml
#  Transformation manifest
query: "select 'asset1' as name"
```

```yaml
#  Transformation manifest
query:
    file:
        my_query.sql
```

</td>
</tr>
</table>

#### Migrate `schedule`:
- No changes required.

#### Migrate `shared`:
- No changes required, default is changed to `true`.

#### Migrate `ignoreNullFields`:
- No changes required.

#### Migrate `apiKey`:
- `apiKey` values used to be treated as environment variables in `jetfire-cli`. Now you need to reference them as `${API_KEY}` instead of `API_KEY` to treat them as environment variables.

<table>
<tr>
<th> Legacy </th>
<th> New </th>
</tr>
<tr>
<td>

```yaml
# Legacy transformation manifest
apiKey: API_KEY # as provided in deploy step
```

</td>
<td>

```yaml
#  Transformation manifest
authentication:
    apiKey: ${API_KEY} # as provided in deploy step
```

</td>
</tr>
</table>


#### Migrate `authentication`:
- `clientId` and `clientSecret` were assumed to be environment variables while others are used as actual values.:
- Also, we added support for `audience` parameter to retrieve the token.
<table>
<tr>
<th> Legacy </th>
<th> New </th>
</tr>
<tr>
<td>

```yaml
# Legacy ransformation manifest
...
  # The following two is given as the name of an environment variable
  clientId: COGNITE_CLIENT_ID
  clientSecret: COGNITE_CLIENT_SECRET
  # The following are explicit values, not environment variables
  tokenUrl: https://my-idp.com/oauth2/token
  scopes:
    - https://bluefield.cognitedata.com/.default
  cdfProjectName: my-project
...
```
</td>
<td>

```yaml
# Transformation manifest
...
  clientId: ${CLIENT_ID}
  clientSecret: ${CLIENT_SECRET}
  tokenUrl: https://my-idp.com/oauth2/token
  scopes: 
    - https://bluefield.cognitedata.com/.default
  cdfProjectName: my-project
  # audience: ""
...
```

</td>
</tr>
</table>

- `apiKey` configuration is moved under `authentication`.

<table>
<tr>
<th> Legacy </th>
<th> New </th>
</tr>
<tr>
<td>

```yaml
# Legacy ransformation manifest
apiKey: API_KEY # as provided in deploy step
```

```yaml
# Legacy ransformation manifest
apiKey: 
    read: READ_API_KEY # as provided in deploy step
    write: WRITE_API_KEY # as provided in deploy step
```

</td>
<td>

```yaml
# Transformation manifest
authentication:
    apiKey: ${API_KEY} # as provided in deploy step
```

```yaml
# Transformation manifest
authentication:
    apiKey: 
        read: ${READ_API_KEY} # as provided in deploy step
        write: ${WRITE_API_KEY} # as provided in deploy step
```

</td>
</tr>
</table>

#### Migrate `notifications`:
- No changes required for `jetfire-cli@v2`.
- If you are migrating from `jetfire-cli@v1`, make sure that you reflect notifications in your manifests. Missing notifications on existing transformations get deleted.



