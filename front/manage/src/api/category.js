import request from '../utils/request'

export function getCategories() {
  return request({
    url: '/manage/categories',
    method: 'get'
  })
}

export function getCategoryDetail(id) {
  return request({
    url: `/manage/categories/${id}`,
    method: 'get'
  })
}

export function createCategory(data) {
  return request({
    url: '/manage/categories',
    method: 'post',
    data
  })
}

export function updateCategory(id, data) {
  return request({
    url: `/manage/categories/${id}`,
    method: 'put',
    data
  })
}

export function deleteCategory(id) {
  return request({
    url: `/manage/categories/${id}`,
    method: 'delete'
  })
}
