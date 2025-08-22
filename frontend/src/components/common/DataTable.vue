<template>
  <div class="data-table">
    <!-- 表格工具栏 -->
    <div v-if="showToolbar" class="table-toolbar">
      <!-- 左侧操作 -->
      <div class="toolbar-left">
        <!-- 批量操作 -->
        <div v-if="selection.length > 0" class="batch-actions">
          <span class="selection-info">
            已选择 {{ selection.length }} 项
          </span>
          <slot name="batch-actions" :selection="selection" />
        </div>
        
        <!-- 普通操作 -->
        <div v-else class="normal-actions">
          <slot name="toolbar-left" />
        </div>
      </div>
      
      <!-- 右侧操作 -->
      <div class="toolbar-right">
        <!-- 搜索框 -->
        <el-input
          v-if="searchable"
          v-model="searchKeyword"
          :placeholder="searchPlaceholder"
          :prefix-icon="Search"
          clearable
          class="search-input"
          @input="handleSearch"
        />
        
        <!-- 刷新按钮 -->
        <el-button
          v-if="refreshable"
          :icon="Refresh"
          :loading="loading"
          @click="handleRefresh"
        >
          刷新
        </el-button>
        
        <!-- 列设置 -->
        <el-dropdown v-if="columnSettable" trigger="click">
          <el-button :icon="Setting">
            列设置
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="col in columns"
                :key="col.prop"
                @click="toggleColumn(col)"
              >
                <el-checkbox
                  :model-value="!col.hidden"
                  @change="toggleColumn(col)"
                >
                  {{ col.label }}
                </el-checkbox>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- 自定义工具栏 -->
        <slot name="toolbar-right" />
      </div>
    </div>
    
    <!-- 表格主体 -->
    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="tableData"
      :height="height"
      :max-height="maxHeight"
      :stripe="stripe"
      :border="border"
      :size="size"
      :row-key="rowKey"
      :default-sort="defaultSort"
      :show-summary="showSummary"
      :summary-method="summaryMethod"
      :span-method="spanMethod"
      :row-class-name="rowClassName"
      :cell-class-name="cellClassName"
      :header-row-class-name="headerRowClassName"
      :header-cell-class-name="headerCellClassName"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @row-click="handleRowClick"
      @row-dblclick="handleRowDblClick"
      @cell-click="handleCellClick"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="selectable"
        type="selection"
        width="55"
        :selectable="selectableFunction"
        fixed="left"
      />
      
      <!-- 序号列 -->
      <el-table-column
        v-if="showIndex"
        type="index"
        label="序号"
        width="60"
        :index="indexMethod"
        fixed="left"
      />
      
      <!-- 数据列 -->
      <template v-for="column in visibleColumns" :key="column.prop">
        <!-- 普通列 -->
        <el-table-column
          v-if="!column.children"
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
          :min-width="column.minWidth"
          :fixed="column.fixed"
          :sortable="column.sortable"
          :sort-method="column.sortMethod"
          :sort-by="column.sortBy"
          :sort-orders="column.sortOrders"
          :resizable="column.resizable"
          :show-overflow-tooltip="column.showOverflowTooltip"
          :align="column.align"
          :header-align="column.headerAlign"
          :class-name="column.className"
          :label-class-name="column.labelClassName"
          :formatter="column.formatter"
        >
          <!-- 自定义表头 -->
          <template v-if="column.headerSlot" #header="scope">
            <slot :name="column.headerSlot" v-bind="scope" />
          </template>
          
          <!-- 自定义内容 -->
          <template v-if="column.slot" #default="scope">
            <slot :name="column.slot" v-bind="scope" />
          </template>
        </el-table-column>
        
        <!-- 多级表头 -->
        <el-table-column
          v-else
          :label="column.label"
          :align="column.align"
          :header-align="column.headerAlign"
        >
          <el-table-column
            v-for="child in column.children"
            :key="child.prop"
            :prop="child.prop"
            :label="child.label"
            :width="child.width"
            :min-width="child.minWidth"
            :sortable="child.sortable"
            :formatter="child.formatter"
            :align="child.align"
            :header-align="child.headerAlign"
          >
            <template v-if="child.slot" #default="scope">
              <slot :name="child.slot" v-bind="scope" />
            </template>
          </el-table-column>
        </el-table-column>
      </template>
      
      <!-- 操作列 -->
      <el-table-column
        v-if="$slots.actions"
        label="操作"
        :width="actionWidth"
        :min-width="actionMinWidth"
        :fixed="actionFixed"
        align="center"
        class-name="table-actions"
      >
        <template #default="scope">
          <slot name="actions" v-bind="scope" />
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页器 -->
    <div v-if="pagination && total > 0" class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="internalPageSize"
        :total="total"
        :page-sizes="pageSizes"
        :layout="paginationLayout"
        :background="paginationBackground"
        :small="paginationSmall"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { Search, Refresh, Setting } from '@element-plus/icons-vue'
import type { ElTable } from 'element-plus'
import { debounce } from 'lodash-es'

// 表格列配置接口
interface TableColumn {
  prop: string
  label: string
  width?: string | number
  minWidth?: string | number
  fixed?: boolean | 'left' | 'right'
  sortable?: boolean | 'custom'
  sortMethod?: Function
  sortBy?: string | string[] | Function
  sortOrders?: string[]
  resizable?: boolean
  showOverflowTooltip?: boolean
  align?: 'left' | 'center' | 'right'
  headerAlign?: 'left' | 'center' | 'right'
  className?: string
  labelClassName?: string
  formatter?: Function
  slot?: string
  headerSlot?: string
  hidden?: boolean
  children?: TableColumn[]
}

