#
# array = [10, 1, 2, 7, 6, 1, 5]
#
# target = 8

def get_sum_combination(array, target):
    result = []
    temp = []
    current_sum = 0
    for i, elm in enumerate(array):
        if elm > target:
            continue
        current_sum += elm
        temp.append(elm)
        for j, elm2 in enumerate(array):
            if elm2 > target or j == i:
                continue
            if current_sum + elm2 <= target:
                current_sum += elm2
                temp.append(elm2)
            if current_sum == target:
                result.append(temp)
                print(temp)
                print(result)
                break
            temp = []
            current_sum = 0


get_sum_combination([10, 1, 2, 7, 6, 1, 5], 8)
