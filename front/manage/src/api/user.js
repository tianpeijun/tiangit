import request from '../utils/request'

export function getUsers(params) {
  return request({
    url: '/manage/users',
    method: 'get',
    params
  })
}

export function getUserDetail(id) {
  return request({
    url: `/manage/users/${id}`,
    method: 'get'
  })
}

export function createUser(data) {
  return request({
    url: '/manage/users',
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({
    url: `/manage/users/${id}`,
    method: 'put',
    data
  })
}

export function deleteUser(id) {
  return request({
    url: `/manage/users/${id}`,
    method: 'delete'
  })
}

export function toggleUserStatus(id, data) {
  return request({
    url: `/manage/users/${id}/status`,
    method: 'put',
    data
  })
}

export function resetPassword(id, data) {
  return request({
    url: `/manage/users/${id}/reset-password`,
    method: 'post',
    data
  })
}
