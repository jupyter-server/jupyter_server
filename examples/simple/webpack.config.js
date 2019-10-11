module.exports = {
  entry: ['./jupyter_simple_ext/static/index.js'],
  output: {
    path: require('path').join(__dirname, 'jupyter_simple_ext', 'static'),
    filename: 'bundle.js'
  },
  mode: 'development'
}
