import csv
import time
import uuid
import os
import psutil
import sys
import pandas as pd
from collections import Counter

from memory_profiler import profile

from .settings import DATABASES
from ..models import AllProteins, Hierarchy
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth
from memory_profiler import profile

# @background()
@profile
def class_filter(email, protein_class, max_distance, min_support):
    start = time.clock()

    transactions = []
    for each in Hierarchy.objects.using(protein_class).all():
        transactions.append(list((str(key) for key in AllProteins.objects.using(protein_class).filter(
            maxDist__lte=max_distance, protein_id_id=each.pk).values_list('protein_key', flat=True))))

    unique_keys_amount = AllProteins.objects.using(protein_class).filter(
            maxDist__lte=max_distance).values_list('protein_key', flat=True).distinct().count()

    # Loop through and change the names to occurrences as well
    for x, transaction in enumerate(transactions):
        occurrences = Counter(transactions[x])
        for key, frequency in occurrences.items():
            for count in range(1, frequency+1):
                transactions[x].append(key+'_'+str(count))
                transactions[x].remove(key)
    print(transactions)

    # Pandas Table
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    transactions = pd.DataFrame(te_ary, columns=te.columns_)

    # Pass through Apriori
    # algorithm = "Apriori"
    # frequent_itemsets = apriori(transactions, min_support=min_support, use_colnames=True, low_memory=True)
    # frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    # frequent_itemsets = frequent_itemsets[frequent_itemsets.length > 2]
    # frequent_itemsets.drop(columns=['support', 'length'])
    # print(frequent_itemsets)

    # Pass through FPGrowth
    algorithm = "FPGrowth"
    frequent_itemsets = fpgrowth(transactions, min_support=min_support, use_colnames=True)
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    frequent_itemsets = frequent_itemsets[frequent_itemsets.length > 2]
    frequent_itemsets.drop(columns=['support', 'length'])
    print(frequent_itemsets)

    transactions = None

    # Search Classes with Apriori Results
    if len(frequent_itemsets) > 0:
        protein_classes = [class_name for class_name in DATABASES if
                           class_name != 'default' and class_name != protein_class]

        column_names = ['ItemSet: {Item: Count}']
        [column_names.extend([x + ' - % of Proteins that have the Itemset', x + ' - Proteins that have the Itemset']) for x in protein_classes]
        df = pd.DataFrame(columns=column_names)
        float_columns = [column for column in column_names[1::2]]

        for itemset in frequent_itemsets['itemsets']:
            classes = {}
            for class_name in protein_classes:
                protein_itemset_list = []
                for protein in Hierarchy.objects.using(class_name).all():

                    item_set_list = [protein_key[:-2] for protein_key in itemset]
                    counted_item_set_list = Counter(item_set_list)

                    protein_key_list = AllProteins.objects.using(class_name).filter(protein_key__in=item_set_list,
                                                                                    protein_id_id=protein.pk).values_list(
                                                                                    'protein_key', flat=True)
                    protein_key_counter = Counter(protein_key_list)

                    count_checker = Counter(
                        {key: protein_key_counter[int(key)] - value for key, value in counted_item_set_list.items()})

                    # Checks to make sure that it has all of the keys.
                    # If there are any negative values than it does not have all of the items in the itemset
                    protein_has_set = not any(elem < 0 for elem in count_checker.values())

                    if protein_has_set:
                        protein_itemset_list.append(protein.pk)
                class_support = len(protein_itemset_list)/Hierarchy.objects.using(class_name).count()
                classes.update({class_name+ ' - % of Proteins that have the Itemset': class_support,
                                class_name + ' - Proteins that have the Itemset': [str(protein_itemset_list)[1:-1]]})

            classes.update({'ItemSet: {Item: Count}': str(counted_item_set_list)[7:]})
            df = df.append(pd.DataFrame(classes), ignore_index=True, sort=False)

        rows_to_drop = []
        for index, row in df.iterrows():
            for column in float_columns:
                if row[column] != 0.0:
                    break
                if column == float_columns[-1]:
                    rows_to_drop.append(index)
        df = df.drop(rows_to_drop)
        print(df.to_html)
        msg_html = render_to_string('email_template.html', {'filtered_dict': df.to_html(index=False),
                                                            'protein_classes': protein_classes,
                                                            'time': round(time.clock() - start, 4),
                                                            'protein_class': protein_class,
                                                            'max_distance': max_distance,
                                                            'min_support': min_support,
                                                            'algorithm': algorithm,
                                                            'unique_keys_amount': unique_keys_amount,
                                                            }
                                    )
        send_mail(
            'TSR3DSystem Results',
            '',
            settings.EMAIL_HOST_USER,
            [email],
            html_message=msg_html,
            fail_silently=False,
        )
    else:
        send_mail(
            'TSR3DSystem Results',
            'There were no itemsets that met the minimum support and minimum confidence',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
