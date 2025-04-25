from rest_framework import serializers

import medialibrary.catalog.serializers as catalog_s
import medialibrary.users.models as users_m
from medialibrary.utils.drf import ReadablePKRF


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


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords must match."}
            )

        if data["new_password"] == data["old_password"]:
            raise serializers.ValidationError(
                {"new_password": "The new password is the same as the old one."}
            )

        if not self.context["user"].check_password(data["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Old password is incorrect."}
            )
        return data


class UserRequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not users_m.User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email not exists."}
            )
        return data


class UserMovieCollectionSerializer(serializers.ModelSerializer):
    movie = ReadablePKRF(catalog_s.MovieSerializer)

    class Meta:
        model = users_m.UserMovieCollection
        fields = "__all__"
        read_only_fields = ("user",)


class UserSeriesCollectionSerializer(serializers.ModelSerializer):
    series = ReadablePKRF(catalog_s.SeriesSerializer)

    class Meta:
        model = users_m.UserSeriesCollection
        fields = "__all__"
        read_only_fields = ("user",)


class UserGameCollectionSerializer(serializers.ModelSerializer):
    game = ReadablePKRF(catalog_s.GameSerializer)

    class Meta:
        model = users_m.UserGameCollection
        fields = "__all__"
        read_only_fields = ("user",)
