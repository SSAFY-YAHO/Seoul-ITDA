import { request } from './client'

export async function sendChatMessage(payload) {
  return request('/api/chat', {
    method: 'POST',
    body: payload,
    timeout: 70000,
  })
}
