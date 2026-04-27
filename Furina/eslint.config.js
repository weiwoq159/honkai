import js from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import pluginVue from 'eslint-plugin-vue'
import json from '@eslint/json'
import css from '@eslint/css'
import { defineConfig } from 'eslint/config'
import prettier from 'eslint-config-prettier'
import pluginPrettier from 'eslint-plugin-prettier'

export default defineConfig([
  {
    files: ['**/*.{js,mjs,cjs,ts,mts,cts,vue}'],
    plugins: { js },
    extends: ['js/recommended'],
    rules: {
      'linebreak-style': ['error', 'unix'], // 改为 "windows" 可兼容 CRLF
      indent: ['error', 2], // 添加缩进规则：2 个空格
    },
  },
  {
    files: ['**/*.{js,mjs,cjs,ts,mts,cts,vue}'],
    plugins: { prettier: pluginPrettier },
    rules: {
      'prettier/prettier': 'warn', // or "error"
    },
  },
  {
    files: ['**/*.{js,mjs,cjs,ts,mts,cts,vue}'],
    languageOptions: {
      globals: globals.browser,
    },
  },
  tseslint.configs.recommended,
  pluginVue.configs['flat/essential'],
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },
  {
    files: ['**/*.json'],
    plugins: { json },
    language: 'json/json',
    extends: ['json/recommended'],
  },
  {
    files: ['**/*.css', '**/*.scss'],
    plugins: { css },
    language: 'css/css',
    extends: ['css/recommended'],
  },
  prettier, // 放在最后，禁用 ESLint 的格式化相关规则
])
