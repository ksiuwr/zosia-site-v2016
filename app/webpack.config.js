const BabiliPlugin = require("babili-webpack-plugin");

const config = {
  entry: './static/script/room.js',
  output: {
    path: './static/script/',
    filename: 'room.min.js'
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        exclude: /(node_modules|bower_components)/,
        loader: 'babel-loader',
        query: {
          plugins: ['transform-react-jsx'],
          presets: ['es2015']
        }
      }
    ]
  },
  plugins: [
    new BabiliPlugin()
  ]
};

module.exports = config;
