import { request } from './client'

export async function fetchLocations(params = {}) {
  const query = new URLSearchParams()
  if (params.category) query.set('category', params.category)
  if (params.limit) query.set('limit', String(params.limit))
  return request(`/api/locations${query.toString() ? `?${query}` : ''}`)
}
