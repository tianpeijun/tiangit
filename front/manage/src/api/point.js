import request from '../utils/request'

export function grantPoints(data) {
  return request({
    url: '/manage/points/grant',
    method: 'post',
    data
  })
}

export function grantPointsBatch(data) {
  return request({
    url: '/manage/points/grant-batch',
    method: 'post',
    data
  })
}
