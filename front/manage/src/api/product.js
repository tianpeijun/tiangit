import request from '../utils/request'

export function getProducts(params) {
  return request({
    url: '/manage/products',
    method: 'get',
    params
  })
}

export function getProductDetail(id) {
  return request({
    url: `/manage/products/${id}`,
    method: 'get'
  })
}

export function createProduct(data) {
  return request({
    url: '/manage/products',
    method: 'post',
    data
  })
}

export function updateProduct(id, data) {
  return request({
    url: `/manage/products/${id}`,
    method: 'put',
    data
  })
}

export function deleteProduct(id) {
  return request({
    url: `/manage/products/${id}`,
    method: 'delete'
  })
}

export function toggleProductStatus(id, status) {
  return request({
    url: `/manage/products/${id}/status`,
    method: 'put',
    params: { status }
  })
}

export function uploadProductImages(id, formData) {
  return request({
    url: `/manage/products/${id}/images`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function deleteProductImage(imageId) {
  return request({
    url: `/manage/products/images/${imageId}`,
    method: 'delete'
  })
}
