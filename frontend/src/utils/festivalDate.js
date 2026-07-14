function normalizeDateValue(value) {
  if (!value && value !== 0) {
    return null
  }

  if (value instanceof Date) {
    return value
  }

  if (typeof value === 'number') {
    return new Date(value)
  }

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return null

    const compact = trimmed.replace(/[^0-9]/g, '')
    if (/^\d{8}$/.test(compact)) {
      const year = Number(compact.slice(0, 4))
      const month = Number(compact.slice(4, 6)) - 1
      const day = Number(compact.slice(6, 8))
      return new Date(year, month, day)
    }

    const parsed = new Date(trimmed)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed
    }
  }

  return null
}

export function parseFestivalDateRange(item) {
  const startRaw = item?.startDate || item?.start_date || item?.start || item?.eventStartDate || item?.event_start_date
  const endRaw = item?.endDate || item?.end_date || item?.end || item?.eventEndDate || item?.event_end_date

  const start = normalizeDateValue(startRaw)
  if (!start) {
    return null
  }

  const end = normalizeDateValue(endRaw)
  if (!end || end < start) {
    return {
      start,
      end: new Date(start.getFullYear(), start.getMonth(), start.getDate() + 1),
    }
  }

  return {
    start,
    end: new Date(end.getFullYear(), end.getMonth(), end.getDate() + 1),
  }
}

export function formatFestivalPeriod(item) {
  const parsed = parseFestivalDateRange(item)
  if (!parsed) {
    return '기간 정보 미정'
  }

  const start = parsed.start.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
  const end = parsed.end.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
  return `${start} ~ ${end}`
}

export function toCalendarEvent(item, index) {
  const parsed = parseFestivalDateRange(item)
  if (!parsed) {
    return null
  }

  return {
    id: item?.id || item?.festivalId || item?.festival_id || `${item?.title || 'festival'}-${index}`,
    title: item?.title || item?.name || item?.festivalName || '축제',
    start: parsed.start.toISOString().slice(0, 10),
    end: parsed.end.toISOString().slice(0, 10),
    allDay: true,
    extendedProps: {
      place: item?.place || item?.venue || item?.location || '',
      address: item?.address || '',
      description: item?.description || item?.summary || item?.content || '',
      imageUrl: item?.imageUrl || item?.image_url || item?.mainImage || '',
      homepageUrl: item?.homepageUrl || item?.homepage_url || item?.url || '',
      phone: item?.phone || item?.contact || '',
      category: item?.category || item?.type || '',
      originalData: item,
    },
  }
}
