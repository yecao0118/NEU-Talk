#### 1. Login

**POST /api/login** 

###### request

Content-Type: application/json

```json
{
    "username" : "testuser",
    "password" : "testpassword"
}
```

###### response

fail

```json
{
    "HTTP Code": 401 Unauthorized,
    "msg": "invalid username or password"
}
```

success

```json
{
    "HTTP Code": 200,
    "data": {
        "userId": "12345678",
        "username": "testuser",
    }
}
```

#### 2.Register

**POST /api/register**

###### request

```json
{
    "username" : "testuser",
    "password" : "testpassword"
}
```

###### response

fail (user exists)

```json
{
    "HTTP Code": 409,
    "msg": "this username is already registered"
}
```


#### 3.Logout

**POST /api/logout**

###### request

```
no parameters
```



###### respond

fail

```json
{
    "HTTP Code": 500,
    "msg": "server error"
}
```

success

```json
{
    "HTTP Code": 200,
    "msg": "success"
}
```


#### 4. Create New Post

**POST /api/new** 

###### request

Content-Type: application/json

###### header
Authorization: Token <your-token>

```json
{
    "title": "Your title",
    "content": "Content of the new post"
}
```

###### response

fail

```json
{
    "HTTP Code": 400,
    "msg": "Content is required"
}
```

success

```json
{
    "HTTP Code": 200,
    "title": "Your title",
    "content": "Content of the new post",
    "author_username": "<author_username>",
    "created_at": "<creation_timestamp>"
}
```
#### 5. Get Post Detail

**GET /api/posts/<uuid:post_id>/** 
**POST /api/posts/<uuid:post_id>/** 


###### GET request

Content-Type: application/json

###### URL Parameters

'post_id'


###### headers

Authorization: Token <your-token>


###### response

fail

```json
{
    "HTTP Code": 404,
}
```

success

```json
{   
    "HTTP Code": 200,
    "post_id": "6f0f5e03-6bb1-4347-85fe-258f7aaed902",
    "title": "Your Title",
    "content": "Your post content here",
    "author_username": "testusernew",
    "created_at": "2023-11-20T11:53:34.497853-08:00",
    "comments": [
        {
            "post_id": "6f0f5e03-6bb1-4347-85fe-258f7aaed902",
            "content": "This is the text of the comment.",
            "author_username": "testuser10",
            "created_at": "2023-11-20T12:36:01.352089-08:00"
        },
        {
            "post_id": "6f0f5e03-6bb1-4347-85fe-258f7aaed902",
            "content": "This is the text of the comment.",
            "author_username": "testusernew",
            "created_at": "2023-11-20T17:10:02.656917-08:00"
        },
    ]
}
```
###### POST request

Content-Type: application/json

```json
{
    "content": "Your comment here"
}
```
###### URL Parameters

'post_id'


###### headers

Authorization: Token <your-token>

###### response
fail

```json
{
    "HTTP Code": 400,
}
```

success

```json
{
    "HTTP Code": 200,
    "post_id": "6f0f5e03-6bb1-4347-85fe-258f7aaed902",
    "content": "This is the text of the comment.",
    "author_username": "testusernew",
    "created_at": "2023-11-20T18:47:07.649778-08:00"
      
}
```
#### 6. Threads list

**GET /api/threads/** 

###### Query Parameters
'author_name'
'start_date' (YYYY-MM-DD)
'end_date' (YYYY-MM-DD)


###### header
Authorization: Token <your-token>


###### response

fail

```json
{
    "HTTP Code": 400,
    "error": "Invalid start date format"
}
```
fail

```json
{
    "HTTP Code": 400,
    "error": "Invalid end date format"
}
```

success

```json
{
    "HTTP Code": 200,
    "post_id": "<post_id>",
    "title": "<thread_title>",
    "content": "<thread_content>",
    "author_username": "<author_username>",
    "created_at": "<creation_timestamp>"
        
}
```
#### 7. Add to Favorites

**POST /api/favorites/add/<uuid:post_id>/**

###### URL Parameters

'post_id' 

###### response

fail

```json
{
    "HTTP Code": 404,
    "error": "Post not found"
}
```
success

```json
{
    "HTTP Code": 200,
    "message": "Post added to favorites"
        
}
```

#### 8. Remove from Favorites

**DELETE /api/favorites/remove/<uuid:post_id>/**

###### URL Parameters

'post_id'

###### response

fail

```json
{
    "HTTP Code": 404,
    "error": "Favorite not found"
}
```
success

```json
{
    "HTTP Code": 200,
    "message": "Post removed from favorites"
        
}
```
#### 9. Favorites List

**GET /api/favorites/**

###### response

```json
{
    "HTTP Code": 200,
    [
    {
        "id": 3,
        "post_detail": {
            "post_id": "5d60c0a0-3865-413c-bf1f-ec23f0e2d903",
            "title": "Your Title",
            "content": "Your post content here",
            "author_username": "testusernew",
            "created_at": "2023-11-26T23:50:08.939787-08:00"
        }
    },
    {
        "id": 2,
        "post_detail": {
            "post_id": "0709db5c-cae7-4de6-9484-eb3bca578fe1",
            "title": "Your Title",
            "content": "Your post content here",
            "author_username": "testusernew",
            "created_at": "2023-11-27T20:26:29.209442-08:00"
        }
    }
]
        
}
```
#### 9. Delete Post

**DELETE /api/posts/delete/<uuid:post_id>/**

###### URL Parameters

'post_id' 

###### header
Authorization: Token <your-token>

###### response

fail

```json
{
    "HTTP Code": 404,
    "error": "Post not found"
}
```

fail

```json
{
    "HTTP Code": 403,
    "error": "You do not have permission to delete this post"
}
```

success

```json
{
    "HTTP Code": 200,
    "message": "Post deleted successfully"
        
}
```
        
