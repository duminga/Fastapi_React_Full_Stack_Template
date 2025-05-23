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

export async function logout(): Promise<void> {
    return request.post('/auth/logout')
}

export async function getUserInfo(): Promise<UserInfo> {
    const response = await request.get<UserInfo>('/users/me')
    return response as unknown as UserInfo
} 