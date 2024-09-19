'''监测点信息类，包含同类监测点的数据列名列表column_name_list、监测类型monitoring_type、监测点坐标列表coordinates_list'''
import numpy as np


class ViewPoints:
    def __init__(self, column_name_list, monitoring_type, coordinates_list):
        self.column_name_list = column_name_list  # Excel中列名称列表 ['应变16(um/m)','应变15(um/m)'...]
        self.monitoring_type = monitoring_type  # 监测类型  "theta方向应变"
        self.coordinates_list = coordinates_list  # [[r,θ,z],[r,θ,z]...]
        self.data = None    # 监测点数据
        self.toOne_value = 0    #  数据归一化值，+该值 即可变为真实值
        self.predict_time = None    # 预测时间列表
        self.predict_data = None    # 监测点未来预测数据
        self.english_column_name_list = self.get_English_name() if coordinates_list is not None else None    #  英文列名列表， 主要用于Pyvista中的显示（Pyvista不支持中文）
        self.view_model_mesh = None     # 监测点标注模型
        self.break_time_list = None     # 断裂时间列表
        self.break_data_list = None     # 断裂应变列表
        # data
    def display_info(self):
        print(f"Column Name: {self.column_name_list}")
        print(f"Monitoring Type: {self.monitoring_type}")
        print(f"Coordinates (r, theta, z): {self.coordinates_list}")

    def get_English_name(self):
        english_name_list = []
        for column_name in self.column_name_list:
            # 提取括号左边的部分
            english_name = column_name.split('(')[0].replace('应变', 'Strain').replace('温度', 'T')
            english_name_list.append(english_name)
        return np.array(english_name_list)

    # def __str__(self):
    #     return f"ViewPoints(Column Name: {self.column_name_list}, Monitoring Type: {self.monitoring_type}," \
    #            f" Coordinates: {self.coordinates_list}, data: {self.data})\n"
    def __str__(self):
        return f"ViewPoints(Column Name: {self.column_name_list}, Monitoring Type: {self.monitoring_type}," \
            f" Coordinates: {self.coordinates_list}, data: {self.data}, toOne_value: {self.toOne_value}," \
            f" predict_time: {self.predict_time}, predict_data: {self.predict_data}," \
               f" english_name: {self.english_column_name_list})\n"
