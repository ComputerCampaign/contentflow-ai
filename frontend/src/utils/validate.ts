/**
 * 验证是否为外部链接
 * @param path 路径
 * @returns 是否为外部链接
 */
export function isExternal(path: string): boolean {
  return /^(https?:|mailto:|tel:)/.test(path)
}

/**
 * 验证是否为有效的URL
 * @param url URL字符串
 * @returns 是否为有效URL
 */
export function isValidURL(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 是否为有效邮箱
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证手机号格式（中国大陆）
 * @param phone 手机号
 * @returns 是否为有效手机号
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 密码强度等级 0-4
 */
export function getPasswordStrength(password: string): number {
  let strength = 0
  
  // 长度检查
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++
  
  // 包含小写字母
  if (/[a-z]/.test(password)) strength++
  
  // 包含大写字母
  if (/[A-Z]/.test(password)) strength++
  
  // 包含数字
  if (/\d/.test(password)) strength++
  
  // 包含特殊字符
  if (/[^\w\s]/.test(password)) strength++
  
  return Math.min(strength, 4)
}

/**
 * 验证是否为有效的IP地址
 * @param ip IP地址
 * @returns 是否为有效IP
 */
export function isValidIP(ip: string): boolean {
  const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return ipRegex.test(ip)
}

/**
 * 验证是否为有效的端口号
 * @param port 端口号
 * @returns 是否为有效端口
 */
export function isValidPort(port: string | number): boolean {
  const portNum = typeof port === 'string' ? parseInt(port, 10) : port
  return !isNaN(portNum) && portNum >= 1 && portNum <= 65535
}

/**
 * 验证是否为有效的域名
 * @param domain 域名
 * @returns 是否为有效域名
 */
export function isValidDomain(domain: string): boolean {
  const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/
  return domainRegex.test(domain)
}

/**
 * 验证是否为有效的JSON字符串
 * @param str JSON字符串
 * @returns 是否为有效JSON
 */
export function isValidJSON(str: string): boolean {
  try {
    JSON.parse(str)
    return true
  } catch {
    return false
  }
}

/**
 * 验证是否为有效的正则表达式
 * @param pattern 正则表达式字符串
 * @returns 是否为有效正则
 */
export function isValidRegex(pattern: string): boolean {
  try {
    new RegExp(pattern)
    return true
  } catch {
    return false
  }
}

/**
 * 验证是否为有效的XPath表达式
 * @param xpath XPath表达式
 * @returns 是否为有效XPath
 */
export function isValidXPath(xpath: string): boolean {
  try {
    // 简单的XPath语法检查
    if (!xpath || typeof xpath !== 'string') return false
    
    // 检查基本的XPath语法
    const xpathRegex = /^(\/\/|\/)([a-zA-Z_][\w\-]*|\*)(\[[^\]]*\])?(\/@[a-zA-Z_][\w\-]*)?(\/([a-zA-Z_][\w\-]*|\*)(\[[^\]]*\])?)*$/
    return xpathRegex.test(xpath) || xpath === '.' || xpath === '..'
  } catch {
    return false
  }
}

/**
 * 验证是否为有效的CSS选择器
 * @param selector CSS选择器
 * @returns 是否为有效选择器
 */
export function isValidCSSSelector(selector: string): boolean {
  try {
    document.querySelector(selector)
    return true
  } catch {
    return false
  }
}

/**
 * 验证文件大小是否在限制范围内
 * @param file 文件对象
 * @param maxSize 最大大小（字节）
 * @returns 是否在限制范围内
 */
export function isValidFileSize(file: File, maxSize: number): boolean {
  return file.size <= maxSize
}

/**
 * 验证文件类型是否允许
 * @param file 文件对象
 * @param allowedTypes 允许的文件类型数组
 * @returns 是否为允许的类型
 */
export function isValidFileType(file: File, allowedTypes: string[]): boolean {
  return allowedTypes.includes(file.type)
}

/**
 * 验证是否为空值
 * @param value 值
 * @returns 是否为空
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 验证是否为有效的数字范围
 * @param value 数值
 * @param min 最小值
 * @param max 最大值
 * @returns 是否在范围内
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}