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


class OrbitProblem(Problem):
    def __init__(self, cost_matrix: list, ):
        self.cost_matrix = cost_matrix
        super().__init__(n_var=2,   # 变量数
                         n_obj=2,   # 目标数
                         n_constr=2,    # 约束数
                         xl=np.array([-2, -2]),     # 变量下界
                         xu=np.array([2, 2]),   # 变量上界
                         )

    def _evaluate(self, x, out, *args, **kwargs):

        # 定义目标函数
        f1 = x[:, 0]**2 + x[:, 1]**2    # x1放在x的第0列，x2放在x的第一列
        f2 = (x[:, 0] - 1)**2 + x[:, 1]**2
        # 定义约束条件
        g1 = 2*(x[:, 0] - 0.1) * (x[:, 0] - 0.9) / 0.18
        g2 = -20*(x[:, 0] - 0.4) * (x[:, 0] - 0.6) / 4.8
        # todo
        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2])


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

    def def_algorithm(self, pop_size: int = 100, sampling=BinaryRandomSampling(),
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
