import request from '../utils/request'

export function createOrder(data) {
  return request({
    url: '/personal/orders/create',
    method: 'post',
    data
  })
}

export function getOrders(params) {
  return request({
    url: '/personal/orders',
    method: 'get',
    params
  })
}

export function getOrderDetail(id) {
  return request({
    url: `/personal/orders/${id}`,
    method: 'get'
  })
}
