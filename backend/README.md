## 数据库初始化
- 初始化数据库脚本`python -m app.db_migrations.db_manage`
- 数据库ER图：
+---------+         +--------------+         +--------------+
|  users  |         |   users_roles|         |    roles     |
+---------+         +--------------+         +--------------+
| id      |<------->| user_id      |         | id           |
| email   |         | role_id      |<------->| name         |
| ...     |         +--------------+         | code         |
+---------+                                  | ...          |
                                             +--------------+
                                                    |
                                                    |
                                                    v
                                             +------------------+
                                             | roles_permissions|
                                             +------------------+
                                             | role_id          |
                                             | permission_id    |<------+
                                             +------------------+       |
                                                                        |
                                                                  +--------------+
                                                                  | permissions  |
                                                                  +--------------+
                                                                  | id           |
                                                                  | name         |
                                                                  | code         |
                                                                  | ...          |
                                                                  +--------------+
### 表结构说明
1. users 与 roles
      通过 users_roles 实现多对多关系：
            一个用户可以有多个角色
            一个角色可以分配给多个用户
2. roles 与 permissions
      通过 roles_permissions 实现多对多关系：
            一个角色可以拥有多个权限
            一个权限可以分配给多个角色