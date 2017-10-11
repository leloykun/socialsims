import time
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np
import math


def do_linear_regression(X, Y):
    print("Linear Regression (start):")
    
    lin_reg = LinearRegression(n_jobs=-1)
    lin_reg.fit(X, Y)

    print("  " + str(round(lin_reg.intercept_, 3)) + " + " +
                 str(round(lin_reg.coef_[0], 3)) + "*step + " +
                 str(round(lin_reg.coef_[1], 3)) + "*depth + " +
                 str(round(lin_reg.coef_[2], 3)) + "*alpha + " +
                 str(round(lin_reg.coef_[3], 3)) + "*gamma")

    print("  R-squared:", str(round(lin_reg.score(X, Y), 4)))
    print("Linear Regression (end)")
    print("\n")


def do_logistic_regression(X, Y):
    print("Logistic Regression (start):")

    print(len(X))
    log_reg = LogisticRegression(C=1e7,
                                 tol=1e-5,
                                 max_iter=100,
                                 class_weight='balanced')
    log_reg.fit(X, Y)
    print()

    with open('data/coef.txt', 'w') as f:
        f.write('\n'.join(' '.join(map(str, line))
                          for line in log_reg.coef_))
    with open('data/intercept.txt', 'w') as f:
        f.write(' '.join(map(str, log_reg.intercept_)))
    with open('data/r-squared.txt', 'w') as f:
        f.write(str(log_reg.score(X, Y)))

    print("  R-squared:", round(log_reg.score(X, Y), 4))
    X_test = [[1, 0, 0, 0],
              [0, 1, 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1],
              [100, 1, 0.5, 0.5]]
    Y_test = log_reg.predict(X_test)
    print(Y_test)
    print("Logistic Regression (end):")
    print("\n")


def do_polynomial_regression(X, Y, degree):
    print("Polynomial Regression (start):")

    poly = PolynomialFeatures(degree=degree)
    X_test = [[2, 3, 5, 7]]
    print("  X's original structure:", ' '.join(map(str, X_test[0])))
    Y_test = poly.fit_transform(X_test)
    Y_test = map(int, Y_test[0])
    print("  X's polynomial structure:", ' '.join(map(str, Y_test)))
    print()

    model = Pipeline([('poly', PolynomialFeatures(degree=degree)),
                     ('linear', LinearRegression(fit_intercept=False))])
    model = model.fit(X, Y)
    coefs = model.named_steps['linear'].coef_
    print("  coefs:", coefs)
    print()

    a = math.sqrt(coefs[0])
    b = coefs[1] / (2 * a)
    c = coefs[2] / (2 * a)
    d = coefs[3] / (2 * a)
    e = coefs[4] / (2 * a)

    print("  perf = (" + str(round(a, 3)) + " + " +
                       str(round(b, 3)) + "*step + " +
                       str(round(c, 3)) + "*depth + " +
                       str(round(d, 3)) + "*alpha + " +
                       str(round(e, 3)) + "*gamma) ^ 2")

    print("  R-squared:", round(model.score(X, Y), 4))
    print("Polynomial Regression (end):")
    print("\n")


def analyze(trials=100, steps=10, runs=10):  # pragma: no cover
    start = time.time()

    X = []
    Y = []

    X_temp = {}

    for depth in range(1, 5):
        for run in range(1, runs + 1):
            with open("data/" + str(depth) + "/data" + str(run) + ".txt") as f:
                for line in f.readlines():
                    line = list(map(int, line.split()))
                    for i in range(2, 12):
                        temp = ((i - 1) * steps,
                                depth,
                                line[0] / 10,
                                line[1] / 10)
                        if temp in X_temp:
                            X_temp[temp] += line[i]
                        else:
                            X_temp[temp] = line[i]

    for key in X_temp:
        X.append(list(key))
        Y.append(int(X_temp[key] / 10))

    do_linear_regression(X, Y)
    # do_logistic_regression(X, Y)
    do_polynomial_regression(X, Y, 2)

    print("run time:", time.time() - start, "secs")


if __name__ == '__main__':  # pragma: no cover
    analyze()
