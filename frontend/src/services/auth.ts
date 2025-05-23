import request from '@/utils/request'

export interface LoginParams {
    username: string
    password: string
    remember?: boolean
}

export interface LoginResult {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
}

export interface UserInfo {
    id: number
    username: string
    email: string
    is_active: boolean
    is_superuser: boolean
}

/**
 * 用户登录
 * @param: params 登录参数，包含用户名、密码和是否记住登录
 * @return: Promise<LoginResult> 登录结果，包含访问令牌和刷新令牌
 * @exception: Error 登录失败时抛出错误
 */
export async function login(params: LoginParams): Promise<LoginResult> {
    const formData = new URLSearchParams();
    formData.append('username', params.username);
    formData.append('password', params.password);
    if (params.remember) {
        formData.append('scope', 'remember');
    }

    const response = await request.post<LoginResult>('/auth/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
    return response as unknown as LoginResult;
}

/**
 * 刷新访问令牌
 * @param: refreshToken 刷新令牌
 * @return: Promise<LoginResult> 新的访问令牌和刷新令牌
 * @exception: Error 刷新令牌失败时抛出错误
 */
export async function refreshToken(refreshToken: string): Promise<LoginResult> {
    const response = await request.post<LoginResult>('/auth/refresh', {
        refresh_token: refreshToken
    }, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return response as unknown as LoginResult;
}

/**
 * 用户登出
 * @return: Promise<void> 登出结果
 * @exception: Error 登出失败时抛出错误
 */
export async function logout(): Promise<void> {
    return request.post('/auth/logout')
}

/**
 * 获取当前用户信息
 * @return: Promise<UserInfo> 用户信息
 * @exception: Error 获取用户信息失败时抛出错误
 */
export async function getUserInfo(): Promise<UserInfo> {
    const response = await request.get<UserInfo>('/users/me')
    return response as unknown as UserInfo
} 