from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import SpotifyInfo, Instrument, Song, Element, File


class SpotifyInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpotifyInfo
        fields = ('access_token', 'refresh_token', 'device_id')


class UserSerializer(serializers.ModelSerializer):
    spotify_info = SpotifyInfoSerializer(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'spotify_info')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ['id', 'make', 'model', 'name', 'family',
                  'tonal_range', 'year']


def get_primary_key_related_model(model_class, **kwargs):
    """
    Nested serializers are a mess. https://stackoverflow.com/a/28016439/2689986
    This lets us accept ids when saving / updating instead of nested objects.
    Representation would be into an object (depending on model_class).
    """
    class PrimaryKeyNestedMixin(model_class):

        def to_internal_value(self, data):
            try:
                return model_class.Meta.model.objects.get(pk=data)
            except model_class.Meta.model.DoesNotExist:
                self.fail('does_not_exist', pk_value=data)
            except (TypeError, ValueError):
                self.fail('incorrect_type', data_type=type(data).__name__)

        def to_representation(self, data):
            return model_class.to_representation(self, data)

    return PrimaryKeyNestedMixin(**kwargs)


class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'album', 'year', 'image', 'genre', 'duration', 'explicit', 'key', 'mode', 'lyrics', 'time_signature', 'tempo',
                  'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'original', 'spotify_url', 'spotify_id', 'elements']


class ElementSerializer(serializers.ModelSerializer):

    song = get_primary_key_related_model(SongSerializer)

    class Meta:
        model = Element
        fields = ["id", "name",
                  "start",
                  "duration",
                  "loudness",
                  "tempo",
                  "key",
                  "mode",
                  "lyrics",
                  "learned",
                  "time_signature",
                  "song"]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file']
