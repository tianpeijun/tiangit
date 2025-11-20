/**
 * 图片 URL 处理工具
 */

// API Base URL（从环境变量获取）
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000'

/**
 * 获取完整的图片 URL
 * @param {string} imagePath - 图片路径（可能是相对路径或完整URL）
 * @returns {string} 完整的图片 URL
 */
export function getImageUrl(imagePath) {
  if (!imagePath) {
    // 使用 ALB URL 作为 placeholder
    return `${API_BASE_URL}/static/placeholder.png`
  }

  // 如果已经是完整的 URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }

  // 如果是相对路径，拼接 API Base URL
  // 确保路径以 / 开头
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`
  
  return `${API_BASE_URL}${path}`
}

/**
 * 获取缩略图 URL
 * @param {string} imagePath - 图片路径
 * @returns {string} 缩略图 URL
 */
export function getThumbnailUrl(imagePath) {
  return getImageUrl(imagePath)
}
