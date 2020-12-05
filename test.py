import re
from models.Schedule import Schedule
from models.ScheduledOperation import ScheduledOperation
from models.Operation import Operation
from models.Category import Category
from os import replace
import pandas as pd
import numpy as np
import math as math
import datetime
from difflib import SequenceMatcher

import time

start = time.time()


# the further element is in the list, the higher its weight is
def weighedAvg(values, minWeight=0.5, maxWeight=1.5):
    weights = np.linspace(minWeight, maxWeight, len(values))
    return np.average(values, weights=weights)


def weighted_avg_and_std(values, minWeight=0.5, maxWeight=1.5):
    weights = np.linspace(minWeight, maxWeight, len(values))
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))


def weighted_avg_std_coefficientOfVariation(values, minWeight=0.5, maxWeight=1.5):
    avg, std = weighted_avg_and_std(values, minWeight, maxWeight)
    cv = std / avg
    return avg, std, (cv if cv > 0 else -cv)


# will ignore thoose substring while checking similarity
toIgnore = [
    's.a.',
    '.pl',
    'www.',
    'sp.zo.o.',
]


def cleanOperationName(name):
    # only first 20 characters, to lowercase, get rid of spaces
    name_ = name.lower().replace(" ", "")
    # get rid of digits
    name_ = re.sub('\d', '', name_)
    # get rid of substrings that sould be ignored
    for s in toIgnore:
        name_ = name_.replace(s, "")

    return name_[0:20]


def similar(a, b):
    return SequenceMatcher(None, cleanOperationName(a), cleanOperationName(b)).ratio()
    #isjunk = lambda x: x == " "


