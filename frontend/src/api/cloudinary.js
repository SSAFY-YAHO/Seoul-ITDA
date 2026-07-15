const cloudName = (import.meta.env.VITE_CLOUDINARY_CLOUD_NAME || '').trim()
const uploadPreset = (import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET || '').trim()

export const isCloudinaryConfigured = Boolean(cloudName && uploadPreset)

export async function uploadCommunityImage(file) {
  if (!isCloudinaryConfigured) {
    throw new Error('사진 업로드 설정이 아직 완료되지 않았습니다.')
  }

  const formData = new FormData()
  formData.append('file', file)
  formData.append('upload_preset', uploadPreset)
  formData.append('folder', 'seoul-itda/community')

  const response = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/image/upload`, {
    method: 'POST',
    body: formData,
  })
  const payload = await response.json().catch(() => null)
  if (!response.ok || !payload?.secure_url) {
    throw new Error(payload?.error?.message || '사진을 업로드하지 못했습니다.')
  }
  return payload.secure_url
}
