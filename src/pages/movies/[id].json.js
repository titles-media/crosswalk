import movies from '@data/exports/movies/full/by_id/movies.id.json'

export function getStaticPaths() {
  return Object.keys(movies).map((id) => ({ params: { id } }))
}

export function GET({ params }) {
  const movie = movies[params.id]
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
