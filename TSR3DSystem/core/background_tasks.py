import csv
import uuid
import pyfpgrowth
from background_task import background

from django.core.mail import send_mail
from django.db.models import Prefetch
from efficient_apriori import apriori
from django.conf import settings
from collections import Counter

from .settings import DATABASES
from ..models import AllProteins, Hierarchy


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
    transactions = {}
    for each in Hierarchy.objects.using(protein_class).all():
        transactions.update({each.pk: list((str(key) for key in AllProteins.objects.using(protein_class).filter(
            maxDist__lte=max_distance, protein_id_id=each.pk).values_list('protein_key', flat=True)))})

    # Loop through and change the names to occurrences as well
    for transaction in transactions:
        occurrences = Counter(transactions[transaction])
        for key, frequency in occurrences.items():
            for count in range(1, frequency+1):
                transactions[transaction].append(key+'_'+str(count))
                transactions[transaction].remove(key)
    print(transactions)

    # Save the file
    file_name = str(uuid.uuid4())
    wtr = csv.writer(open(file_name + '.csv', 'w'), delimiter=',', lineterminator='\n')
    for x in transactions:
        wtr.writerow(transactions[x])
    key_csv = data_generator(file_name + '.csv')

    # Pass through Apriori
    itemsets, rules = apriori(key_csv, min_support=min_support, min_confidence=min_confidence)
    print(itemsets)


    # Switch to other  databases and filter them - OBSOLETE
    # for each in DATABASES:
        # if each == 'default':
        #     continue
        # keys.append(
            # (tuple(AllProteins.objects.using(each).filter(protein_key__in=filtered_keys).values_list('protein_key',
            #                                                                                          flat=True).distinct())))

    # FP Growth Portion
    # patterns = pyfpgrowth.find_frequent_patterns(keys, min_support)
    # rules = pyfpgrowth.generate_association_rules(patterns, min_confidence)
    # print(patterns)
    # print(rules)

    # Search Classes with Apriori Results
    filtered_dict = {}
    for itemset in itemsets:
        for item in itemsets[itemset]:
            classes = ''
            for each in DATABASES:
                if each == 'default':
                    continue
                for protein_key in item:
                    exists = AllProteins.objects.using(each).filter(protein_key=protein_key).exists()
                    if exists:
                        classes += each+', '
            filtered_dict.update({str(item): classes})

    # Email user results
    # send_mail(
    #     'TSR3DSystem Results',
    #     [str(itemsets), str(rules), str(classes)],
    #     #'akomebaby@yahoo.com',
    #     settings.EMAIL_HOST_USER,
    #     [email],
    #     fail_silently=False,
    # )
    print('send email here')
