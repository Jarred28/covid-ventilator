
# simple allocator that greedily fulfills orders
def allocate(orders, htov, htog):
    """
    orders: list[
        orders_dict{
            'hospital': [hospital_id]
            'num_requested': (int)
        }
    ]
    htov: list[
        hospital_dict{
        'hospital': [hospital_id]
        'group': [group_id]
        'reputation': (float)
        'num_ventilators': (int)
        'only_within_group': (boolean)
        }
    ]
    htog: dict{hospital --> group}

    returns list[tuple(sender, amount, receiver)]
    """
    allocs = []

    for order in orders:
        requesting_hospital = order['hospital']
        requesting_hospital_group = htog[requesting_hospital]
        for sender in htov:
            if sender["num_ventilators"] <= 0:
                continue

            if sender["only_within_group"] and not requesting_hospital_group == sender['group']:
                continue

            # more demand than supply
            # create allocation with entire supply, set supply to 0
            if order['num_requested'] > sender['num_ventilators']:
                allocs.append((sender['hospital'], sender['num_ventilators'], requesting_hospital))
                order['num_requested'] -= sender['num_ventilators']
                sender['num_ventilators'] = 0
            #more supply than num_requested
            #create allocation with amount demanded, adjust supply
            else:
                allocs.append((sender['hospital'], order['num_requested'], requesting_hospital))
                sender['num_ventilators'] -= order['num_requested']
                break #exit inner loop since order has been fulfilled

    return allocs

# example usage
# def example():
#     orders = []
#     orders.append({
#         'hospital': 1,
#         'num_requested': 200
#     })
#     orders.append({
#         'hospital': 2,
#         'num_requested': 500
#     })
#
#     # list of senders
#     htov = []
#     htov.append({
#         'hospital': 10,
#         'group': 'VA',
#         'reputation': 0.5,
#         'num_ventilators': 300,
#         'only_within_group': True
#     })
#
#     # maps hospital to its group
#     htog = {
#         1: 'VA',
#         2: 'VA'
#     }
#
#     list_of_shipments = allocate(orders, htov, htog)
