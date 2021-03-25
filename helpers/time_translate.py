from typing import List


def time_to_str_intervals(intervals: List[List[int]]) -> List[str]:
    """
    Превращает интервалы вида [[720, 900], [1200, 1350]] -> ["12:00-15:00", "20:00-22:30"]
    :param intervals: Интревалы в int (int - минуты)
    :return: Интервалы в str
    """
    return [
        f"{i[0]//600}{i[0]%600//60}:{i[0]%60//10}{i[0]%10}-{i[1]//600}{i[1]%600//60}:{i[1]%60//10}{i[1]%10}"
        for i in intervals
    ]


def time_to_int_intervals(intervals: List[str]) -> List[List[int]]:
    """
    Превращает интервалы вида ["12:00-15:00", "20:00-22:30"] -> [[720, 900], [1200, 1350]]
    :param intervals: Интревалы в int (int - минуты)
    :return: Интервалы в str
    """
    if type(intervals) == str:
        intervals = list((intervals, ))
    return list(map(lambda x: [int(x[0:2]) * 60 + int(x[3:5]), int(x[6:8]) * 60 + int(x[9:11])], intervals))

