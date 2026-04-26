# titles.media crosswalk

Stable identifier mappings for film works across IMDb, TMDB, Letterboxd, and Wikidata — served as static JSON, CSV, and NDJSON via GitHub Pages at [`crosswalk.titles.media`](https://crosswalk.titles.media).

This repo is the **automated build output** of [`titles-media/crosswalk-data`](https://github.com/titles-media/crosswalk-data). Exports are regenerated on every merge to that repo and committed here by CI. Do not edit `exports/` by hand.

## Using the data

Exports are available at `crosswalk.titles.media/exports/movies/` in two flavours:

- **`full/`** — all fields: `id`, `title`, `year`, `imdb_id`, `wikidata_id`, `tmdb_id`, `letterboxd_id`
- **`ids/`** — identifier fields only, no title or year

Each flavour ships as:

| File | Description |
|---|---|
| `movies.json` | JSON array, pretty-printed |
| `movies.min.json` | JSON array, minified |
| `movies.csv` | CSV with header row |
| `movies.ndjson` | One JSON object per line |
| `by_id/movies.{field}.json` | Dict keyed by identifier field |
| `by_id/movies.{field}.min.json` | Minified version |

`by_id` files exist for each identifier field: `id`, `imdb_id`, `tmdb_id`, `letterboxd_id`, `wikidata_id`. Rows with an empty value for a given field are omitted from that file. `movies.id.json` always contains all rows.

## Record shape

```json
{
  "id": "p148c7y3",
  "title": "Project Hail Mary",
  "year": 2026,
  "imdb_id": "tt12042730",
  "wikidata_id": "Q107105860",
  "tmdb_id": "687163",
  "letterboxd_id": "project-hail-mary"
}
```

Internal IDs are stable and permanent — see [crosswalk-data](https://github.com/titles-media/crosswalk-data) for details on ID assignment.

## Contributing

**To add or update film data** — open a pull request in [`titles-media/crosswalk-data`](https://github.com/titles-media/crosswalk-data). Changes there trigger an automated rebuild here.

**To contribute to the build tooling** — pull requests in this repo are welcome for changes to `scripts/`, workflows, or configuration.

**Additional output formats** — we're open to supporting new formats, but please open a discussion issue before submitting a PR. Because exports are committed to git, non-binary open formats are strongly preferred — formats like Parquet or SQLite are unlikely to be accepted.

## Attribution

Source data is maintained in [`titles-media/crosswalk-data`](https://github.com/titles-media/crosswalk-data). External identifier data is sourced from IMDb, TMDB, Letterboxd, and Wikidata — see that repo for full attribution details.

## Licensing

Build scripts are released under the [MIT License](LICENSE).

Data exports are released under the [Open Data Commons Attribution License (ODC-BY 1.0)](LICENSE-DATA). You are free to use, share, and adapt the data as long as you attribute titles.media as the source.
