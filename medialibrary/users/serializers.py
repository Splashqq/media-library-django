from rest_framework import serializers

import medialibrary.users.models as users_m


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = users_m.User
        fields = ("email", "username", "avatar")
        read_only_fields = ("email",)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = users_m.User
        fields = ("email", "username", "password1", "password2")

    def validate(self, data):
        if users_m.User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError(
                {"username": "A user with this username already exists."}
            )

        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Passwords must match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")
        user = users_m.User(**validated_data)
        user.set_password(password)
        user.save()
        return user
