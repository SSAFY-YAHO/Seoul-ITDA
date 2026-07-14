import { request } from './client'

export async function fetchPosts(params = {}) {
  const query = new URLSearchParams()
  if (params.q) {
    query.set('q', params.q)
  }

  const endpoint = `/api/posts${query.toString() ? `?${query.toString()}` : ''}`
  return request(endpoint)
}

export async function fetchPostById(postId) {
  return request(`/api/posts/${postId}`)
}

export async function createPost(payload) {
  return request('/api/posts', {
    method: 'POST',
    body: payload,
  })
}

export async function updatePost(postId, payload) {
  return request(`/api/posts/${postId}`, {
    method: 'PUT',
    body: payload,
  })
}

export async function deletePost(postId, payload) {
  return request(`/api/posts/${postId}`, {
    method: 'DELETE',
    body: payload,
  })
}
