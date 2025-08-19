import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import relativeTime from 'dayjs/plugin/relativeTime'
import duration from 'dayjs/plugin/duration'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

// 配置dayjs插件
dayjs.extend(relativeTime)
dayjs.extend(duration)
dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.locale('zh-cn')

/**
 * 格式化日期
 * @param date 日期字符串或Date对象
 * @param format 格式化模板，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的日期字符串
 */
export const formatDate = (date: string | Date | number | undefined, format = 'YYYY-MM-DD HH:mm:ss'): string => {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 格式化相对时间
 * @param date 日期字符串或Date对象
 * @returns 相对时间字符串，如：2小时前
 */
export const formatRelativeTime = (date: string | Date | number | undefined): string => {
  if (!date) return ''
  return dayjs(date).fromNow()
}

/**
 * 格式化持续时间
 * @param milliseconds 毫秒数
 * @returns 格式化后的持续时间字符串
 */
export const formatDuration = (milliseconds: number): string => {
  if (!milliseconds || milliseconds < 0) return '0秒'
  
  const duration = dayjs.duration(milliseconds)
  const hours = Math.floor(duration.asHours())
  const minutes = duration.minutes()
  const seconds = duration.seconds()
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟${seconds}秒`
  } else if (minutes > 0) {
    return `${minutes}分钟${seconds}秒`
  } else {
    return `${seconds}秒`
  }
}

/**
 * 获取日期范围
 * @param type 范围类型：today, yesterday, week, month, year
 * @returns [开始时间, 结束时间]
 */
export const getDateRange = (type: 'today' | 'yesterday' | 'week' | 'month' | 'year'): [string, string] => {
  const now = dayjs()
  
  switch (type) {
    case 'today':
      return [
        now.startOf('day').format('YYYY-MM-DD HH:mm:ss'),
        now.endOf('day').format('YYYY-MM-DD HH:mm:ss')
      ]
    case 'yesterday':
      const yesterday = now.subtract(1, 'day')
      return [
        yesterday.startOf('day').format('YYYY-MM-DD HH:mm:ss'),
        yesterday.endOf('day').format('YYYY-MM-DD HH:mm:ss')
      ]
    case 'week':
      return [
        now.startOf('week').format('YYYY-MM-DD HH:mm:ss'),
        now.endOf('week').format('YYYY-MM-DD HH:mm:ss')
      ]
    case 'month':
      return [
        now.startOf('month').format('YYYY-MM-DD HH:mm:ss'),
        now.endOf('month').format('YYYY-MM-DD HH:mm:ss')
      ]
    case 'year':
      return [
        now.startOf('year').format('YYYY-MM-DD HH:mm:ss'),
        now.endOf('year').format('YYYY-MM-DD HH:mm:ss')
      ]
    default:
      return [
        now.startOf('day').format('YYYY-MM-DD HH:mm:ss'),
        now.endOf('day').format('YYYY-MM-DD HH:mm:ss')
      ]
  }
}

/**
 * 判断是否为有效日期
 * @param date 日期字符串或Date对象
 * @returns 是否为有效日期
 */
export const isValidDate = (date: string | Date | number): boolean => {
  return dayjs(date).isValid()
}

/**
 * 获取时区
 * @returns 当前时区
 */
export const getTimezone = (): string => {
  return dayjs.tz.guess()
}

/**
 * 转换时区
 * @param date 日期
 * @param timezone 目标时区
 * @returns 转换后的日期
 */
export const convertTimezone = (date: string | Date | number, timezone: string): string => {
  return dayjs(date).tz(timezone).format('YYYY-MM-DD HH:mm:ss')
}

export default {
  formatDate,
  formatRelativeTime,
  formatDuration,
  getDateRange,
  isValidDate,
  getTimezone,
  convertTimezone
}