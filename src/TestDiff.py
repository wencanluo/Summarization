import difflib

test_result_before_refactoring = open('../data/before.txt').read().splitlines()
test_result_after_refactoring = open('../data/after.txt').read().splitlines()

d = difflib.Differ()
delta = d.compare(test_result_after_refactoring, test_result_before_refactoring)

ins = []
outs = []
for i in delta:
    if len(i) > 0:
        if i[0] == '+': #insert
            outs.append(i.strip())
        if i[0] == '-': #delete
            ins.append(i.strip())
    differences = ins + outs

print len(outs)
print len(ins)

#recall = TP / N_before
recall = (len(test_result_before_refactoring) - len(outs)) * 1.0/len(test_result_before_refactoring)

#precision = TP/N_after
precision = (len(test_result_before_refactoring) - len(outs)) * 1.0/len(test_result_after_refactoring)

f1_score = 2*recall * precision / (recall + precision)

print recall, precision, f1_score