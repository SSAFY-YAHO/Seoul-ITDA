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

export async function likePost(postId) {
  return request(`/api/posts/${postId}/like`, {
    method: 'POST',
  })
}

export async function fetchComments(postId) {
  return request(`/api/posts/${postId}/comments`)
}

export async function createComment(postId, payload) {
  return request(`/api/posts/${postId}/comments`, {
    method: 'POST',
    body: payload,
  })
}

export async function likeComment(postId, commentId) {
  return request(`/api/posts/${postId}/comments/${commentId}/like`, {
    method: 'POST',
  })
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
