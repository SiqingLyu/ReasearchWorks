import numpy as np
from pymoo.core.problem import ElementwiseProblem, Problem  # 两者区别是是否要得到单一解
from pymoo.core.sampling import Sampling
from pymoo.core.mutation import Mutation
from pymoo.core.crossover import Crossover
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.algorithms.soo.nonconvex.ga import GA
from typing import List, Tuple, Dict


class OrbitProblem(ElementwiseProblem):
    def __init__(self, **kwargs):
        super().__init__(n_var=4, n_obj=3, n_ieq_constr=9, n_eq_constr=0,
                         xl=np.array([0, 0, 0, 0]), xu=np.array([1, 24, 24, 90]), **kwargs)

    def object_max_profit(self, x):

        y = """此处输入的x需要做二值化，也可结合constr_one_observe设置x为int"""
        return -y

    def object_min_load(self, x):
        y = """"""
        return y

    def object_max_neighbors(self, x):
        y = """"""
        return -y

    def constr_one_observe(self, x):
        y = """"""
        return y

    def constr_change_time(self, x):
        y = """"""
        return y

    def constr_inside_window(self, x):
        y1, y2 = """"""
        return y1, y2

    def constr_compos_time(self, x):
        y = """"""
        return y

    def constr_compos_angle(self, x):
        y = """"""
        return y

    def constr_round_max_time(self, x):
        y = """"""
        return y

    def constr_max_space(self, x):
        y = """"""
        return y

    def constr_max_energy(self, x):
        y = """"""
        return y

    def _evaluate(self, x, out, *args, **kwargs):

        # 定义目标函数
        f1 = self.object_max_profit(x)
        f2 = self.object_min_load(x)
        f3 = self.object_max_neighbors(x)
        # 定义约束条件
        g1 = self.constr_one_observe(x)
        g2 = self.constr_change_time(x)
        g3_1, g3_2 = self.constr_inside_window(x)
        g4 = self.constr_compos_time(x)
        g5 = self.constr_compos_angle(x)
        g6 = self.constr_round_max_time(x)
        g7 = self.constr_max_space(x)
        g8 = self.constr_max_energy(x)

        out["F"] = np.column_stack([f1, f2, f3])
        out["G"] = np.column_stack([g1, g2, g3_1, g3_2, g4, g5, g6, g7, g8])


class MySampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, problem.n_var), False, dtype=bool)

        for k in range(n_samples):
            I = np.random.permutation(problem.n_var)[:problem.n_max]
            X[k, I] = True

        return X


class BinaryCrossover(Crossover):
    def __init__(self):
        super().__init__(2, 1)

    def _do(self, problem, X, **kwargs):
        n_parents, n_matings, n_var = X.shape

        _X = np.full((self.n_offsprings, n_matings, problem.n_var), False)

        for k in range(n_matings):
            p1, p2 = X[0, k], X[1, k]

            both_are_true = np.logical_and(p1, p2)
            _X[0, k, both_are_true] = True

            n_remaining = problem.n_max - np.sum(both_are_true)

            I = np.where(np.logical_xor(p1, p2))[0]

            S = I[np.random.permutation(len(I))][:n_remaining]
            _X[0, k, S] = True

        return _X


class MyMutation(Mutation):
    def _do(self, problem, X, **kwargs):
        for i in range(X.shape[0]):
            X[i, :] = X[i, :]
            is_false = np.where(np.logical_not(X[i, :]))[0]
            is_true = np.where(X[i, :])[0]
            X[i, np.random.choice(is_false)] = True
            X[i, np.random.choice(is_true)] = False

        return X


class MyNSGAII:
    def __init__(self, problems: Problem = None):
        self.problems = problems
        self.algorithm = None
        return

    def get_problems(self):
        return self.problems

    def def_problems(self, problems):
        self.problems = problems

    def def_algorithm(self, pop_size: int = 500, sampling=BinaryRandomSampling(),
                      crossover=TwoPointCrossover(), mutation=BitflipMutation(),
                      eliminate=True):
        self.algorithm = NSGA2(
            pop_size=pop_size,
            sampling=sampling,
            crossover=crossover,
            mutation=mutation,
            eliminate_duplicates=eliminate)

    def nsga2(self, pop_size: int = 100):
        res = minimize(self.problems, self.algorithm)


if __name__ == '__main__':
    pass
