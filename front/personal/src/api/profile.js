import request from '../utils/request'

export function getProfile() {
  return request({
    url: '/personal/profile',
    method: 'get'
  })
}

export function getAddress() {
  return request({
    url: '/personal/address',
    method: 'get'
  })
}

export function updateAddress(data) {
  return request({
    url: '/personal/address',
    method: 'put',
    data
  })
}
