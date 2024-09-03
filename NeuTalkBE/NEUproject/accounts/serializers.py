from rest_framework import serializers
from .models import CustomUser, Post, Comment, Favorite

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

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['post_id', 'title', 'content', 'author_username', 'created_at']

    def get_author_username(self, obj):
        return obj.author.username

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['unique_id', 'post_id', 'content', 'author_username', 'created_at']

    def get_author_username(self, obj):
        return obj.author.username

class FavoriteSerializer(serializers.ModelSerializer):
    post_detail = PostSerializer(source='post_id')

    class Meta:
        model = Favorite
        fields = ['id', 'post_detail']