<template>
  <el-color-picker
    v-model="theme"
    :predefine="[
      '#409EFF',
      '#1890ff',
      '#304156',
      '#212121',
      '#11a983',
      '#13c2c2',
      '#6959CD',
      '#f5222d',
    ]"
    class="theme-picker"
    popper-class="theme-picker-dropdown"
  />
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const ORIGINAL_THEME = '#409EFF' // default color
const theme = ref(appStore.state.theme || ORIGINAL_THEME)

// 监听主题变化
watch(
  theme,
  async (val) => {
    if (typeof val !== 'string') return
    const oldVal = theme.value
    await updateTheme(val, oldVal)
    appStore.setTheme(val as 'light' | 'dark' | 'auto')
  }
)

// 更新主题
const updateTheme = async (val: string, oldVal: string) => {
  if (typeof val !== 'string') return
  const head = document.getElementsByTagName('head')[0]
  const themeCluster = getThemeCluster(val.replace('#', ''))
  const originalCluster = getThemeCluster(oldVal.replace('#', ''))
  
  const getHandler = (variable: string, id: string) => {
    return () => {
      const originalCluster = getThemeCluster(ORIGINAL_THEME.replace('#', ''))
      const newStyle = updateStyle(getStyleTemplate(variable), originalCluster, themeCluster)
      
      let styleTag = document.getElementById(id)
      if (!styleTag) {
        styleTag = document.createElement('style')
        styleTag.setAttribute('id', id)
        head.appendChild(styleTag)
      }
      styleTag.innerText = newStyle
    }
  }
  
  const chalkHandler = getHandler('chalk', 'chalk-style')
  
  if (!window.chalk) {
    const url = `https://unpkg.com/element-plus/dist/index.css`
    await getCSSString(url, chalkHandler, 'chalk')
  } else {
    chalkHandler()
  }
  
  const styles: HTMLElement[] = [].slice.call(document.querySelectorAll('style'))
    .filter((style: HTMLElement) => {
      const text = style.innerText
      return new RegExp(oldVal, 'i').test(text) && !/Chalk Variables/.test(text)
    })
  
  styles.forEach(style => {
    const { innerText } = style
    if (typeof innerText !== 'string') return
    style.innerText = updateStyle(innerText, originalCluster, themeCluster)
  })
  
  await nextTick()
}

// 更新样式
const updateStyle = (style: string, oldCluster: string[], newCluster: string[]) => {
  let newStyle = style
  oldCluster.forEach((color, index) => {
    newStyle = newStyle.replace(new RegExp(color, 'ig'), newCluster[index])
  })
  return newStyle
}

// 获取CSS字符串
const getCSSString = (url: string, callback: Function, variable: string) => {
  return new Promise(resolve => {
    const xhr = new XMLHttpRequest()
    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4 && xhr.status === 200) {
        ;(window as any)[variable] = xhr.responseText.replace(/@font-face{[^}]+}/g, '')
        callback()
        resolve(null)
      }
    }
    xhr.open('GET', url)
    xhr.send()
  })
}

// 获取主题色彩集群
const getThemeCluster = (theme: string) => {
  const tintColor = (color: string, tint: number) => {
    let red = parseInt(color.slice(0, 2), 16)
    let green = parseInt(color.slice(2, 4), 16)
    let blue = parseInt(color.slice(4, 6), 16)
    
    if (tint === 0) {
      return [red, green, blue].join(',')
    } else {
      red += Math.round(tint * (255 - red))
      green += Math.round(tint * (255 - green))
      blue += Math.round(tint * (255 - blue))
      
      red = red > 255 ? 255 : red
      green = green > 255 ? 255 : green
      blue = blue > 255 ? 255 : blue
      
      return `#${red.toString(16).padStart(2, '0')}${green.toString(16).padStart(2, '0')}${blue.toString(16).padStart(2, '0')}`
    }
  }
  
  const shadeColor = (color: string, shade: number) => {
    let red = parseInt(color.slice(0, 2), 16)
    let green = parseInt(color.slice(2, 4), 16)
    let blue = parseInt(color.slice(4, 6), 16)
    
    red = Math.round((1 - shade) * red)
    green = Math.round((1 - shade) * green)
    blue = Math.round((1 - shade) * blue)
    
    return `#${red.toString(16).padStart(2, '0')}${green.toString(16).padStart(2, '0')}${blue.toString(16).padStart(2, '0')}`
  }
  
  const clusters = [theme]
  for (let i = 0; i <= 9; i++) {
    clusters.push(tintColor(theme, Number((i / 10).toFixed(2))))
  }
  clusters.push(shadeColor(theme, 0.1))
  return clusters
}

// 获取样式模板
const getStyleTemplate = (data: string) => {
  return data
}

// 声明全局变量
declare global {
  interface Window {
    chalk: string
  }
}
</script>

<style>
.theme-picker .el-color-picker__trigger {
  vertical-align: middle;
}

.theme-picker-dropdown .el-color-dropdown__link-btn {
  display: none;
}
</style>