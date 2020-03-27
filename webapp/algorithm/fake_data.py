
def example_1():
    orders = []
    orders.append({
        'hospital': 1,
        'num_requested': 200
    })
    orders.append({
        'hospital': 2,
        'num_requested': 500
    })

    # list of senders
    htov = []
    htov.append({
        'hospital': 10,
        'group': 'VA',
        'reputation': 0.5,
        'num_ventilators': 300,
        'only_within_group': True
    })

    # maps hospital to its group
    htog = {
        1: 'VA',
        2: 'VA'
    }
    return {
        'orders': orders,
        'htov': htov,
        'htog': htog
    }

def example_2():
    orders = []
    orders.append({
        'hospital': 1,
        'num_requested': 200
    })
    orders.append({
        'hospital': 2,
        'num_requested': 500
    })
    htov = []
    htov.append({
        'hospital': 10,
        'group': 'VA',
        'reputation': 0.5,
        'num_ventilators': 300,
        'only_within_group': True
    })
    htov.append({
        'hospital': 11,
        'group': 'CA',
        'reputation': 0.5,
        'num_ventilators': 600,
        'only_within_group': True
    })
    htog = {
        1: 'VA',
        2: 'CA'
    }
    return {
        'orders': orders,
        'htov': htov,
        'htog': htog
    }


def example_3():
    orders = []
    orders.append({
        'hospital': 1,
        'num_requested': 200
    })
    orders.append({
        'hospital': 2,
        'num_requested': 500
    })
    htov = []
    htov.append({
        'hospital': 10,
        'group': 'VA',
        'reputation': 0.5,
        'num_ventilators': 100,
        'only_within_group': True
    })
    htov.append({
        'hospital': 11,
        'group': 'VA',
        'reputation': 0.5,
        'num_ventilators': 200,
        'only_within_group': True
    })
    htog = {
        1: 'VA',
        2: 'CA'
    }
    return {
        'orders': orders,
        'htov': htov,
        'htog': htog
    }
