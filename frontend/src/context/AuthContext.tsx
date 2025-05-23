import React, { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { message } from 'antd'
import { login as loginApi, logout as logoutApi, getUserInfo, refreshToken } from '@/services/auth'
import type { LoginParams, UserInfo, LoginResult } from '@/services/auth'

interface AuthContextType {
    user: UserInfo | null
    loading: boolean
    login: (params: LoginParams) => Promise<void>
    logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

/**
 * 使用认证上下文
 * @return: AuthContextType 认证上下文对象
 * @exception: Error 在AuthProvider外部使用时抛出错误
 */
export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<UserInfo | null>(null)
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    /**
     * 检查并刷新令牌
     * @return: Promise<void>
     * @exception: Error 刷新令牌失败时抛出错误
     */
    const checkAndRefreshToken = async () => {
        const refreshTokenStr = localStorage.getItem('refresh_token')
        const accessTokenStr = localStorage.getItem('access_token')

        // 如果没有 refresh_token，清除所有令牌并返回
        if (!refreshTokenStr) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            setUser(null)
            setLoading(false)
            if (window.location.pathname !== '/login') {
                navigate('/login')
            }
            return
        }

        try {
            const result = await refreshToken(refreshTokenStr)
            if (result.access_token && result.refresh_token) {
                // 验证新令牌是否与旧令牌不同
                if (result.refresh_token === refreshTokenStr) {
                    throw new Error('刷新令牌无效')
                }

                localStorage.setItem('access_token', result.access_token)
                localStorage.setItem('refresh_token', result.refresh_token)

                // 获取用户信息
                const userInfo = await getUserInfo()
                setUser(userInfo)

                // 如果当前在登录页，自动跳转到仪表盘
                if (window.location.pathname === '/login') {
                    navigate('/dashboard')
                }
            } else {
                throw new Error('刷新令牌失败')
            }
        } catch (error) {
            console.error('Token refresh failed:', error)
            // 刷新失败，清除令牌
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            setUser(null)
            // 如果不在登录页，跳转到登录页
            if (window.location.pathname !== '/login') {
                navigate('/login')
            }
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        checkAndRefreshToken()
    }, [])

    /**
     * 用户登录
     * @param: params 登录参数
     * @return: Promise<void>
     * @exception: Error 登录失败时抛出错误
     */
    const login = async (params: LoginParams) => {
        try {
            const result = await loginApi(params)
            localStorage.setItem('access_token', result.access_token)
            if (result.refresh_token) {
                localStorage.setItem('refresh_token', result.refresh_token)
            }

            const userInfo = await getUserInfo()
            setUser(userInfo)
            message.success('登录成功')
            navigate('/dashboard')
        } catch (error) {
            message.error('登录失败')
            throw error
        }
    }

    /**
     * 用户登出
     * @return: Promise<void>
     * @exception: Error 登出失败时抛出错误
     */
    const logout = async () => {
        try {
            await logoutApi()
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            setUser(null)
            message.success('登出成功')
            navigate('/login')
        } catch (error) {
            message.error('登出失败')
            throw error
        }
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
} 