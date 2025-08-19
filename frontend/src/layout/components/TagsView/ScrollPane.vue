<template>
  <div
    ref="scrollContainer"
    class="scroll-container"
    @wheel.prevent="handleScroll"
  >
    <div
      ref="scrollWrapper"
      class="scroll-wrapper"
      :style="{
        transform: `translateX(${left}px)`
      }"
    >
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['scroll'])

const scrollContainer = ref<HTMLElement>()
const scrollWrapper = ref<HTMLElement>()
const left = ref(0)

const handleScroll = (e: WheelEvent) => {
  const eventDelta = (e as any).wheelDelta || -e.deltaY * 40
  const $scrollWrapper = scrollWrapper.value!
  const $scrollContainer = scrollContainer.value!
  
  const wrapperWidth = $scrollWrapper.offsetWidth
  const containerWidth = $scrollContainer.offsetWidth
  
  if (eventDelta > 0) {
    left.value = Math.min(0, left.value + eventDelta)
  } else {
    if (containerWidth - wrapperWidth < left.value) {
      left.value = left.value
    } else {
      left.value = Math.max(containerWidth - wrapperWidth, left.value + eventDelta)
    }
  }
  emit('scroll')
}

const moveToTarget = (currentTag: HTMLElement) => {
  const $scrollContainer = scrollContainer.value!
  const $scrollWrapper = scrollWrapper.value!
  
  const containerWidth = $scrollContainer.offsetWidth
  const wrapperWidth = $scrollWrapper.offsetWidth
  
  const tagOffsetLeft = currentTag.offsetLeft
  const tagWidth = currentTag.offsetWidth
  
  if (containerWidth < wrapperWidth) {
    if (tagOffsetLeft < -left.value) {
      // tag in the left
      left.value = -tagOffsetLeft + 20
    } else if (tagOffsetLeft + tagWidth > -left.value + containerWidth) {
      // tag in the right
      left.value = -(tagOffsetLeft - (containerWidth - tagWidth) + 20)
    }
  }
}

defineExpose({
  moveToTarget
})
</script>

<style lang="scss" scoped>
.scroll-container {
  white-space: nowrap;
  position: relative;
  overflow: hidden;
  width: 100%;
  
  .scroll-wrapper {
    position: absolute;
    transition: transform 0.3s ease-in-out;
  }
}
</style>