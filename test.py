# from logging import error
# import os
# from werkzeug.utils import secure_filename
from os import replace
import pandas as pd
import numpy as np
import datetime
from difflib import SequenceMatcher


# from flask import Flask, request, jsonify, render_template, _request_ctx_stack, url_for
# from flask_cors import cross_origin

# from middleware.tokenAuth import AuthError, requires_auth
from models.Category import Category
from models.Operation import Operation
from models.ScheduledOperation import ScheduledOperation
# from app import create_app, db, api, migrate
# from endpoints import routes

import re


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
    for n in range(int((end_date - start_date).days)):
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


def generateScheduledOperationsFromSimilarOperations(similarOperations):
    print("================================== " + str(cat.name) + ' ' + str(similarOperations.__len__()) +
          " ======================================")

    #print(' === by single operation === ')
    median, avg, var, std, stds, cv = getStatsOfArray(operationValues)

    operationsByDay = {}
    operationsByWeek = {}
    operationsByMonth = {}
    for single_date in daterange(minDate, maxDate):
        ymd = (single_date.strftime("%Y-%m-%d"))
        yw = (single_date.strftime("%Y-%W"))
        ym = (single_date.strftime("%Y-%m"))
        operationsByDay[ymd] = {"operations": [], "value": [], "date": []}
        operationsByWeek[yw] = {"operations": [], "value": [], "date": []}
        operationsByMonth[ym] = {"operations": [], "value": [], "date": []}

    # group by day
    # for each day between minDate and maxDate
    for op in similarOperations:
        # datetime.datetime.strptime('2019-01-04T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
        dt = datetime.datetime.strptime(
            op.when, "%Y-%m-%dT%H:%M:%S%z")
        ymd = dt.strftime("%Y-%m-%d")
        if ymd in operationsByDay:
            # operationsByDay[ymd]["operations"].append(op)
            operationsByDay[ymd]["value"].append(op.value)
            # operationsByDay[ymd]["date"].append(op.when)
        yw = (dt.strftime("%Y-%W"))
        if yw in operationsByWeek:
            # operationsByWeek[yw]["operations"].append(op)
            operationsByWeek[yw]["value"].append(op.value)
            # operationsByWeek[yw]["date"].append(op.when)
        ym = (dt.strftime("%Y-%m"))
        if ym in operationsByMonth:
            # operationsByMonth[ym]["operations"].append(op)
            operationsByMonth[ym]["value"].append(op.value)
            # operationsByMonth[ym]["date"].append(op.when)

    d = []
    for item in operationsByDay:
        d.append(np.sum(operationsByDay[item]["value"]))
    w = []
    for item in operationsByWeek:
        w.append(np.sum(operationsByWeek[item]["value"]))
    m = []
    for item in operationsByMonth:
        m.append(np.sum(operationsByMonth[item]["value"]))

    daily_cv = np.std(d) / abs(np.average(d))
    weekly_cv = np.std(w) / abs(np.average(w))
    monthly_cv = np.std(m) / abs(np.average(m))

    # if any cv below 1
    if(daily_cv < 1 or weekly_cv < 1 or monthly_cv < 1):

        value = 0

        if(daily_cv < 1 and daily_cv < weekly_cv and daily_cv < monthly_cv):
            value = np.average(d)
            print("*** DAILY %8.2f   (%8.2f) for %s ***" %
                  (value, daily_cv, cat.name))
            print(d)
        elif(weekly_cv < 1 and weekly_cv < daily_cv and weekly_cv < monthly_cv):
            value = np.average(w)
            print("*** Weekly %8.2f  (%8.2f) for %s ***" %
                  (value, weekly_cv, cat.name))
            print(w)
        elif(monthly_cv < 1 and monthly_cv < weekly_cv and monthly_cv < daily_cv):
            value = np.average(m)
            print("*** Monthly %8.2f (%8.2f) for %s ***" %
                  (value, monthly_cv, cat.name))
            print(m)

        if(abs(value) < 5):
            print('skip bc value too low')
            return None
            # continue

        newScheduledOp = ScheduledOperation(id=None, user_id=currentUserId, value=value, name=cat.name,
                                            schedule_id=None, active=True, hidden=False, category=cat)

        # check as already analyzed, (not sure if necessary now)
        for op in similarOperations:
            op.analyzed = True
            op.scheduled_operation = newScheduledOp  # pbbly not what i want

        # scheduledOperationsToAdd.append(newScheduledOp)
        return newScheduledOp


currentUserId = None

file = 'tmp\\lista_operacji.csv'
linesToSkip = 25


parsed = pd.read_csv(file, sep=';', encoding='cp1250', skip_blank_lines=False,
                     skiprows=linesToSkip, header=0, index_col=False, decimal=",")


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
# find recurring operations
# first find by category


