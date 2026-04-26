import movies from '@data/exports/movies/full/movies.json'

const SOURCES = ['imdb', 'wikidata', 'tmdb', 'letterboxd']

export function getStaticPaths() {
  return movies.flatMap((movie) =>
    SOURCES
      .filter((s) => movie[s + '_id'])
      .map((s) => ({
        params: {
          source: s,
          source_id: String(movie[s + '_id'])
        }
      }))
  )
}

export function GET({ params }) {
  const field = params.source + '_id'
  const movie = movies.find((m) => m[field] === params.source_id)
  if (!movie) {
    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    })
  }
  return new Response(JSON.stringify(movie), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
