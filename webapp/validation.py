import functools

from .models import User

def validate_signup(data, user_type, ValidationError):
    required_fields = {}
    required_fields[User.UserType.Hospital.name] = ['hospital_name', 'hospital_address']
    required_fields[User.UserType.Supplier.name] = ['supplier_name', 'supplier_address']
    required_fields[User.UserType.HospitalGroup.name] = ['hospitalgroup_name']
    required_fields[User.UserType.SystemOperator.name] = ['systemoperator_name']

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
