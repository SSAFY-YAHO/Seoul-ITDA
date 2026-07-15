<script setup>
import { ref } from 'vue'
import { isCloudinaryConfigured, uploadCommunityImage } from '../../api/cloudinary'

const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])
const uploading = ref(false)
const error = ref('')
const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']

async function selectFiles(event) {
  const files = Array.from(event.target.files || [])
  event.target.value = ''
  error.value = ''
  if (!isCloudinaryConfigured) { error.value = 'Netlify에 Cloudinary 환경변수를 먼저 설정해주세요.'; return }
  if (props.modelValue.length + files.length > 5) { error.value = '사진은 게시글당 최대 5장까지 첨부할 수 있습니다.'; return }
  const invalid = files.find((file) => !allowedTypes.includes(file.type) || file.size > 5 * 1024 * 1024)
  if (invalid) { error.value = 'JPG, PNG, WebP 파일만 장당 5MB 이하로 첨부할 수 있습니다.'; return }
  uploading.value = true
  try {
    const urls = await Promise.all(files.map(uploadCommunityImage))
    emit('update:modelValue', [...props.modelValue, ...urls])
  } catch (err) { error.value = err.message || '사진 업로드에 실패했습니다.' }
  finally { uploading.value = false }
}

function removeImage(index) {
  emit('update:modelValue', props.modelValue.filter((_, itemIndex) => itemIndex !== index))
}
</script>

<template>
  <section class="post-image-uploader">
    <div class="post-image-uploader__head"><div><strong>사진 첨부</strong><small>최대 5장 · JPG, PNG, WebP · 장당 5MB</small></div><span>{{ modelValue.length }}/5</span></div>
    <div v-if="modelValue.length" class="post-image-previews">
      <figure v-for="(url,index) in modelValue" :key="url"><img :src="url" :alt="`첨부 사진 ${index + 1}`"/><button type="button" :aria-label="`사진 ${index + 1} 삭제`" @click="removeImage(index)">×</button></figure>
    </div>
    <label v-if="modelValue.length < 5" class="post-image-add" :class="{ disabled: uploading }">
      <input type="file" accept="image/jpeg,image/png,image/webp" multiple :disabled="uploading" @change="selectFiles"/>
      <span>{{ uploading ? '사진 올리는 중…' : '＋ 사진 선택하기' }}</span>
    </label>
    <p v-if="error" class="form-error">{{ error }}</p>
  </section>
</template>

<style scoped>
.post-image-uploader { display:grid; gap:13px; padding:18px; border:1px dashed #b9ccb7; border-radius:18px; background:#f8faf3; }.post-image-uploader__head { display:flex; justify-content:space-between; gap:12px; }.post-image-uploader__head div { display:grid; }.post-image-uploader__head small { margin-top:3px; color:#7b897e; }.post-image-uploader__head > span { color:#52705c; font-weight:900; }.post-image-previews { display:grid; grid-template-columns:repeat(5,1fr); gap:9px; }.post-image-previews figure { position:relative; aspect-ratio:1; margin:0; overflow:hidden; border-radius:12px; background:#e5ecdf; }.post-image-previews img { width:100%; height:100%; object-fit:cover; }.post-image-previews button { position:absolute; top:5px; right:5px; width:25px; height:25px; border-radius:50%; background:rgba(42,58,47,.75); color:white; font-size:18px; line-height:1; }.post-image-add { display:grid; place-items:center; min-height:64px; border:1px solid #cad8c6; border-radius:13px; background:white; color:#52705c; font-weight:850; cursor:pointer; }.post-image-add:hover { background:#f0f6e9; }.post-image-add.disabled { cursor:wait; opacity:.65; }.post-image-add input { position:absolute; width:1px; height:1px; overflow:hidden; opacity:0; }.form-error { margin:0; }
@media(max-width:640px){.post-image-previews{grid-template-columns:repeat(3,1fr)}}
</style>
