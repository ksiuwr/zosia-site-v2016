const webpack = require('webpack');
const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');

const config = {
  entry: {
    room: './js/room.js',
  },
  output: {
    filename: '[name].min.js',
    path: path.resolve(__dirname, 'static/script/')
  },
  plugins: [
    new webpack.ProgressPlugin(),
    new CopyWebpackPlugin([
      {
        from: path.resolve(__dirname, './node_modules/jquery/dist/jquery.min.js'),
        to: path.resolve(__dirname, './static/script/jquery.min.js'),
      },
      {
        from: path.resolve(__dirname, './node_modules/materialize-css/dist/js/materialize.min.js'),
        to: path.resolve(__dirname, './static/script/materialize.min.js'),
      },
      {
        from: path.resolve(__dirname, './node_modules/materialize-css/dist/css/materialize.min.css'),
        to: path.resolve(__dirname, './static/css/materialize.min.css'),
      },
      {
        from: path.resolve(__dirname, './node_modules/materialize-css/extras/noUiSlider/nouislider.min.js'),
        to: path.resolve(__dirname, './static/script/nouislider.min.js'),
      },
      {
        from: path.resolve(__dirname, './node_modules/materialize-css/extras/noUiSlider/nouislider.css'),
        to: path.resolve(__dirname, './static/css/nouislider.css'),
      },
      {
        from: path.resolve(__dirname, './node_modules/materialize-css/dist/fonts'),
        to: path.resolve(__dirname, './static/fonts'),
      },
    ]),
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
            plugins: ["@babel/plugin-proposal-class-properties"],
          },
        },
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};
 
module.exports = config;

