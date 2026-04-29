import persons from '@data/exports/persons/full/by_id/persons.id.json'

export function getStaticPaths() {
  return Object.keys(persons).map((id) => ({ params: { id } }))
}

export function GET({ params }) {
  const person = persons[params.id]
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
