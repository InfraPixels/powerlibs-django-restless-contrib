from unittest import mock

from powerlibs.django.restless.contrib.admin import CreatedByAdminMixin


def test_created_by_admin_mixin():
    class MyParentClass:
        save_model = mock.Mock()

    class MyAdminClass(CreatedByAdminMixin, MyParentClass):
        pass

    admin_object = MyAdminClass()
    mocked_object = mock.Mock()
    mocked_user = mock.Mock()
    mocked_request = mock.Mock(user=mocked_user)

    admin_object.save_model(mocked_request, mocked_object, None, None)

    assert mocked_object.created_by == mocked_user
