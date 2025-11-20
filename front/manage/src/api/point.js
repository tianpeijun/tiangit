import request from '../utils/request'

export function grantPoints(data) {
  return request({
    url: '/api/manage/points/grant',
    method: 'post',
    data
  })
}

export function grantPointsBatch(data) {
  return request({
    url: '/api/manage/points/grant-batch',
    method: 'post',
    params: data  // 使用 params 而不是 data，因为后端期望查询参数
  })
}
