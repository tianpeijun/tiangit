import request from '../utils/request'

export function getProducts(params) {
  return request({
    url: '/api/personal/products',
    method: 'get',
    params
  })
}

export function getProductDetail(id) {
  return request({
    url: `/api/personal/products/${id}`,
    method: 'get'
  })
}

export function searchProducts(params) {
  return request({
    url: '/api/personal/products/search',
    method: 'get',
    params
  })
}

export function getCategories() {
  return request({
    url: '/api/personal/categories',
    method: 'get'
  })
}
