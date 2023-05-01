import random

# 设置资源数量和任务数量
n_resources = 20
n_tasks = 30

# 生成随机资源
def random_resources(n_resources):
    data = []

    cpu_range = (4 / 4, 192 / 4)
    memory_range = (16 / 16, 2048 / 16)
    tdp_range = (65 / 5, 3000 / 5)

    for i in range(n_resources):
        cpu = random.randint(*cpu_range) * 4   # 在cpu_range范围内随机生成cpu值
        memory = random.randint(*memory_range) * 16   # 在memory_range范围内随机生成memory值
        tdp = random.randint(*tdp_range) * 5    # 在tdp_range范围内随机生成tdp值
        
        data.append({
            "id": i,
            "cpu": cpu,
            "memory": memory,
            "tdp": tdp
        })
    print(data)
    return data

# 生成随机作业
def random_tasks(n_tasks):
    data = []

    cpu_req_range = (4 / 4, 192 / 24)
    memory_req_range = (16 / 16, 2048 / 64)

    for i in range(n_tasks):
        cpu = random.randint(*cpu_req_range)   # 在cpu_range范围内随机生成cpu值
        memory = random.randint(*memory_req_range)   # 在memory_range范围内随机生成memory值
        
        data.append({
            "id": i,
            "cpu_req": cpu,
            "memory_req": memory,
        })
    print(data)
    return data

# 基础功耗
base_power = 30

# 最大允许cpu使用率
max_cpu_use = 1

#最大允许内存使用率
max_mem_use = 1

'''
base_power = input("设置单服务器基础功耗：")
max_cpu_use = input("设置单服务器最高cpu使用率：")
max_mem_use = input("设置单服务器最高内存使用率：")
'''

resources = random_resources(n_resources)
tasks = random_tasks(n_tasks)

'''
# 资源列表
resources = [
    {"id": 1, "cpu": 4, "memory": 6, "tdp": 65},
    {"id": 2, "cpu": 4, "memory": 8, "tdp": 75},
    {"id": 3, "cpu": 6, "memory": 12, "tdp": 105}
]

# 任务列表 
tasks = [
    {"id": 1, "cpu_req": 3, "memory_req": 6},
    {"id": 2, "cpu_req": 4, "memory_req": 8},
    {"id": 3, "cpu_req": 2, "memory_req": 6} 
]
'''
