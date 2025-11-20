import request from '../utils/request'

export function login(data) {
  return request({
    url: '/api/auth/login',
    method: 'post',
    data
  })
}

export function logout() {
  return request({
    url: '/api/auth/logout',
    method: 'post'
  })
}

export function getCurrentUser() {
  return request({
    url: '/api/auth/current-user',
    method: 'get'
  })
}

export function changePassword(data) {
  return request({
    url: '/api/auth/password/change',
    method: 'post',
    data
  })
}
