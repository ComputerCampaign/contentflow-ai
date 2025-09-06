<template>
  <div class="comment-node" :class="{ 'is-child': level > 0 }">
    <div class="comment-content">
      <div class="comment-text">{{ comment.text }}</div>
      <div v-if="comment.children && comment.children.length > 0" class="comment-children">
        <div v-for="(child, index) in comment.children" :key="index" class="child-comment">
          <CommentNode :comment="child" :level="level + 1" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Comment {
  text: string
  children?: Comment[]
}

interface Props {
  comment: Comment
  level: number
}

defineProps<Props>()
</script>

<style scoped>
</style>
.comment-node {
  margin-bottom: 12px;
}

.comment-node.is-child {
  margin-left: 20px;
  padding-left: 16px;
  border-left: 2px solid #e4e7ed;
}

.comment-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
}

.comment-node.is-child .comment-content {
  background: #ffffff;
  border: 1px solid #dcdfe6;
}

.comment-text {
  color: #303133;
  line-height: 1.6;
  word-wrap: break-word;
  font-size: 14px;
}

.comment-children {
  margin-top: 12px;
}

.child-comment {
  position: relative;
}

.child-comment:before {
  content: '';
  position: absolute;
  left: -16px;
  top: 20px;
  width: 12px;
  height: 1px;
  background: #e4e7ed;
}

.child-comment:not(:last-child):after {
  content: '';
  position: absolute;
  left: -16px;
  top: 20px;
  bottom: -12px;
  width: 1px;
  background: #e4e7ed;
}