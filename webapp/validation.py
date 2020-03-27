import functools

def validate_signup(data, user_type, required_fields, ValidationError):
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
