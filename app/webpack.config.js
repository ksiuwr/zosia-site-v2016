const webpack = require('webpack');
const path = require('path');

const config = {
  entry: {
    room: './static/script/room.js',
  },
  output: {
    filename: '[name].min.js',
    path: path.resolve(__dirname, 'static/script/')
  },
  plugins: [
    new webpack.ProgressPlugin(),
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: [
          'babel-loader',
        ],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};
 

module.exports = config;
