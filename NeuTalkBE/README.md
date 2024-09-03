### 1. Team
#### Team Name: Mars2Moon
#### Team Member: Ye Cao, Wanshi Ma, Xiang Xiang Chen
#### Project Name: Neu Talk

### 2. Background and Mission of the Product
#### Integrated Communication Platform Need
- The product was developed due to the need for a more unified and efficient communication platform within the university.
- Current solutions, like WeChat groups, show limitations and are not accessible to non-Chinese speakers as there are no English version.

#### Limitations of Current Tools
- WeChat Groups: Key information can be overlooked, and sometimes messages receive no response.
- RED (Social Media Platform): Plagued with advertisements and lacks search efficiency.

#### Mission of the New Platform
- **A Hub for Community**: Aims to offer a platform for students, faculty, and staff to connect.
- **Encouraging Collaboration**: Designed to foster collaboration across various departments and groups.
- **Information Sharing**: Serves as a central repository for sharing academic resources, news, and important announcements.
- **Supporting Students**: Emphasizes peer-to-peer support, discussion groups, and provides space for student initiatives.

### 3. How to Run the Product
As we use the Front-end and Back-end separation development model,so we need to run the backend server first then run the front end server.
#### Back End
Github Repository: https://github.com/wanshima/NeuTalkBE <br>
To set up both Django and Django REST framework using pip: <br>
```pip install django djangorestframework```

To run the Django development server, in the terminal of the project（NEUproject）, run the command: <br>
```cd NEUproject```
<br>
```python manage.py runserver```
#### Front End
Github Repository: https://github.com/xiangxichen26/NeuTalk <br>
install all the requirements(be sure you have install the node.js):<br>
```npm install```

To run the server,in the terminal of the project, run the command:<br>
```npm run dev```


### 4. Main Functions (Back End)

#### Models created in "accounts/models.py"
These models form a basic structure for the forum, allowing for user registration, posting content, commenting on posts, and favoriting posts. <br>
1. CustomUser
2. Post
3. Comment
4. Favorite


```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid

# user model
class CustomUser(AbstractUser):
    def __str__(self):
        return self.username
    
# post model
class Post(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# comment model
class Comment(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    post_id = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

# favorite post model
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        unique_together = ('user', 'post_id')
```

#### Serializers created in "accounts/serializers.py"


```python
from rest_framework import serializers
from .models import CustomUser, Post, Comment, Favorite

# serializer for user authentication
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# serializer for post 
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['post_id', 'title', 'content', 'author_username', 'created_at']

    def get_author_username(self, obj):
        return obj.author.username

# serializer for comment 
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['unique_id', 'post_id', 'content', 'author_username', 'created_at']

    def get_author_username(self, obj):
        return obj.author.username

# serializer for favorite post
class FavoriteSerializer(serializers.ModelSerializer):
    post_detail = PostSerializer(source='post_id')

    class Meta:
        model = Favorite
        fields = ['id', 'post_detail']
```

#### API view created in "accounts/views.py"
These views handle various functionalities: <br>
1. User registration page
2. Login page for users
3. Logout functionality
4. Page to create a new post
5. View details of a specific post
6. Comment on a post
7. Delete a specific post
8. List all posts
9. View user's favorite posts
10. Add a post to favorites
11. Remove a post from favorites


