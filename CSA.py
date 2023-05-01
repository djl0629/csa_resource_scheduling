import random
import numpy as np
import scipy.special as special
import sys
from env_variable import *
import matplotlib.pyplot as plt

# 目标函数(功耗)
def objective(solution):
    # 初始化功耗以及违约次数
    total_power = 0
    constraint_violation = 0
    for i in range(len(resources)):
        # 初始化单个资源的cpu使用以及功耗
        cpu_use = 0
        mem_use = 0
        single_power = 0
        for j in range(len(solution)):
            if solution[j] == i:
                cpu_use += tasks[j]["cpu_req"]
                if cpu_use > resources[i]["cpu"] * max_cpu_use:
                    constraint_violation += 1
                mem_use += tasks[j]["memory_req"]
                if mem_use > resources[i]["memory"] * max_mem_use:
                    constraint_violation += 1
        if cpu_use > 0:
            # 如果该资源有任务分配，则增加基础功耗
            single_power += base_power
            # 计算cpu使用率
            cpu_util = cpu_use / resources[i]["cpu"]
            # 实时功耗 = cpu使用 / cpu资源量 * tdp
            single_power += cpu_util * resources[i]["tdp"]
            total_power += single_power
            # 计算内存使用率
            mem_util = mem_use / resources[i]["memory"]
            # 添加约束判断和惩罚项
            if cpu_util > max_cpu_use:
                constraint_violation += 1
            if mem_util > max_mem_use:
                constraint_violation += 1
            
    # 计算惩罚值对结果的影响
    objective_value = total_power + constraint_violation * 2000

    return objective_value

# 寻找最佳适应度巢穴下标
def select_best(nest):
    best_obj = sys.maxsize
    for i in range(len(nest)):
        new_obj = objective(nest[i])
        if best_obj > new_obj:
            best_obj = new_obj
            best_index = i
    return best_index

# 求种群适应度平均值
def obj_avg(nest, n_nest):
    total_obj = 0
    for solution in nest:
        total_obj += objective(solution)
    obj_avg = total_obj / n_nest
    return obj_avg

# levy飞行生成新解
def levy_fly(best, iter, max_iter):
    # 莱维分布参数
    beta = 1.5
    # levy飞行基础步长
    alpha_init = 0.4
    # levy飞行最小步长
    alpha_min = 0.2
    # 自适应步长缩放和上下限
    lb = 0
    ub = len(resources) - 1
    alpha_range = alpha_init - alpha_min
    alpha = alpha_min + alpha_range * (1 - iter / max_iter)
    alpha_scaled = alpha * (ub - lb)

    # 维度
    best_np = np.array(best)
    size = best_np.shape
    # 计算levy随机步长
    sigma_u = (special.gamma(1 + beta) * np.sin(np.pi * beta / 2) / (special.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    u = np.random.normal(0, sigma_u, size)
    v = np.random.normal(0, 1, size)
    levy_step = u / np.abs(v) ** (1 / beta)

    # 生成新解
    new_solution = best_np + alpha_scaled * levy_step

    print('新解：', new_solution)
    
    # 四舍五入并将新解重新映射到指定范围内
    new_solution = np.round(new_solution).astype(int)
    new_solution = lb + (new_solution - lb) % (ub - lb + 1)

    return new_solution.tolist()

# 超支检测
def check(solution):
    cpu_over = 0
    mem_over = 0
    for i in range(len(resources)):
        # 初始化单个资源的cpu使用以及功耗
        cpu_use = 0
        mem_use = 0
        for j in range(len(solution)):
            if solution[j] == i:
                cpu_use += tasks[j]["cpu_req"]
                mem_use += tasks[j]["memory_req"]
        # 计算cpu使用率
        cpu_util = cpu_use / resources[i]["cpu"]
        # 所分配任务cpu需求总和大于设定上限，标记为超支
        if cpu_util > max_cpu_use:
            cpu_over = 1
        # 计算内存使用率
        mem_util = mem_use / resources[i]["memory"]
        # 所分配任务memory需求总和大于设定上限，标记为超支
        if mem_util > max_mem_use:
            mem_over = 1
    if cpu_over == 1:
        print("超支，任务分配失败，需要更多cpu资源！")
    if mem_over == 1:
        print("超支，任务分配失败，需要更多memory资源！")
    if cpu_over + mem_over > 0:
        return 0
    else:
        return 1


# 主函数
def cuckoo_search():

    # 最大迭代次数
    max_iter = 300

    # 巢穴数量
    n_nest = 20

    # 随机生成种群
    nest = []
    for i in range(n_nest):
        solution = []
        for j in range(len(tasks)):
            solution.append(random.choice(range(len(resources))))
            if j == len(tasks) - 1:
                nest.append(solution)

    # 寻找最佳巢穴
    best_index = select_best(nest)
    best = nest[best_index][:]
    best_obj = objective(best)

    for iter in range(max_iter):
        x_iter.append(iter + 1)
        y_obj_avg.append(obj_avg(nest, n_nest))
        y_obj_best.append(best_obj)
        print("开始第", iter + 1, "轮迭代！")
        # levy飞行
        for i in range(n_nest):
            # 以最佳巢穴为初始值进行levy飞行生成新解
            new_solution = levy_fly(best, iter, max_iter)[:]
            new_obj = objective(new_solution)

            # 随机选择一个巢穴与新解比较
            x = random.randint(0, n_nest - 1)
            if objective(nest[x]) > new_obj:
                nest[x] = new_solution[:]
                if best_obj > new_obj:
                    best_index = x
                    best = nest[x][:]
                    best_obj = new_obj

        # 生成自适应离巢率
        pa = 0.3 * (1 - iter/max_iter)
        # pa概率被发现
        for i in range(n_nest):
            # 过滤最佳巢穴
            if i != best_index:
                if random.random() <= pa:
                    new_solution = levy_fly(best, iter, max_iter)[:]
                    new_obj = objective(new_solution)
                    nest[i] = new_solution[:]
                    if best_obj > new_obj:
                        best_index = i
                        best = nest[i][:]
                        best_obj = new_obj

        # 打印该轮迭代最佳巢穴
        print("此时最佳巢穴为", best)
        print("此时最佳适应度为：", best_obj, "瓦")
    
    # 收集绘图数据
    x_iter.append(iter + 1)
    y_obj_avg.append(obj_avg(nest, n_nest))
    y_obj_best.append(best_obj)


    return best

# 初始化图形，x轴为种群代数，y轴为适应度的平均值以及最佳适应度
x_iter, y_obj_avg, y_obj_best = [], [], []
best_solution = cuckoo_search()[:] 
if check(best_solution) == 1:
    print("最佳任务分配为", best_solution)
    print("最低功率约为", round(objective(best_solution)), "瓦")
    # 绘制代数-平均适应度折线
    plt.plot(x_iter, y_obj_avg, 'r-')
    # 绘制代数-最佳适应度折线
    plt.plot(x_iter, y_obj_best, 'b-')
    '''
    plt.xlabel('迭代次数')
    plt.ylabel('适应度')
    '''
    # 展示图形
    plt.show()
