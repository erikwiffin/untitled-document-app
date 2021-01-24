const path = require('path');
 
module.exports = {
  entry: {
    vendor: ['react', 'react-dom', 'jquery', 'bootstrap'],
    styles: path.resolve(__dirname, './src/styles.scss'),
    fileUpload: path.resolve(__dirname, './src/file-upload/index.js'),
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader']
      },
      {
        test: /\.(scss)$/,
          use: [
            {
              loader: 'style-loader', // inject CSS to page
            },
            {
              loader: 'css-loader', // translates CSS into CommonJS modules
            },
            {
              loader: 'postcss-loader', // Run postcss actions
              options: {
                postcssOptions: {
                  plugins: [
                    require('autoprefixer')
                  ]
                }
              }
            },
            {
              loader: 'sass-loader' // compiles Sass to CSS
            }
          ]
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts/'
            }
          }
        ]
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
  output: {
    path: path.resolve(__dirname, '../server/document_app/static/dist'),
    filename: '[name].bundle.js',
  },
};
