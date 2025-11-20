module.exports = {
  outputDir: '../static/manage',
  publicPath: '/',
  devServer: {
    port: 8081,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].title = 'AWSomeShop - 管理端'
      return args
    })
  }
}
