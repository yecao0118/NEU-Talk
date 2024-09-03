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

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'A user with that username name is already registered'}, status=status.HTTP_400_BAD_REQUEST)



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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    if post.author != request.user:
        return Response({"error": "You do not have permission to delete this post"}, status=status.HTTP_403_FORBIDDEN)
    post.delete()
    return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, post_id):
    try:
        post = get_object_or_404(Post, post_id=post_id)
        Favorite.objects.get_or_create(user=request.user, post_id=post)
        return Response({"message": "Post added to favorites"}, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_favorites(request, post_id):
    try:
        favorite = Favorite.objects.get(user=request.user, post_id=post_id)
        favorite.delete()
        return Response({"message": "Post removed from favorites"}, status=status.HTTP_200_OK)
    except Favorite.DoesNotExist:
        return Response({"error": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('post_id').order_by('-created_at')
    serializer = FavoriteSerializer(favorites, many=True) 
    return Response(serializer.data, status=status.HTTP_200_OK)
