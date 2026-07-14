import { request } from './client'

export async function fetchFestivals() {
  try {
    return await request('/api/festivals')
  } catch (error) {
    if (error.message?.includes('404') || error.message?.includes('not found')) {
      return []
    }
    throw error
  }
}
