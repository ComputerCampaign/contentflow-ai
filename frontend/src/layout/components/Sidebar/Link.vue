<template>
  <component :is="linkProps.is" v-bind="linkProps.props">
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { isExternal } from '@/utils/validate'

interface Props {
  to: string
}

const props = defineProps<Props>()

// 计算链接属性
const linkProps = computed(() => {
  if (isExternal(props.to)) {
    return {
      is: 'a',
      props: {
        href: props.to,
        target: '_blank',
        rel: 'noopener'
      }
    }
  }
  return {
    is: 'router-link',
    props: {
      to: props.to
    }
  }
})
</script>