
# User registration

## 用户状态转换：
1. 提交注册，待确认：1
1. 确认，未更新必要详细信息：2
1. 更新必要详细信息，激活态：3
1. 被屏蔽：4

## 激活码：

1. 当用户打开URL时自行删除
1. 随机生成64位UUID
1. 单独表存储

## Email:

1. 从JSON中获取username, email, password(text，生产中用https)
1. 验证email和password格式
1. 将password通过bcrypt做hash处理
1. 插入数据库，用户状态置为1，发送email确认邮件，确认URL包含激活码（随机）
1. 用户打开URL，更新用户状态到“已确认、未更新详细信息”，跳转到详细信息填写
1. 提交必要详细信息，更新数据，更新用户状态到3
1. 为用户创建session，重定向到首页
1. 恶意注册拦截

## Oauth

TBD.
