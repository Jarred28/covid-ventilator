from .models import HospitalGroup

def get_hospital_group_choices():
    return [(hg.id, hg.name) for hg in HospitalGroup.objects.all()]
