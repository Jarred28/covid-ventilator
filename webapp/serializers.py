from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(style={
        'placeholder': 'Username',
    })
    password = serializers.CharField(style={
        'input_type': 'password',
        'placeholder': 'Password',
    })
