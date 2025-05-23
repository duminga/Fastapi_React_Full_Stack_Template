import React from 'react'
import { useAuth } from '@/context/AuthContext'
import LoginForm from '@/components/LoginForm'
import type { LoginFormValues } from '@/components/LoginForm/types'

const Login: React.FC = () => {
    const { login } = useAuth()

    /**
     * 处理登录表单提交
     * @param: values 登录表单值
     * @return: Promise<void>
     * @exception: Error 登录失败时抛出错误
     */
    const handleLogin = async (values: LoginFormValues) => {
        try {
            await login({
                username: values.username,
                password: values.password,
                remember: values.remember
            })
        } catch (error) {
            console.error('登录失败:', error)
        }
    }

    return (
        <div className="login-page">
            <LoginForm onFinish={handleLogin} />
        </div>
    )
}

export default Login 