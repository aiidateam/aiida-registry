import json from '@rollup/plugin-json';

export default {
  input: 'src/App.jsx',
  output: {
    dir: 'output',
    format: 'cjs'
  },
  plugins: [json()]
};
