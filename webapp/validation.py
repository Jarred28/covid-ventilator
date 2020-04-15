import functools

from .models import User


def validate_signup(data, user_type, ValidationError):
    # required_fields enforces that the user has all of the fields in its
    # user_type section and that none of the other fields in the dictionary are
    # filled out
    required_fields = {}
    required_fields[User.UserType.Hospital.name] = ['hospital_name', 'hospital_address']
    required_fields[User.UserType.Supplier.name] = ['supplier_name', 'supplier_address']
    required_fields[User.UserType.HospitalGroup.name] = ['hospitalgroup_name']
    required_fields[User.UserType.System.name] = ['System_name']

    if not user_type:
        return

    all_fields = functools.reduce(
        lambda a, b: a + b,
        required_fields.values()
    )
    other_fields = [field for field in all_fields if field not in required_fields[user_type]]
    missing_fields = functools.reduce(
        lambda a, b: a or b,
        [data.get(element, '') == '' for element in required_fields[user_type]]
    )
    extra_fields = not functools.reduce(
        lambda a, b: a and b,
        [data.get(element, '') == '' for element in other_fields]
    )
    if missing_fields:
        raise ValidationError('{user_type} information must be provided.'.format(user_type=user_type))
    if extra_fields:
        raise ValidationError('Only {user_type} information should be provided.'.format(user_type=user_type))

    # hospital needs hospital group
    # not in required_fields because the other types of users can have this filled out
    if user_type == User.UserType.Hospital.name and data.get('hospital_hospitalgroup', '') == '':
        raise ValidationError('Hospital group must be selected in Hospital section. If no hospital groups are listed, one must be created before adding this hospital')