for cat in categoriesToAdd:

    operationsOfCategory = []
    operationValues = []
    operationDates = []
    for op in operationsToAdd:
        if(op.category == cat):
            operationsOfCategory.append(op)
            operationValues.append(op.value)
            operationDates.append(op.when)

    if(operationsOfCategory.__len__() > 5):
        print("================================== " + str(cat.name) + ' ' + str(operationsOfCategory.__len__()) +
              " ======================================")

        #print(' === by single operation === ')
        median, avg, var, std, stds, cv = getStatsOfArray(operationValues)

        operationsByDay = {}
        operationsByWeek = {}
        operationsByMonth = {}
        for single_date in daterange(minDate, maxDate):
            ymd = (single_date.strftime("%Y-%m-%d"))
            yw = (single_date.strftime("%Y-%W"))
            ym = (single_date.strftime("%Y-%m"))
            operationsByDay[ymd] = {"operations": [], "value": [], "date": []}
            operationsByWeek[yw] = {"operations": [], "value": [], "date": []}
            operationsByMonth[ym] = {"operations": [], "value": [], "date": []}

        # group by day
        # for each day between minDate and maxDate
        for op in operationsOfCategory:
            # datetime.datetime.strptime('2019-01-04T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
            dt = datetime.datetime.strptime(
                op.when, "%Y-%m-%dT%H:%M:%S%z")
            ymd = dt.strftime("%Y-%m-%d")
            if ymd in operationsByDay:
                # operationsByDay[ymd]["operations"].append(op)
                operationsByDay[ymd]["value"].append(op.value)
                # operationsByDay[ymd]["date"].append(op.when)
            yw = (dt.strftime("%Y-%W"))
            if yw in operationsByWeek:
                # operationsByWeek[yw]["operations"].append(op)
                operationsByWeek[yw]["value"].append(op.value)
                # operationsByWeek[yw]["date"].append(op.when)
            ym = (dt.strftime("%Y-%m"))
            if ym in operationsByMonth:
                # operationsByMonth[ym]["operations"].append(op)
                operationsByMonth[ym]["value"].append(op.value)
                # operationsByMonth[ym]["date"].append(op.when)

        d = []
        for item in operationsByDay:
            d.append(np.sum(operationsByDay[item]["value"]))
        w = []
        for item in operationsByWeek:
            w.append(np.sum(operationsByWeek[item]["value"]))
        m = []
        for item in operationsByMonth:
            m.append(np.sum(operationsByMonth[item]["value"]))

        daily_cv = np.std(d) / abs(np.average(d))
        weekly_cv = np.std(w) / abs(np.average(w))
        monthly_cv = np.std(m) / abs(np.average(m))

        # if any cv below 1
        if(daily_cv < 1 or weekly_cv < 1 or monthly_cv < 1):

            value = 0

            if(daily_cv < 1 and daily_cv < weekly_cv and daily_cv < monthly_cv):
                value = np.average(d)
                print("*** DAILY %8.2f   (%8.2f) for %s ***" %
                      (value, daily_cv, cat.name))
                print(d)
            elif(weekly_cv < 1 and weekly_cv < daily_cv and weekly_cv < monthly_cv):
                value = np.average(w)
                print("*** Weekly %8.2f  (%8.2f) for %s ***" %
                      (value, weekly_cv, cat.name))
                print(w)
            elif(monthly_cv < 1 and monthly_cv < weekly_cv and monthly_cv < daily_cv):
                value = np.average(m)
                print("*** Monthly %8.2f (%8.2f) for %s ***" %
                      (value, monthly_cv, cat.name))
                print(m)

            if(abs(value) < 5):
                print('skip bc value too low')
                continue

            newScheduledOp = ScheduledOperation(id=None, user_id=currentUserId, value=value, name=cat.name,
                                                schedule_id=None, active=True, hidden=False, category=cat)

            for op in operationsOfCategory:
                op.analyzed = True
                op.scheduled_operation = newScheduledOp  # pbbly not what i want

            scheduledOperationsToAdd.append(newScheduledOp)


print('scheduledOperationsToAdd')
print(scheduledOperationsToAdd)


# check those that have already been analyzed and assigned scheduled operation
# find operations with same name (in those not analyzed)


# get distinct names of operations
operationsByNames = {}
for op in operationsToAdd:

    # if not analyzed before
    if(op.analyzed):
        continue

    similarByName = []
    similarByNameValues = []

    for op2 in operationsToAdd:
        if(op == op2):
            continue

        similarity = similar(op.name, op2.name)
        if(similarity > 0.75):

            similarByName.append(op2)
            similarByNameValues.append(op2.value)

            #print("%s ~ %s =  %8.2f  " % (op.name, op2.name, similarity))

    if(similarByName.__len__() > 5):
        print(" === %s ===" % op.name)
        median, avg, var, std, stds, cv = getStatsOfArray(similarByNameValues)
        print("  ===  %s ==== cv: %8.2f" % (op.name, cv))
        print(" MED: %8.2f  AVG: %8.2f   VAR: %8.2f   STD: %8.2f   STDs: %8.2f" %
              (median, avg, var, std, stds))
        # print(similarByNameValues)

        for op3 in similarByName:
            op3.analyzed = True
        op.analyzed = True

    '''
    simplifiedName = op.name.lower().replace(" ", "")[0:10]

    if simplifiedName in operationsByNames:
        operationsByNames[simplifiedName].append(op)
    else:
        operationsByNames[simplifiedName] = [op]
    '''


# maybe join similar groups


print(operationsByNames)

# for each distinct name get operations
# do a n a l y z e


'''
for op in operationsToAdd:

    # if not analyzed before
    if(op.analyzed):
        continue

    # get operations with the same name
    group = []
    for op2 in operationsToAdd:
        if(op2.name == op.name):
            group.append(op2)
    # ignore if: much deviation in values, much deviation in delta days (on random days)
    if(group.__len__() >= 5):
        # add scheduled operation
        name = op.name
        sumValue = 0
        for op2 in group:
            sumValue += op2.value
        value = sumValue / group.__len__()  # avg value from group ?, maybe round to 0,1
        schedule = None  # oh fukkk
        # find on avg every x days operation occurs (they are alredy ordered by date)
        temp = ScheduledOperation(id=None, user_id=currentUserId, value=value, name=name,
                                  schedule_id=None, active=True, hidden=False, category_id=op.category_id)
'''
