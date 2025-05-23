import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { message } from 'antd'
import { refreshToken } from '@/services/auth'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
    baseURL: '/api/v1',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
request.interceptors.request.use(
    (config) => {
        // 从 localStorage 获取 token
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    <T>(response: AxiosResponse<T>) => {
        return response.data as T
    },
    async (error) => {
        if (error.response) {
            const { status, data } = error.response
            switch (status) {
                case 401:
                    // 尝试使用 refresh_token 刷新
                    const refreshTokenStr = localStorage.getItem('refresh_token')
                    if (refreshTokenStr) {
                        try {
                            const result = await refreshToken(refreshTokenStr)
                            localStorage.setItem('access_token', result.access_token)
                            localStorage.setItem('refresh_token', result.refresh_token)
                            // 重试原请求
                            const config = error.config
                            config.headers.Authorization = `Bearer ${result.access_token}`
                            return request(config)
                        } catch (refreshError) {
                            // 刷新失败，清除令牌并跳转到登录页
                            localStorage.removeItem('access_token')
                            localStorage.removeItem('refresh_token')
                            // 使用 navigate 而不是直接修改 location
                            window.location.href = '/login'
                        }
                    } else {
                        localStorage.removeItem('access_token')
                        localStorage.removeItem('refresh_token')
                        window.location.href = '/login'
                    }
                    break
                case 403:
                    window.location.href = '/403'
                    break
                case 500:
                    message.error('服务器错误')
                    break
                default:
                    message.error(data.detail || '请求失败')
            }
        } else {
            message.error('网络错误')
        }
        return Promise.reject(error)
    }
)

export default request 