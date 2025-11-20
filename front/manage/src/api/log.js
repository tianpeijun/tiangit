import request from '../utils/request'

export function getLogs(params) {
  return request({
    url: '/manage/logs',
    method: 'get',
    params
  })
}

export function getLogDetail(id) {
  return request({
    url: `/manage/logs/${id}`,
    method: 'get'
  })
}
