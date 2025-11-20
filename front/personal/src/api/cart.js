import request from '../utils/request'

export function getCart() {
  return request({
    url: '/api/personal/cart',
    method: 'get'
  })
}

export function addToCart(data) {
  return request({
    url: '/api/personal/cart/add',
    method: 'post',
    data
  })
}

export function updateCartItem(data) {
  return request({
    url: '/api/personal/cart/update',
    method: 'put',
    data
  })
}

export function removeFromCart(productId) {
  return request({
    url: `/api/personal/cart/remove/${productId}`,
    method: 'delete'
  })
}

export function clearCart() {
  return request({
    url: '/api/personal/cart/clear',
    method: 'delete'
  })
}
