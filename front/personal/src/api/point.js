import request from '../utils/request'

export function getPointsBalance() {
  return request({
    url: '/api/personal/points/balance',
    method: 'get'
  })
}

export function getPointsTransactions(params) {
  return request({
    url: '/api/personal/points/transactions',
    method: 'get',
    params
  })
}
