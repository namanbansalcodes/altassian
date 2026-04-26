import factory
from django.contrib.auth import get_user_model

from user_accounts.models import Organization

User = get_user_model()


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = "Altassian"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    display_name = factory.Sequence(lambda n: f"User {n}")
    role = User.Role.MEMBER
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or "testpass123")
        if create:
            obj.save()


class AdminFactory(UserFactory):
    role = User.Role.ADMIN


from spaces.models import Space


class SpaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Space

    slug = factory.Sequence(lambda n: f"space-{n}")
    name = factory.Sequence(lambda n: f"Space {n}")
