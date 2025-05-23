import React from 'react'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { Button, Form, Input, Card, Checkbox } from 'antd'
import { LoginFormProps, LoginFormValues } from './types'
import loginImage from '@/assets/login.jpg'
import './style.css'

const LoginForm: React.FC<LoginFormProps> = ({ onFinish, loading }) => {
    return (
        <div className="login-form-container">
            <Card className="login-form-card">
                <div className="login-content">
                    <div className="login-image">
                        <img src={loginImage} alt="login" />
                        {/* <div className="login-image-text">
                            欢迎使用管理系统
                        </div> */}
                    </div>
                    <div className="login-form-wrapper">
                        <div className="login-form-title-wrapper">
                            <h3 className="login-form-title">一个基于Fastapi+React+Ant Design的RDBC系统</h3>
                            <h1 className="login-form-title">系统登录</h1>
                        </div>
                        <Form
                            name="login"
                            className="login-form"
                            onFinish={onFinish}
                        >
                            <Form.Item
                                name="username"
                                rules={[{ required: true, message: '请输入用户名！' }]}
                            >
                                <Input
                                    prefix={<UserOutlined />}
                                    placeholder="用户名"
                                    size="large"
                                />
                            </Form.Item>
                            <Form.Item
                                name="password"
                                rules={[{ required: true, message: '请输入密码！' }]}
                            >
                                <Input.Password
                                    prefix={<LockOutlined />}
                                    placeholder="密码"
                                    size="large"
                                />
                            </Form.Item>

                            <Form.Item name="remember" valuePropName="checked">
                                <Checkbox>记住登录</Checkbox>
                            </Form.Item>

                            <Form.Item>
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    className="login-form-button"
                                    size="large"
                                    loading={loading}
                                >
                                    登录
                                </Button>
                            </Form.Item>
                        </Form>
                    </div>
                </div>
            </Card>
        </div>
    )
}

export default LoginForm 