```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from .models import CustomUser, Post, Comment, Favorite
from .serializers import PostSerializer, UserSerializer, FavoriteSerializer, CommentSerializer

# API view for user registration
# It uses UserSerializer to validate and save the new user data. 
# If validation fails (e.g., username already exists), it returns an error response.
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'A user with that username name is already registered'}, status=status.HTTP_400_BAD_REQUEST)

# API view for user login with authentication tokens
# It authenticates the user and, if successful, generates and returns an authentication token for further secured interactions with the API.
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            response_data = {
                'username': user.username,
                'token': token.key,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

# API view for user logout 
# It deletes the user's auth token, effectively ending the session.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API view for user to create a new post
# It checks for authentication, validates the post data using PostSerializer, and saves it if valid.
@api_view(['POST'])
def create_post(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = PostSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(author=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API view for user to view details of a specific post or add comment to the post
# For GET requests, it returns post details along with comments; for POST requests, it allows authenticated users to add a new comment.
@api_view(['GET','POST'])
def get_post_detail(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, post_id=post_id).exists() 
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        comment_data = {
            'content': request.data.get('content'),
            'post_id': post.post_id  
        }
        comment_serializer = CommentSerializer(data=comment_data, context={'request': request})
        if comment_serializer.is_valid():
            comment_serializer.save(author=request.user)  
            return Response(comment_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
        comment_serializer = CommentSerializer(comments, many=True)
        post_serializer = PostSerializer(post)
        post_data_with_comments = post_serializer.data
        post_data_with_comments['comments'] = comment_serializer.data
        post_data_with_comments['is_favorite'] = is_favorite
        return Response(post_data_with_comments, status=status.HTTP_200_OK)

# API view for user to view all post threads
# It supports filtering by author, start date, and end date. Only authenticated users can access this view.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def thread_list(request):
    author_name = request.query_params.get('author_name')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    queryset = Post.objects.all()
    if author_name:
        queryset = queryset.filter(author__username=author_name)
    if start_date:
        parsed_start_date = parse_datetime(start_date)
        if parsed_start_date:
            queryset = queryset.filter(created_at__gte=parsed_start_date)
    if end_date:
        parsed_end_date = parse_datetime(end_date)
        if parsed_end_date:
            queryset = queryset.filter(created_at__lte=parsed_end_date)
    queryset = queryset.order_by('-created_at')
    serializer = PostSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# API view for user to add a post to favoriate post collection 
# It checks if the post exists and adds it to the user's favorites.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, post_id):
    try:
        post = get_object_or_404(Post, post_id=post_id)
        Favorite.objects.get_or_create(user=request.user, post_id=post)
        return Response({"message": "Post added to favorites"}, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

# API view for user to delete a post from favoriate post collection 
# It checks if the favorite entry exists and deletes it if found.
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_favorites(request, post_id):
    try:
        favorite = Favorite.objects.get(user=request.user, post_id=post_id)
        favorite.delete()
        return Response({"message": "Post removed from favorites"}, status=status.HTTP_200_OK)
    except Favorite.DoesNotExist:
        return Response({"error": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND)

# API view for user to view all favorite posts
# It serializes the favorite posts using FavoriteSerializer.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('post_id').order_by('-created_at')
    serializer = FavoriteSerializer(favorites, many=True) 
    return Response(serializer.data, status=status.HTTP_200_OK)

```

### 5. Front End
#### Pages
1. NeuTalk/src/views/HomePage.vue : Layout of this product and log out 
2. NeuTalk/src/views/LoginView.vue : Log in and sign up
3. NeuTalk/src/views/MyCollectionList.vue : show all the posts which you have collected
4. NeuTalk/src/views/MyPostList.vue: show all the posts which created by yourself
5. NeuTalk/src/views/PostList.vue: show all the posts and can do some filter
6. NeuTalk/src/views/PostDetail.vue: show the detail of the post and can make comment, collect the post, remove collection of this post, delete your own post.
#### Router
1. router management: NeuTalk/src/router/index.ts

#### Usage of APIs
1. get post list
```javascript
    const getPostList = () => {
        axios.get('threads/', {
            params: {
              author_name: window.sessionStorage.getItem('username'),
              start_date: filterDate.value[0],
              end_date: filterDate.value[1],
            }
          })
          .then((res: any) => {
            postList.value = res.data;
            console.log(postList.value)
          })
          .catch((err: any) => {
            console.log(err)
          })
      };
```

2. get post deatil
```javascript
const getPostDetail = () => {
            console.log();
            proxy.get("http://127.0.0.1:5173/api/posts/" + post_id)
                .then((res: any) => {
                    postDetail.value = res;
                    console.log(res.is_favorite);
                })
                .catch((err: any) => {
                    console.log(err);
                });
        };
```

