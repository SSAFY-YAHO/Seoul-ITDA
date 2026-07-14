import { request } from './client'

export async function fetchFestivals(params = {}) {
  const query = new URLSearchParams()
  if (params.q) {
    query.set('q', params.q)
  }
  if (params.status) {
    query.set('status', params.status)
  }
  if (params.startDate) {
    query.set('start_date', params.startDate)
  }
  if (params.endDate) {
    query.set('end_date', params.endDate)
  }

  const endpoint = `/api/festivals${query.toString() ? `?${query.toString()}` : ''}`

  try {
    return await request(endpoint)
  } catch (error) {
    if (error.message?.includes('404') || error.message?.includes('not found')) {
      return []
    }
    throw error
  }
}
