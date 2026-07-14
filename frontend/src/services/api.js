const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchHealth() {
  const response = await fetch(`${apiBaseUrl}/api/health`)

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`)
  }

  return response.json()
}

export { apiBaseUrl }