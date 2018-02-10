# Api Design


## Resource URL

[参考Github的API蓝图](https://api.github.com/)
curl http://tecstack.org/demo/api/v1.0

{
  "user_list_url": {
    "rel":   "collection  http://tecstack.org/demo/api/v1.0/users",
    "href":  " http://tecstack.org/demo/api/v1.0/users",
    "title": "List of users",
    "type":  "application/vnd.ext.mediatype+json"
  },
  'link':{
    ......
  },
  ......
}

### user model for demo

| HTTP 方法   |  行为          |         示例 |
| ---------- |-------------- |---------------|
| GET      |   获取资源的信息 |    http://tecstack.org/demo/api/v1.0/users |
| GET      |   获取某个特定资源的信息 | http://tecstack.org/demo/api/v1.0/users/123 |
| POST     |   创建新资源           |  http://tecstack.org/demo/api/v1.0/users |
| PUT      |   更新资源             |  http://tecstack.org/demo/api/v1.0/users/123 |
| DELETE   |   删除资源             |  http://tecstack.org/demo/api/v1.0/users/123 |
| GET      |   获取特定用户的todo_list信息 |    http://tecstack.org/demo/api/v1.0/users/123/todos |
| GET      |   获取特定用户的特定todo信息 |    http://tecstack.org/demo/api/v1.0/users/123/todos/100 |

GET List Output:
{
  'users':[
    {
      'id':'0'
      'username':'username',
      'email':'email',
      'url':'resource.url.address'
    },
    {
      ......
    },
  ]
}

GET Entity Output:
{
  'user':{
    'id':'1',
    'username':'username',
    'email':'email',
    'url':'url for entity'
  }
}

POST Input Args:
{
  'username':'testuser',
  'email':'email@email.com'
}

POST Oputput:
{
  'user':{
    'id':'1',
    'username':'username',
    'email':'email',
    'url':'url for entity'
  }
}

PUT Input Args:
{
  'user_id':'1',
  'username':'New username',
  'email':'New Email'
}

PUT Output:
{
  'user':{
    'id':'1',
    'username':'username',
    'email':'email',
    'url':'url for entity'
  }
}

DELETE Input Args:
{
  'user_id':'1'
}

DELETE Output:{}

过滤参数：

* ?limit=10：指定返回记录的数量
* ?offset=10：指定返回记录的开始位置。
* ?page=2&per_page=100：指定第几页，以及每页的记录数。
* ?sortby=name&order=asc：指定返回结果按照哪个属性排序，以及排序顺序。
* ?animal_type_id=1：指定筛选条件

HTTP状态码：[官方参考](http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)

* 200 OK - [GET]：服务器成功返回用户请求的数据，该操作是幂等的（Idempotent）。
* 201 CREATED - [POST/PUT/PATCH]：用户新建或修改数据成功。
* 202 Accepted - ：表示一个请求已经进入后台排队（异步任务）
* 204 NO CONTENT - [DELETE]：用户删除数据成功。
* 400 INVALID REQUEST - [POST/PUT/PATCH]：用户发出的请求有错误，服务器没有进行新建或修改数据的操作，该操作是幂等的。
* 401 Unauthorized - ：表示用户没有权限（令牌、用户名、密码错误）。
* 403 Forbidden -  表示用户得到授权（与401错误相对），但是访问是被禁止的。
* 404 NOT FOUND - ：用户发出的请求针对的是不存在的记录，服务器没有进行操作，该操作是幂等的。
* 406 Not Acceptable - [GET]：用户请求的格式不可得（比如用户请求JSON格式，但是只有XML格式）。
* 410 Gone -[GET]：用户请求的资源被永久删除，且不会再得到的。
* 422 Unprocesable entity - [POST/PUT/PATCH] 当创建一个对象时，发生一个验证错误。
* 500 INTERNAL SERVER ERROR - ：服务器发生错误，用户将无法判断发出的请求是否成功。

错误处理，如4XX，500等，提供更详细的应用错误描述：
{
    error: "Invalid API key"
}

### todo model for demo

| HTTP 方法   |  行为          |         示例 |
| ---------- |-------------- |---------------|
| GET      |   获取资源的信息 |    http://tecstack.org/demo/api/v1.0/todos |
| GET      |   获取某个特定资源的信息 | http://tecstack.org/demo/api/v1.0/todos/123 |
| POST     |   创建新资源           |  http://tecstack.org/demo/api/v1.0/todos |
| PUT      |   更新资源             |  http://tecstack.org/demo/api/v1.0/todos/123 |
| DELETE   |   删除资源             |  http://tecstack.org/demo/api/v1.0/todos/123 |

### Biz Model

This is for orders, products, payment... mgmt.

| HTTP 方法   |  行为          |         示例 |
| ---------- |-------------- |---------------|
| GET      |   获取资源的信息 |    http://tecstack.org/biz/api/v1.0/orders |
| GET      |   获取某个特定资源的信息 | http://tecstack.org/biz/api/v1.0/orders/123 |
| POST     |   创建新资源           |  http://tecstack.org/biz/api/v1.0/orders |
| PUT      |   更新资源             |  http://tecstack.org/biz/api/v1.0/orders/123 |
| DELETE   |   删除资源             |  http://tecstack.org/biz/api/v1.0/orders/123 |

### Crm Model

This is for customer, company, ... mgmt.

| HTTP 方法   |  行为          |         示例 |
| ---------- |-------------- |---------------|
| GET      |   获取资源的信息 |    http://tecstack.org/crm/api/v1.0/customers |
| GET      |   获取某个特定资源的信息 | http://tecstack.org/crm/api/v1.0/customers/123 |
| POST     |   创建新资源           |  http://tecstack.org/crm/api/v1.0/customers |
| PUT      |   更新资源             |  http://tecstack.org/crm/api/v1.0/customers/123 |
| DELETE   |   删除资源             |  http://tecstack.org/crm/api/v1.0/customers/123 |

### ... other Models

TBD.


## Authentication

TBD.
