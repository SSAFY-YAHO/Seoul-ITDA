const DEFAULT_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').trim()

function buildUrl(path) {
  const normalizedBase = DEFAULT_BASE_URL.replace(/\/$/, '')
  return `${normalizedBase}${path.startsWith('/') ? path : `/${path}`}`
}

function normalizeErrorMessage(payload, fallbackMessage) {
  if (!payload) {
    return fallbackMessage
  }

  if (typeof payload === 'string') {
    return payload
  }

  if (typeof payload === 'object') {
    if (typeof payload.message === 'string') {
      return payload.message
    }

    if (typeof payload.error === 'string') {
      return payload.error
    }

    if (Array.isArray(payload.detail)) {
      const firstDetail = payload.detail[0]
      if (typeof firstDetail?.msg === 'string') {
        return firstDetail.msg
      }
    }

    if (typeof payload.detail === 'string') {
      return payload.detail
    }
  }

  return fallbackMessage
}

export async function request(path, options = {}) {
  const method = options.method || 'GET'
  const headers = new Headers(options.headers || {})

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const requestOptions = {
    method,
    headers,
    signal: options.signal,
  }

  if (options.body !== undefined && options.body !== null) {
    requestOptions.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body)
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || 10000)
  requestOptions.signal = controller.signal

  try {
    const response = await fetch(buildUrl(path), requestOptions)
    const contentType = response.headers.get('content-type') || ''
    let payload = null

    if (contentType.includes('application/json')) {
      payload = await response.json().catch(() => null)
    } else {
      payload = await response.text().catch(() => null)
    }

    if (!response.ok) {
      throw new Error(normalizeErrorMessage(payload, '요청을 처리하지 못했습니다. 잠시 후 다시 시도해주세요.'))
    }

    return payload
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요.')
    }

    if (error instanceof Error) {
      throw error
    }

    throw new Error('요청을 처리하지 못했습니다. 잠시 후 다시 시도해주세요.')
  } finally {
    clearTimeout(timeoutId)
  }
}

export async function getHealth() {
  return request('/api/health')
}

export const apiBaseUrl = DEFAULT_BASE_URL