// 组件属性
interface Props {
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  height?: string | number
  maxHeight?: string | number
  stripe?: boolean
  border?: boolean
  size?: 'large' | 'default' | 'small'
  rowKey?: string | Function
  defaultSort?: { prop: string; order: 'ascending' | 'descending' }
  showSummary?: boolean
  summaryMethod?: Function
  spanMethod?: Function
  rowClassName?: string | Function
  cellClassName?: string | Function
  headerRowClassName?: string | Function
  headerCellClassName?: string | Function
  selectable?: boolean
  selectableFunction?: Function
  showIndex?: boolean
  indexMethod?: Function
  showToolbar?: boolean
  searchable?: boolean
  searchPlaceholder?: string
  refreshable?: boolean
  columnSettable?: boolean
  actionWidth?: string | number
  actionMinWidth?: string | number
  actionFixed?: boolean | 'left' | 'right'
  pagination?: boolean
  total?: number
  pageSize?: number
  pageSizes?: number[]
  paginationLayout?: string
  paginationBackground?: boolean
  paginationSmall?: boolean
}

// 定义属性默认值
const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  columns: () => [],
  loading: false,
  stripe: true,
  border: true,
  size: 'default',
  selectable: false,
  showIndex: false,
  showToolbar: true,
  searchable: true,
  searchPlaceholder: '请输入关键词搜索',
  refreshable: true,
  columnSettable: true,
  actionWidth: 150,
  actionMinWidth: 100,
  actionFixed: 'right',
  pagination: true,
  total: 0,
  pageSize: 10,
  pageSizes: () => [10, 20, 50, 100],
  paginationLayout: 'total, sizes, prev, pager, next, jumper',
  paginationBackground: true,
  paginationSmall: false
})

// 定义事件
const emit = defineEmits<{
  search: [keyword: string]
  refresh: []
  selectionChange: [selection: any[]]
  sortChange: [{ column: any; prop: string; order: string }]
  rowClick: [row: any, column: any, event: Event]
  rowDblClick: [row: any, column: any, event: Event]
  cellClick: [row: any, column: any, cell: any, event: Event]
  sizeChange: [size: number]
  currentChange: [page: number]
}>()

// 响应式数据
const tableRef = ref<InstanceType<typeof ElTable>>()
const selection = ref<any[]>([])
const searchKeyword = ref('')
const currentPage = ref(1)
const internalPageSize = ref(props.pageSize)
const internalColumns = ref([...props.columns])

// 计算属性
const tableData = computed(() => props.data)
const visibleColumns = computed(() => internalColumns.value.filter(col => !col.hidden))

// 防抖搜索
const handleSearch = debounce((keyword: string) => {
  emit('search', keyword)
}, 300)

// 刷新数据
const handleRefresh = () => {
  emit('refresh')
}

// 切换列显示/隐藏
const toggleColumn = (column: TableColumn) => {
  column.hidden = !column.hidden
}

// 选择变化
const handleSelectionChange = (val: any[]) => {
  selection.value = val
  emit('selectionChange', val)
}

// 排序变化
const handleSortChange = (sortInfo: { column: any; prop: string; order: string }) => {
  emit('sortChange', sortInfo)
}

// 行点击
const handleRowClick = (row: any, column: any, event: Event) => {
  emit('rowClick', row, column, event)
}

// 行双击
const handleRowDblClick = (row: any, column: any, event: Event) => {
  emit('rowDblClick', row, column, event)
}

// 单元格点击
const handleCellClick = (row: any, column: any, cell: any, event: Event) => {
  emit('cellClick', row, column, cell, event)
}

// 页面大小变化
const handleSizeChange = (size: number) => {
  internalPageSize.value = size
  emit('sizeChange', size)
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  emit('currentChange', page)
}

// 清空选择
const clearSelection = () => {
  tableRef.value?.clearSelection()
}

// 切换所有选择
const toggleAllSelection = () => {
  tableRef.value?.toggleAllSelection()
}

// 切换行选择
const toggleRowSelection = (row: any, selected?: boolean) => {
  tableRef.value?.toggleRowSelection(row, selected)
}

// 设置当前行
const setCurrentRow = (row: any) => {
  tableRef.value?.setCurrentRow(row)
}

// 刷新表格布局
const doLayout = () => {
  nextTick(() => {
    tableRef.value?.doLayout()
  })
}

// 监听列变化
watch(
  () => props.columns,
  (newColumns) => {
    internalColumns.value = [...newColumns]
  },
  { deep: true }
)

// 暴露方法
defineExpose({
  clearSelection,
  toggleAllSelection,
  toggleRowSelection,
  setCurrentRow,
  doLayout,
  tableRef
})

// 导出类型
export type { TableColumn }
</script>

<style lang="scss" scoped>
.data-table {
  .table-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding: 16px;
    background-color: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    
    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .batch-actions {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .selection-info {
          color: var(--el-color-primary);
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
    
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .search-input {
        width: 240px;
      }
    }
  }
  
  :deep(.el-table) {
    .table-actions {
      .el-button {
        margin: 0 2px;
      }
    }
  }
  
  .table-pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
    padding: 16px 0;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .data-table {
    .table-toolbar {
      flex-direction: column;
      gap: 12px;
      align-items: stretch;
      
      .toolbar-left,
      .toolbar-right {
        justify-content: center;
      }
      
      .search-input {
        width: 100% !important;
      }
    }
    
    .table-pagination {
      justify-content: center;
      
      :deep(.el-pagination) {
        flex-wrap: wrap;
        justify-content: center;
      }
    }
  }
}
</style>