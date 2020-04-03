import numpy as np

# calculates a weighted average of contribution, reputation, and load for
# each hospital to calculate the "importance" of each hospital and fulfulls
# orders in order of importance (highest to lowest)
def allocate(orders, htov, system_params):
    """
    orders: list[ tuple(Order, Hospital) ] (Hospital that submitted the order)
    htov: list[ tuple(Hospital, num_available) ]
    system_params: dict{
        contribution_weight, strategic_reserve, reputation_weight,
        projected_load_weight
    }

    returns list[tuple(sender, amount, receiver)]
    """

    #system parameters
    w_c = system_params.contribution_weight
    strategic_reserve = system_params.strategic_reserve
    w_r = system_params.reputation_score_weight
    w_p = system_params.projected_load_weight


    #relevant variables

    def relative_contributions(hospitals):
        contributions = np.array([hospital.contribution for hospital in hospitals],
            dtype=np.float)
        return contributions/np.sum(contributions)

    def relative_loads(hospitals):
        loads = np.array([hospital.projected_load for hospital in hospitals],
            dtype=np.float)
        return loads/np.sum(loads)

    def reputations(hospitals):
        return np.array([(hospital.reputation_score or 1) for hospital in hospitals],
            dtype=np.float)

    hospitals = [t[1] for t in orders]
    contribution_scores = relative_contributions(hospitals)
    load_scores = relative_loads(hospitals)
    rep_scores = reputations(hospitals)
    stress_factors = w_c*contribution_scores + w_r*rep_scores + w_p*load_scores

    # from highest importance to lowest
    sorted_by_importance = list(zip(orders, stress_factors))
    sorted_by_importance = sorted(sorted_by_importance, key=lambda x: x[1], reverse=True)



    class Sender:
        def __init__(self, Hospital, num_avail):
            self.hospital = Hospital
            self.num_available = (1 - strategic_reserve) * num_avail

    senders = [Sender(h[0], h[1]) for h in htov]
    allocs = []
    for (order, receiver), stress_factors in sorted_by_importance:


        for sender in senders:

            if sender.hospital.id == receiver.id or sender.num_available == 0:
                continue

            elif sender.hospital.within_group_only and receiver.hospital_group != sender.hospital.hospital_group:
                continue

            #eligible sender
            #more supply than demand
            if sender.num_available >= order.num_requested:
                sender.num_available -= order.num_requested
                allocs.append((
                    sender.hospital.id, order.num_requested, receiver.id
                ))
                order.num_requested = 0
                break

            else:
                order.num_requested -= sender.num_available
                allocs.append((
                    sender.hospital.id, sender.num_available, receiver.id
                ))
                sender.num_available = 0

    return allocs
