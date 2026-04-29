import persons from '@data/exports/persons/full/persons.json'

const SOURCES = ['imdb', 'wikidata', 'tmdb']

export function getStaticPaths() {
  return persons.flatMap((person) =>
    SOURCES
      .filter((s) => person[s + '_id'])
      .map((s) => ({
        params: {
          source: s,
          source_id: String(person[s + '_id'])
        }
      }))
  )
}

export function GET({ params }) {
  const field = params.source + '_id'
  const person = persons.find((p) => p[field] === params.source_id)
  if (!person) {
    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    })
  }
  return new Response(JSON.stringify(person), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