3. logout
```javascript
    const handleCommand = (command: string | number | object) => {
      if (command === 'logout') {
        axios.post('http://127.0.0.1:5173/api/logout/')
          .then(() => {
            window.sessionStorage.clear();
            ElMessage.success('Log out successfully');
            router.push({ path: '/login' });
          })
          .catch((err: any) => {
            ElMessage.error('Log out failed');
            console.log(err)
          })
      }
    };

```
4. create post
```javascript
const createPost = () => {
      axios.post('new/', createPostForm)
        .then(() => {
          createPostForm.content = '';
          createPostForm.title = '';
          if (window.location.pathname === '/postList') {
            window.location.reload();
          }
          else {
            router.push({ path: '/postList' });
          }
          ElMessage.success('Create post successfully');
          createFormVisible.value = false;
        })
        .catch((err: any) => {
          ElMessage.error('Create post failed');
          console.log(err)
        })

    };
```
5. log in
```javascript
const login = () => {
      proxy.post('login/', loginForm).then((res: any) => {
        ElMessage({
          message: 'Login successfully',
          type: 'success'
        });
        router.push({ path: '/' });
        window.sessionStorage.setItem('token', res.token);
        console.log(window.sessionStorage.getItem('token'));
        window.sessionStorage.setItem('username', loginForm.username);
      })
      .catch((err: any) => {
        ElMessage({
          message: err.error,
          type: 'error'
        });
        console.log(err)
      })
    }

```
6. sign up
```javascript
const register = () => {
      proxy.post('register/', registerForm)
      .then((res: any) => {
        // show login form
        showLoginForm.value = true;
        ElMessage({
          message: 'Register successfully',
          type: 'success'
        })
        console.log(res)
      })
      .catch((err: any) => {
        ElMessage({
          message: err.error,
          type: 'error'
        });
        console.log(err)
      })
    }

```
7. get my collection list
```javascript
 const getMyCollectionList = () => {
            axios.get('favorites/')
                .then((res: any) => {
                    postList.value = res.data;
                    console.log(postList.value)
                })
                .catch((err: any) => {
                    console.log(err)
                })
        };
```
8. create comment
```javascript
 const createComment = () => {
            proxy.post("http://127.0.0.1:5173/api/posts/" + post_id + "/", commentCentent)
                .then((res: any) => {
                    console.log(res);
                    getPostDetail();
                    commentCentent.content = "";
                })
                .catch((err: any) => {
                    console.log(err);
                });
        };
```
9. collect post
```javascript
const collectPost = () => {
            proxy.post("http://127.0.0.1:5173/api/favorites/add/" + post_id + "/")
                .then((res: any) => {
                    console.log(res);
                    ElMessage.success("Collect post successfully");
                    getPostDetail();
                })
                .catch((err: any) => {
                    console.log(err);
                });
        };
```
10. delete collection
```javascript
const cancelCollectPost = async() => {
            try {
                await axios.delete('http://127.0.0.1:5173/api/favorites/remove/'+ post_id + "/");
                ElMessage.success("Remove collection successfully");
                getPostDetail();
            } catch (error) {
                if (axios.isAxiosError(error)) {
                    console.error('Error deleting resource:', error.response?.data);
                } else {
                    console.error('Unexpected error:', error);
                }
                throw error; 
            }
        };
```
11. delete post
```javascript
const deletePost = async () => {
            try {
                await axios.delete('http://127.0.0.1:5173/api/posts/delete/'+ post_id + "/");
                ElMessage.success("Delete post successfully");
                router.push({ path: "/postList" });
            } catch (error) {
                if (axios.isAxiosError(error)) {
                    console.error('Error deleting resource:', error.response?.data);
                } else {
                    console.error('Unexpected error:', error);
                }
                throw error; 
            }
            
        };
```


```python

```
