import request from '../utils/request'

export function getCart() {
  return request({
    url: '/personal/cart',
    method: 'get'
  })
}

export function addToCart(data) {
  return request({
    url: '/personal/cart/add',
    method: 'post',
    data
  })
}

export function updateCartItem(data) {
  return request({
    url: '/personal/cart/update',
    method: 'put',
    data
  })
}

export function removeFromCart(productId) {
  return request({
    url: `/personal/cart/remove/${productId}`,
    method: 'delete'
  })
}

export function clearCart() {
  return request({
    url: '/personal/cart/clear',
    method: 'delete'
  })
}
