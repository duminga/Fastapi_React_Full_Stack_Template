import React from 'react'
import { useAuth } from '@/context/AuthContext'
import LoginForm from '@/components/LoginForm'
import type { LoginFormValues } from '@/components/LoginForm/types'

const Login: React.FC = () => {
    const { login } = useAuth()

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