import { request } from './client'

export async function fetchLocations() {
  return request('/api/locations')
}
