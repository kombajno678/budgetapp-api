# from logging import error
# import os
# from werkzeug.utils import secure_filename
import re
from models.Schedule import Schedule
from models.ScheduledOperation import ScheduledOperation
from models.Operation import Operation
from models.Category import Category
from os import replace
import pandas as pd
import numpy as np
import datetime
from difflib import SequenceMatcher

import time

start = time.time()


# from flask import Flask, request, jsonify, render_template, _request_ctx_stack, url_for
# from flask_cors import cross_origin

# from middleware.tokenAuth import AuthError, requires_auth
# from app import create_app, db, api, migrate
# from endpoints import routes


def similar(a, b):
    toIgnore = [
        's.a.',
        '.pl',
        'www.',
        'sp.zo.o.',
    ]
    a_ = a.lower().replace(" ", "")
    b_ = b.lower().replace(" ", "")

    a_ = re.sub('\d', '', a_)
    b_ = re.sub('\d', '', b_)

    for s in toIgnore:
        a_ = a_.replace(s, "")
        b_ = b_.replace(s, "")

    return SequenceMatcher(None, a_, b_).ratio()
    #isjunk = lambda x: x == " "


def daterange(start_date, end_date):
    for n in range(1 + int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


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

    daily_cv = np.std(d) / abs(np.average(d))
    weekly_cv = np.std(w) / abs(np.average(w))
    monthly_cv = np.std(m) / abs(np.average(m))

    # if any cv below maxCv
    if(daily_cv < maxCv or weekly_cv < maxCv or monthly_cv < maxCv):

        value = 0
        schedule = None

        if(daily_cv < maxCv and daily_cv < weekly_cv and daily_cv < monthly_cv):
            value = np.average(d)
            schedule = templateSchedules['daily']

        elif(weekly_cv < maxCv and weekly_cv < daily_cv and weekly_cv < monthly_cv):
            value = np.average(w)
            schedule = templateSchedules['weekly']

        elif(monthly_cv < maxCv and monthly_cv < weekly_cv and monthly_cv < daily_cv):
            value = np.average(m)
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

        # check as already analyzed, (not sure if necessary now)
        for op in similarOperations:
            op.analyzed = True
            op.scheduled_operation = newScheduledOp  # pbbly not what i want

        # scheduledOperationsToAdd.append(newScheduledOp)
        return newScheduledOp


currentUserId = None


# read from file
file = 'tmp\\lista_operacji.csv'
linesToSkip = 25
parsed = pd.read_csv(file, sep=';', encoding='cp1250', skip_blank_lines=False,
                     skiprows=linesToSkip, header=0, index_col=False, decimal=",")

# fit data to models
# =====================================================================
# ============================== preprocessing ========================
# =====================================================================
existingOperations = []
existingCategories = []

operationsToAdd = []
categoriesToAdd = []
scheduledOperationsToAdd = []

whenColumnIndex = 0
valueColumnIndex = 0
nameColumnIndex = 0
categoryNameColumnIndex = 0
i = 0
for c in parsed.columns:

    # print(str(c))

    if(c.lower().__contains__("data")):
        whenColumnIndex = i
    if(c.lower().__contains__("kwota")):
        valueColumnIndex = i
    if(c.lower().__contains__("opis")):
        nameColumnIndex = i
    if(c.lower().__contains__("kategoria")):
        categoryNameColumnIndex = i

    i += 1


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

# add new categories, so they
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

        name = nameRaw.split("  ")[0]  # + '(' + str(categoryNameRaw) + ')'

        valueRaw = valueRaw.replace(" ", "")
        value = float(re.findall(
            r'[-]?[0-9]*[.,]?[0-9]+', valueRaw)[0].replace(",", "."))

        when = whenRaw + 'T12:00:00+0000'
        dt = datetime.datetime.strptime(when, "%Y-%m-%dT%H:%M:%S%z")

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

        temp = Operation(id=id, user_id=currentUserId, name=name,
                         value=value, when=when, category_id=category_id, category=operationCategory)
        operationsToAdd.append(temp)
        # print(str(temp))
    except:
        print('skipping ' + str(x))

minDate = datetime.datetime.strptime(
    minDate, "%Y-%m-%dT%H:%M:%S%z")
maxDate = datetime.datetime.strptime(
    maxDate, "%Y-%m-%dT%H:%M:%S%z")

print('operationsToAdd = ' + str(operationsToAdd.__len__()))


# ========================================================================
# =================             analysis                ==================
# ========================================================================
#

maxCv = 1.5
minValue = 3.0

dailySchedule = Schedule(id=None, user_id=currentUserId, year=[], month=[
], day_of_month=[], day_of_week=[])
weeklySchedule = Schedule(id=None, user_id=currentUserId, year=[], month=[
], day_of_month=[], day_of_week=[6])
monthlySchedule = Schedule(id=None, user_id=currentUserId, year=[], month=[
], day_of_month=[1], day_of_week=[])
templateSchedules = {'daily': dailySchedule,
                     'weekly': weeklySchedule, 'monthly': monthlySchedule}

# find recurring operations
# by category

for category in categoriesToAdd:

    operationsOfCategory = []
    operationValues = []
    operationDates = []
    # gert operations of this category
    for op in operationsToAdd:
        if(op.category == category):
            operationsOfCategory.append(op)
            operationValues.append(op.value)
            operationDates.append(op.when)

    if(operationsOfCategory.__len__() > 5):

        newScheduledOp = tryToGenerateScheduledOperationFromSimilarOperations(
            operationsOfCategory, minDate, maxDate, templateSchedules, currentUserId, None, category, maxCv, minValue)

        if(newScheduledOp is not None):
            for op in operationsOfCategory:
                op.analyzed = True
                op.scheduled_operation = newScheduledOp  # pbbly not what i want

            scheduledOperationsToAdd.append(newScheduledOp)

# by similar name
for op in operationsToAdd:

    # if not analyzed before
    if(op.analyzed or op.skipped):
        continue

    similarByName = []
    #similarByNameValues = []

    similarByName.append(op)
    # similarByNameValues.append(op.value)

    for op2 in operationsToAdd:
        if(op == op2):
            continue

        # check how similar are names of operations
        similarity = similar(op.name, op2.name)
        if(similarity > 0.75):
            similarByName.append(op2)
            # similarByNameValues.append(op2.value)

    if(similarByName.__len__() > 5):
        #print(" === %s ===" % op.name)

        newScheduledOp = tryToGenerateScheduledOperationFromSimilarOperations(
            similarByName, minDate, maxDate, templateSchedules, currentUserId, op.name, None, maxCv, minValue)

        if(newScheduledOp is not None):
            for op in similarByName:
                op.analyzed = True
                op.scheduled_operation = newScheduledOp  # pbbly not what i want
            scheduledOperationsToAdd.append(newScheduledOp)
        else:
            for op in similarByName:
                op.skipped = True

# generate scheduled operation from all other operations
otherOperations = []
for op in operationsToAdd:
    if(op.analyzed == False):
        otherOperations.append(op)

scheduledOperationsFromOthers = tryToGenerateScheduledOperationFromSimilarOperations(
    otherOperations, minDate, maxDate, templateSchedules, currentUserId, 'Others', None, 999999, 0)

scheduledOperationsToAdd.append(scheduledOperationsFromOthers)
# maybe join similar groups
end = time.time()
print("time elapled : %8.2fs" % (end - start))

print('operations to add : ')
print(operationsToAdd.__len__())
# for op in operationsToAdd:
#    print(op)

print('scheduled operations to add : ')
for sop in scheduledOperationsToAdd:
    print(sop)

print('categories to add : ')
print(categoriesToAdd.__len__())
# for cat in categoriesToAdd:
#    print(cat)
print('done')
