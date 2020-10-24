import re

minsup = 0.01
minconf = 0.02

def support_count(itemsets, searchSet):
    index = []
    count = 0
    searchSet = set(searchSet)
    for i in range(len(itemsets)):
        if searchSet <= set(itemsets[i]):
            count = count + 1
            index.append(i)
    return count, index

def self_join(itemset, subset):
    res = []
    for item in itemset:
        if item not in subset:
            new_set = subset + [item]
            new_set.sort()
            if new_set not in res:
                res.append(new_set)
    return res
        
def gen_candidates(itemsets, dropped, frequent_itemsets, indexes):
    candidates = []
    for i in range(len(frequent_itemsets)):
        for j in range(len(indexes[i])):
            current_candidates = self_join(itemsets[j], frequent_itemsets[i])
            for current_candidate in current_candidates:
                if current_candidate not in candidates:
                    candidates.append(current_candidate)

    res = candidates
    for candidate in candidates:
        for drop in dropped:
            if set(drop) <= set(candidate):
                res.remove(candidate)
                break
    return res

def Apriori(itemsets, candidates, min_supcount):
    # Compute frequent itemsets
    frequent_itemsets = []
    sup_count = []
    dropped = []
    indexes = []
    for candidate in candidates:
        count, index = support_count(itemsets, candidate)
        if count >= min_supcount:
            frequent_itemsets.append(candidate)
            sup_count.append(count)
            indexes.append(index)
        else:
            dropped.append(candidate)

    # Generate new candidates
    candidates = gen_candidates(itemsets, dropped, frequent_itemsets, indexes)
    if len(candidates) == 0:
        return frequent_itemsets, sup_count

    # Call Apriori
    fre_set, s_count = Apriori(itemsets, candidates, min_supcount)
    frequent_itemsets = frequent_itemsets + fre_set
    sup_count = sup_count + s_count
    return frequent_itemsets, sup_count

def split_to_last_level_itemsets(itemset):
    res = []
    for item in itemset:
        temp = list(set(itemset) - set([item]))
        temp.sort()
        res.append([temp, [item]])
    return res

def get_subset(itemset, size):
    if size > len(itemset) or size == 0:
        return []

    # Take
    sub1 = get_subset(itemset[1:], size - 1)
    if len(sub1) == 0:
        sub1 = [[itemset[0]]]
    else:
        sub1 = [itemset[:1] + sub for sub in sub1]
    # Not take
    sub2 = get_subset(itemset[1:], size)
    return sub1 + sub2
    


def gen_rules(frequent_itemsets, sup_count, min_conf):
    rules = []
    frequent_itemsets.reverse()
    process_left = frequent_itemsets.copy()
    sup_count.reverse()

    # Find from large ones
    while len(process_left) != 0:
        itemset = process_left[0]
        if len(itemset) == 1:
            break
        subsets = split_to_last_level_itemsets(itemset)

        # Check coff
        for subset in subsets:
            coff = float(sup_count[frequent_itemsets.index(itemset)]) / sup_count[frequent_itemsets.index(subset[0])]
            if coff >= min_conf and subset + [coff] not in rules:
                rules.append(subset + [coff])

                # Move LHS to RHS
                for l in range(1, len(subset[0])):
                    subs = get_subset(subset[0], l)
                    for sub in subs:
                        newR = subset[1] + sub
                        newR.sort() 
                        newL = list(set(subset[0]) - set(sub))
                        conf_sub = float(sup_count[frequent_itemsets.index(itemset)]) / sup_count[frequent_itemsets.index(newL)]
                        new_rule = [newL, newR, conf_sub]
                        if new_rule not in rules:
                            rules.append(new_rule)
                    
            else:
                if subset[0] in process_left:
                    process_left.remove(subset[0])
        process_left.remove(itemset)
    return rules

def print_support(itemset, support):
    itemset = [str(item) for item in itemset]
    res = ', '.join(itemset)
    print('{' + res + '}    support: %.4f' % support)

def print_rule(rule):
    # Set A
    setA = [str(item) for item in rule[0]]
    setA = ', '.join(setA)
    setA = '{' + setA + '}'
    
    # Set B
    setB = [str(item) for item in rule[1]]
    setB = ', '.join(setB)
    setB = '{' + setB + '}'

    print(setA + ' --> ' + setB + '    conf: %.4f' % rule[2])

# Read file
f = open('../data', 'r')
trans = f.readlines()

# Transfer data to numbers
trans = [[int(s) for s in re.split(' |\n', row) if s] for row in trans]
print('Done reading %d transactions.' % len(trans))

# Group itemIDs by transactionID
itemsets = []
itemset = []
count = 1
for tran in trans:
    if tran[0] != count:
        itemsets.append(itemset)
        itemset = []
        count = tran[0]
    itemset.append(tran[2])
itemsets.append(itemset)
print('Done grouping into %d sets.' % len(itemsets))

# Create first candidates
items = []
for itemset in itemsets:
    for item in itemset:
        if [item] not in items:
            items.append([item])
items.sort()

# Get frequent itemsets by Apriori algorithm
frequent_itemsets, support_count = Apriori(itemsets, items, minsup * len(itemsets))
support = [(float(sup) / len(itemsets)) for sup in support_count]
print('')
print('Frequent itemsets:')
for i in range(len(frequent_itemsets)):
    print_support(frequent_itemsets[i], support[i])

rules = gen_rules(frequent_itemsets, support_count, minconf)
print('')
print('Association rules:')
for rule in rules:
    print_rule(rule)