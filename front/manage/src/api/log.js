import request from '../utils/request'

export function getLogs(params) {
  return request({
    url: '/api/manage/logs',
    method: 'get',
    params
  })
}

export function getLogDetail(id) {
  return request({
    url: `/api/manage/logs/${id}`,
    method: 'get'
  })
}