def daterange(start_date, end_date):
    for n in range(1 + int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


'''
def getStatsOfArray(a):
    # check stddev of values
    median = np.median(a)
    avg = np.average(a)
    var = np.var(a)
    std = np.std(a)
    stds = np.std(a, ddof=1)
    # https://en.wikipedia.org/wiki/Coefficient_of_variation
    cv = std / abs(avg)

    # print(" MED: %8.2f  AVG: %8.2f   VAR: %8.2f   STD: %8.2f   STDs: %8.2f" %
    #      (median, avg, var, std, stds))
    # print(a)
    return median, avg, var, std, stds, cv
'''


def getBins(minDate, maxDate, initialValue=None):
    # if hasattr(getBins, "minDate") and hasattr(getBins, "maxDate") and getBins.minDate == minDate and getBins.minDate == maxDate:
    #    return getBins.distinctDays, getBins.distinctWeeks, getBins.distinctMonths

    getBins.minDate = minDate
    getBins.maxDate = maxDate
    distinctDays = {}
    distinctWeeks = {}
    distinctMonths = {}
    for single_date in daterange(minDate, maxDate):
        ymd = (single_date.strftime("%Y-%m-%d"))
        yw = (single_date.strftime("%Y-%W"))
        ym = (single_date.strftime("%Y-%m"))

        distinctDays[ymd] = initialValue
        if(yw not in distinctWeeks.keys()):  # distinctWeeks.__len__() == 0 or
            distinctWeeks[yw] = initialValue
        if(ym not in distinctMonths.keys()):  # distinctMonths.__len__() == 0 or
            distinctMonths[ym] = initialValue

    getBins.distinctDays = distinctDays
    getBins.distinctWeeks = distinctWeeks
    getBins.distinctMonths = distinctMonths

    return getBins.distinctDays, getBins.distinctWeeks, getBins.distinctMonths


#
# templateSchedules = {'daily' : schedule, 'weekly' : schedule, 'monthly' : schedule}
#
def tryToGenerateScheduledOperationFromSimilarOperations(similarOperations, minDate, maxDate, templateSchedules, user_id, groupName=None, category=None, maxCv=1.0, minValue=5.0):

    if(category is not None):
        groupName = category.name

    operationsByDay, operationsByWeek, operationsByMonth = getBins(
        minDate, maxDate, 0)

    # fill bins (group by day, week, month)
    for op in similarOperations:
        # datetime.datetime.strptime('2019-01-04T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
        dt = datetime.datetime.strptime(
            op.when, "%Y-%m-%dT%H:%M:%S%z")

        ymd = dt.strftime("%Y-%m-%d")
        yw = dt.strftime("%Y-%W")
        ym = dt.strftime("%Y-%m")

        # if ymd in operationsByDay:
        operationsByDay[ymd] += (op.value)
        # if yw in operationsByWeek:
        operationsByWeek[yw] += (op.value)
        # if ym in operationsByMonth:
        operationsByMonth[ym] += (op.value)

    d = []
    w = []
    m = []
    for item in operationsByDay:
        d.append((operationsByDay[item]))
    for item in operationsByWeek:
        w.append((operationsByWeek[item]))
    for item in operationsByMonth:
        m.append((operationsByMonth[item]))

    # using weightedCoefficientOfVariation so that more recent operations will be more important
    min = 0.25
    max = 2

    daily_avg, daily_std, daily_cv = weighted_avg_std_coefficientOfVariation(
        d, min, max)

    weekly_avg, weekly_std, weekly_cv = weighted_avg_std_coefficientOfVariation(
        w, min, max)

    monthly_avg, monthly_std, monthly_cv = weighted_avg_std_coefficientOfVariation(
        m, min, max)

    # if any cv below maxCv
    if(daily_cv < maxCv or weekly_cv < maxCv or monthly_cv < maxCv):

        value = 0
        cv = 0
        schedule = None

        if(daily_cv < maxCv and daily_cv < weekly_cv and daily_cv < monthly_cv):
            cv = daily_cv
            value = daily_avg
            schedule = templateSchedules['daily']

        elif(weekly_cv < maxCv and weekly_cv < daily_cv and weekly_cv < monthly_cv):
            cv = weekly_cv
            value = weekly_avg
            schedule = templateSchedules['weekly']

        elif(monthly_cv < maxCv and monthly_cv < weekly_cv and monthly_cv < daily_cv):
            cv = monthly_cv
            value = monthly_avg
            schedule = templateSchedules['monthly']
        else:
            # too much variation in values
            return None

        # skip if value too low
        if(abs(value) < minValue):
            #print('skip bc value too low')
            return None
            # continue

        newScheduledOp = ScheduledOperation(id=None, user_id=user_id, value=value, name=groupName,
                                            schedule_id=None, schedule=schedule, active=True, hidden=False, category=category)

        newScheduledOp.cv = cv
        newScheduledOp.n = len(similarOperations)

        # check as already analyzed, (not sure if necessary now)

        for op in similarOperations:
            op.analyzed = True
            op.scheduled_operation = newScheduledOp  # pbbly not what i want

        # scheduledOperationsToAdd.append(newScheduledOp)
        return newScheduledOp

    else:
        return None


def analyzeByCategory(analyzedOperations, operationsLeftToAnalyze, categories, minNumberOfOperationsInCategory=5, maxCv=1.0, minValue=5.0):
    generatedScheduledOperations = []
    for category in categories:
        if(category.analyzed):
            continue

        operationsOfCategory = []
        # gert operations of this category
        for op in operationsLeftToAnalyze:
            if(op.analyzed or op.skipped):
                continue
            if(op.category == category):
                operationsOfCategory.append(op)

        if(operationsOfCategory.__len__() >= minNumberOfOperationsInCategory):

            newScheduledOp = tryToGenerateScheduledOperationFromSimilarOperations(
                operationsOfCategory, minDate, maxDate, templateSchedules, currentUserId, groupName=None, category=category, maxCv=maxCv, minValue=minValue)

            if(newScheduledOp is not None):
                category.analyzed = True

                for op in operationsOfCategory:

                    # remove operation from operationsLeftToAnalyze
                    operationsLeftToAnalyze.remove(op)

                    op.analyzed = True
                    op.scheduled_operation = newScheduledOp  # pbbly not what i want
                    # add operation to analyzedOperations
                    analyzedOperations.append(op)

                generatedScheduledOperations.append(newScheduledOp)

    return generatedScheduledOperations


def analyzeByName(analyzedOperations, operationsLeftToAnalyze, minNumberOfOperationsWithSimilarName=5, maxCv=1.0, minValue=5.0, nameSimilarityThreshold=0.75):
    generatedScheduledOperations = []
    for op in operationsLeftToAnalyze:

        # if not analyzed before
        if(op.analyzed or op.skipped):
            continue

        operationsSimilarByName = [op]

        for op2 in operationsLeftToAnalyze:
            if(op == op2):
                continue

            # check how similar are names of operations
            if(similar(op.name, op2.name) >= nameSimilarityThreshold):
                operationsSimilarByName.append(op2)

        if(operationsSimilarByName.__len__() > minNumberOfOperationsWithSimilarName):
            #print(" === %s ===" % op.name)

            newScheduledOp = tryToGenerateScheduledOperationFromSimilarOperations(
                operationsSimilarByName, minDate, maxDate, templateSchedules, currentUserId, cleanOperationName(op.name), None, maxCv, minValue)

            if(newScheduledOp is not None):
                for op in operationsSimilarByName:
                    # remove operation from operationsLeftToAnalyze
                    operationsLeftToAnalyze.remove(op)

                    op.analyzed = True
                    op.scheduled_operation = newScheduledOp
                    # add operation to analyzedOperations
                    analyzedOperations.append(op)

                generatedScheduledOperations.append(newScheduledOp)
            else:
                for op in operationsSimilarByName:
                    op.skipped = True

    for op in operationsLeftToAnalyze:
        op.skipped = False

    return generatedScheduledOperations


def parseMBankCsvDataIntoModel(filePath):

    # read from file
    file = filePath

    # specific for mbank lista operacji
    linesToSkip = 25
    parsed = pd.read_csv(file, sep=';', encoding='cp1250', skip_blank_lines=False,
                         skiprows=linesToSkip, header=0, index_col=False, decimal=",")

    #existingOperations = []
    existingCategories = []

    operationsToAdd = []
    operationsLeftToAnalyze = []  # will shrink during analysis

    categoriesToAdd = []
    scheduledOperationsToAdd = []

    # find columns that we are interested in (from model)
    whenColumnIndex = None
    valueColumnIndex = None
    nameColumnIndex = None
    categoryNameColumnIndex = None

    for i, c in enumerate(parsed.columns):
        # again, specific for mbank
        if(c.lower().__contains__("data") and whenColumnIndex is None):
            whenColumnIndex = i
        elif(c.lower().__contains__("kwota") and valueColumnIndex is None):
            valueColumnIndex = i
        elif(c.lower().__contains__("opis") and nameColumnIndex is None):
            nameColumnIndex = i
        elif(c.lower().__contains__("kategoria") and categoryNameColumnIndex is None):
            categoryNameColumnIndex = i

    # create categories
    for x in parsed.values:
        categoryNameRaw = x[categoryNameColumnIndex]
        if(isinstance(categoryNameRaw, str) == False):
            continue
        # check if category with this name alredy exists
        exists = False
        for category in existingCategories:
            if(category.name == categoryNameRaw):
                exists = True
                break

        for category in categoriesToAdd:
            if(category.name == categoryNameRaw):
                exists = True
                break

        if(exists == False):

            # if not then add new
            newCategory = Category(
                id=None, user_id=currentUserId, name=categoryNameRaw)
            categoriesToAdd.append(newCategory)

    # mbank specific, delete category 'Bez kategorii'
    categoriesToAdd = [cat for cat in categoriesToAdd if not (
        similar(cat.name, 'bez kategorii') >= 0.9)]

    # keep track of lowest and highest date in rows
    minDate = None
    maxDate = None
    # create operations
    for x in parsed.values:
        id = None
        nameRaw = x[nameColumnIndex]
        valueRaw = x[valueColumnIndex]
        whenRaw = x[whenColumnIndex]
        categoryNameRaw = x[categoryNameColumnIndex]

        if(isinstance(nameRaw, str) == False):
            continue
        if(isinstance(valueRaw, str) == False):
            continue
        if(isinstance(whenRaw, str) == False):
            continue

        try:
            # mbank specific, after double spaces is usually address (which is useless for us)

            name = nameRaw.split("  ")[0]

            # parse value, specific for mbank
            valueRaw = valueRaw.replace(" ", "")
            value = float(re.findall(
                r'[-]?[0-9]*[.,]?[0-9]+', valueRaw)[0].replace(",", "."))

            # assume middle of day, specific for mbank
            when = whenRaw + 'T12:00:00+0000'
            #dt = datetime.datetime.strptime(when, "%Y-%m-%dT%H:%M:%S%z")

            # keep track of lowest and highest date in rows
            if(minDate is None):
                minDate = when
            elif(when < minDate):
                minDate = when

            if(maxDate is None):
                maxDate = when
            elif(when > maxDate):
                maxDate = when

            # find category
            category_id = None
            operationCategory = None
            for category in categoriesToAdd:
                if(category.name == categoryNameRaw):
                    category_id = category.id
                    operationCategory = category
                    break
            if(operationCategory is None):
                for category in existingCategories:
                    if(category.name == categoryNameRaw):
                        category_id = category.id
                        operationCategory = category
                        break

            # category_id = None

            parsedOperation = Operation(id=id, user_id=currentUserId, name=name,
                                        value=value, when=when, category_id=category_id, category=operationCategory)

            # adding to both lists at once, since it seems easier then to try and later deep copy list
            operationsToAdd.append(parsedOperation)
            operationsLeftToAnalyze.append(parsedOperation)
        except:
            # error while parsing, pbbly empty row or something
            pass
            #print('skipping ' + str(x))

    minDate = datetime.datetime.strptime(
        minDate, "%Y-%m-%dT%H:%M:%S%z")
    maxDate = datetime.datetime.strptime(
        maxDate, "%Y-%m-%dT%H:%M:%S%z")

    #print(f'operations to add and analyze = {operationsToAdd.__len__()}')

    return minDate, maxDate, operationsToAdd, operationsLeftToAnalyze, categoriesToAdd


currentUserId = None

parse_start = time.time()

minDate, maxDate, operationsToAdd, operationsLeftToAnalyze, categoriesToAdd = parseMBankCsvDataIntoModel(
    'tmp\\lista_operacji.csv')

parse_end = time.time()
print(f'parsing time : {parse_end - parse_start:.3f}s')


# ========================================================================
# =================             analysis                ==================
# ========================================================================
#

scheduledOperationsToAdd = []

dailySchedule = Schedule(id=None, user_id=currentUserId, year=[], month=[
], day_of_month=[], day_of_week=[])
weeklySchedule = Schedule(id=None, user_id=currentUserId, year=[], month=[
], day_of_month=[], day_of_week=[6])
monthlySchedule = Schedule(id=None, user_id=currentUserId, year=[], month=[
], day_of_month=[1], day_of_week=[])
templateSchedules = {'daily': dailySchedule,
                     'weekly': weeklySchedule, 'monthly': monthlySchedule}

# find recurring operations
maxCvRange = [0.65, 0.85, 1.15, 1.55, 2.5]
minValue = 5.0

analyzedOperations = []

for cv in maxCvRange:
    iteration_start = time.time()

    # by category
    newByCategory = analyzeByCategory(analyzedOperations, operationsLeftToAnalyze, categoriesToAdd,
                                      minNumberOfOperationsInCategory=3, maxCv=cv, minValue=minValue)

    # by similar name
    newByName = analyzeByName(analyzedOperations, operationsLeftToAnalyze, minNumberOfOperationsWithSimilarName=3,
                              maxCv=cv, minValue=minValue, nameSimilarityThreshold=0.75)

    scheduledOperationsToAdd.extend(newByCategory)
    scheduledOperationsToAdd.extend(newByName)
    iteration_end = time.time()
    print(f"> maxCv:{cv:.3f} minValue:{minValue:.1f} newByCategory:{newByCategory.__len__()}, newByName:{newByName.__len__()}; a:{analyzedOperations.__len__()} l:{operationsLeftToAnalyze.__len__()} t:{iteration_end - iteration_start:.3f}s")

# generate scheduled operation from all other operations
scheduledOperationFromOthers = tryToGenerateScheduledOperationFromSimilarOperations(
    operationsLeftToAnalyze, minDate, maxDate, templateSchedules, currentUserId, 'Others', None, 999999, 0)

scheduledOperationsToAdd.append(scheduledOperationFromOthers)

for op in operationsLeftToAnalyze:

    op.analyzed = True
    op.scheduled_operation = scheduledOperationFromOthers


# maybe join similar groups
end = time.time()
print(f"time elapsed : {end - start:.3f}s")

print(
    f' === categorized operations : {100*(len(analyzedOperations) / len(operationsToAdd)):.2f}% === ')


print('scheduled operations to add : ')
for sop in scheduledOperationsToAdd:
    print(f"{sop!r} {sop.schedule!r}")

print('categories to add : ')
print(categoriesToAdd.__len__())

print('ALL operations to add : ')
print(operationsToAdd.__len__())

# print('analyzedoOperations : ')
# print(analyzedOperations.__len__())

# print('other operations : ')
# print(operationsLeftToAnalyze.__len__())


print('done')
