const path = require('path');

module.exports = {
    entry: './src/assets/scripts/index.js',
    output: {
        'path': path.resolve(__dirname, 'src', 'static','bund'),
        'filename': 'app.bundle.js',
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            }
        ]
    },
    optimization: {
        minimize: true
 }
}