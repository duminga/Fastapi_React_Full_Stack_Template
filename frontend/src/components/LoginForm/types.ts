export interface LoginFormValues {
    username: string
    password: string
    remember?: boolean
}

export interface LoginFormProps {
    onFinish: (values: LoginFormValues) => void
    loading?: boolean
} 