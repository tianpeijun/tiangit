import request from '../utils/request'

export function getProfile() {
  return request({
    url: '/api/personal/profile',
    method: 'get'
  })
}

export function getAddress() {
  return request({
    url: '/api/personal/address',
    method: 'get'
  })
}

export function updateAddress(data) {
  return request({
    url: '/api/personal/address',
    method: 'put',
    data
  })
}
