import csv
import uuid
from background_task import background

from django.core.mail import send_mail
from efficient_apriori import apriori

from .settings import DATABASES
from ..models import AllProteins


def data_generator(filename):
    """
    Data generator, needs to return a generator to be called several times.
    """

    def data_gen():
        with open(filename) as file:
            for line in file:
                yield tuple(k.strip() for k in line.split(','))

    return data_gen


# @background()
def class_filter(email, protein_class, max_distance, min_support, min_confidence):
    filtered_keys = list(AllProteins.objects.using(protein_class).filter(maxDist__lte=max_distance).values_list(
        'protein_key', flat=True).distinct())
    # Switch to other  databases and filter them
    keys = []
    for each in DATABASES:
        if each == 'default':
            continue
        keys.append(
            (tuple(AllProteins.objects.using(each).filter(protein_key__in=filtered_keys).values_list('protein_key',
                                                                                                     flat=True).distinct())))

    # Apriori Portion
    file_name = str(uuid.uuid4())
    wtr = csv.writer(open(file_name + '.csv', 'w'), delimiter=',', lineterminator='\n')
    for x in keys: wtr.writerow([x])
    key_csv = data_generator(file_name+'.csv')
    itemsets, rules = apriori(key_csv, min_support=min_support, min_confidence=min_confidence)
    print(rules)

    # Search Classes with Apriori Results

    classes = []
    for each in DATABASES:
        if each == 'default':
            continue
        if AllProteins.objects.using(each).filter(protein_key__in=itemsets).exists():
            classes.append(each)

    # Email user results
    send_mail(
        'TSR3DSystem Results',
        str(itemsets, rules, classes),
        'ayokomilasisi18@gmail.com',
        [email],
        fail_silently=False,
    )
    print('send email here')
