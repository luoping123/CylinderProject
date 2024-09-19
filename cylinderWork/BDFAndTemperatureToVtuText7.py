from pyNastran.bdf.bdf import BDF
from pyNastran.op2.op2 import OP2
# noinspection PyUnresolvedReferences
import vtkmodules.all as vtk
import numpy as np
import pandas as pd
import pyvista as pv
from CoordinateTemperatureText3 import get_temperature_from_rz  # 自己的





# # bdf中单元类型对应的 vtk中的单元的类型
ETYPE_MAP_VTKVALUE = {
    # line
    'CDAMP1' : 3,
    'CDAMP2' : 3,
    'CDAMP3' : 3,
    'CDAMP4' : 3,
    'CDAMP5': 3,
    'CELAS1' : 3,
    'CELAS2' : 3,
    'CELAS3' : 3,
    'CELAS4' : 3,
    'CBAR' : 3,
    'CBEAM' : 3,
    'CROD' : 3,
    'CONROD' : 3,
    'CTUBE' : 3,
    'CTRIA3' : 5, # triangle
    'CQUAD' : 9,  # quad
    'CQUAD4' : 9,  # quad
    'CSHEAR' : 9,  # quad
    'CTETRA' : 10,  # tetra
    'CTETRA4': 10,  # tetra
    'CHEXA': 12,  # hexahedron
    'CHEXA8': 12,  # hexahedron
    'CPENTA' : 13, # wedge
    'CPENTA6': 13,  # wedge
    'CPYRAM' : 14,  # pyramid
    'CPYRAM5' : 14,  # pyramid
    # quadratic shell
    'CTRIA6': 22,  # quadratic triangle
    'CQUAD8': 23,  # quadratic quad
    # quadratic solids
    'CTETRA10' : 24,
    'CHEXA20': 25,  # quadratic hexahedron
    'CPENTA15' : 26, # quadratic wedge
    'CPYRAM13' : 27, # quadratic pyramid
}
# bdf中单元类型对应的 vtk中的单元类的实例
ETYPE_MAP_VTKCLASS = {
    # line
    'CDAMP1': vtk.vtkLine(),
    'CDAMP2': vtk.vtkLine(),
    'CDAMP3': vtk.vtkLine(),
    'CDAMP4': vtk.vtkLine(),
    'CDAMP5': vtk.vtkLine(),
    'CELAS1': vtk.vtkLine(),
    'CELAS2': vtk.vtkLine(),
    'CELAS3': vtk.vtkLine(),
    'CELAS4': vtk.vtkLine(),
    'CBAR': vtk.vtkLine(),
    'CBEAM': vtk.vtkLine(),
    'CROD': vtk.vtkLine(),
    'CONROD': vtk.vtkLine(),
    'CTUBE': vtk.vtkLine(),
    'CTRIA3': vtk.vtkTriangle(),  # triangle
    'CQUAD': vtk.vtkQuad(),  # quad
    'CQUAD4': vtk.vtkQuad(),  # quad
    'CSHEAR': vtk.vtkQuad(),  # quad
    'CTETRA': vtk.vtkTetra(),  # tetra
    'CTETRA4': vtk.vtkTetra(),  # tetra
    'CHEXA': vtk.vtkHexahedron(),  # hexahedron
    'CHEXA8': vtk.vtkHexahedron(),  # hexahedron
    'CPENTA': vtk.vtkWedge(),  # wedge
    'CPENTA6': vtk.vtkWedge(),  # wedge
    'CPYRAM': vtk.vtkPyramid(),  # pyramid
    'CPYRAM5': vtk.vtkPyramid(),  # pyramid
    # quadratic shell
    'CTRIA6': vtk.vtkQuadraticTriangle(),  # quadratic triangle
    'CQUAD8': vtk.vtkQuadraticQuad(),  # quadratic quad
    # quadratic solids
    'CTETRA10': vtk.vtkQuadraticTetra(),
    'CHEXA20': vtk.vtkQuadraticHexahedron(),  # quadratic hexahedron
    'CPENTA15': vtk.vtkQuadraticWedge(),  # quadratic wedge
    'CPYRAM13': vtk.vtkQuadraticPyramid(),  # quadratic pyramid
}

# 我们正在分析一个静态问题，所以itime = 0
itime = 0
# 我们还假设子情况1
isubcase = 1

class VtuModel:

    def __init__(self):
        cylinderStructured = pv.CylinderStructured(radius=np.linspace(0, 55, 100), height=2.0,
                                                   direction=(0.0, 0.0, 1.0), theta_resolution=30, z_resolution=30)
        # 将结构化网格转换为非结构化四面体网格
        tetra_mesh = cylinderStructured.triangulate()
        self.model = tetra_mesh
        self.xyz_points_list = self.model.points
        # self.point_dataDic = {}
        self.vtu_filename = './test.vtu'

    def set_vtu_filename(self, vtu_filename):
        '''设置vtu路径'''
        self.vtu_filename = vtu_filename

    # 模型初始化设置 设置模型
    def set_model(self, mesh):
        self.model = mesh

    # 获取模型的节点xyz坐标列表
    def get_xyz_points_list(self):
        self.xyz_points_list = self.model.points
        return self.xyz_points_list

    '''设置节点的数据'''
    def set_points_data(self, dataName:str, pointDataList, number):
        # 创建点数据
        point_data = vtk.vtkDoubleArray()
        point_data.SetNumberOfComponents(number)  # 一个节点有三个方向的位移数据(x,y,z)
        point_data.SetName(dataName)  # 设置节点数据的名称
        # Temperature
        for data in pointDataList:
            if number ==1:
                point_data.InsertNextValue(data)
            elif number >1:
                point_data.InsertNextTuple(data)
        # grid.GetPointData().SetScalars(point_data)
        self.model.GetPointData().AddArray(point_data)

    '''写入.vtu文件'''
    def write_to_vtu(self):
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(self.vtu_filename)
        writer.SetInputData(self.model)
        writer.SetDataModeToAscii()  # 以纯文本形式将点数据写入.vtu文件
        writer.Write()






# 将三维直角坐标系下的（x, y, z）转换为柱坐标系下的（r, θ, z）
def xyz_to_rtz(xyz_point):
    # 计算极径 r
    r = np.sqrt(xyz_point[:, 0] ** 2 + xyz_point[:, 1] ** 2)

    # 计算极角 θ（以弧度表示）
    theta = np.arctan2(xyz_point[:, 1], xyz_point[:, 0])

    # 获取 z 值，这里假设 z 已经在xyz_grid的第2列
    z = xyz_point[:, 2]

    # 创建柱坐标系下的数组
    rtz_point = np.column_stack((r, theta, z))
    return rtz_point

# 将柱坐标系下的（r, θ, z）转换为三维直角坐标系下的（x, y, z）
def rtz_to_xyz(rtz_point):
    x = rtz_point[:, 0] * np.cos(rtz_point[:, 1])
    y = rtz_point[:, 0] * np.sin(rtz_point[:, 1])
    z = rtz_point[:, 2]
    # 创建直角坐标系下的数组
    xyz_point = np.column_stack((x, y, z))
    return xyz_point

'''整理rtz坐标点(下半圆柱点的z取绝对值)，用于计算拟合数据结果'''
def get_fitting_rtz(rtz_points_list):
    r = rtz_points_list[:, 0]
    theta = rtz_points_list[:, 1]
    z = np.abs(rtz_points_list[:, 2])
    fitting_rtz_points_list = np.column_stack((r, theta, z))
    return fitting_rtz_points_list


def get_strain_other_list(strain_axis1_list: np.ndarray, strain_axis2_list: np.ndarray) -> np.ndarray:
    '''根据已知的两个方向的应变数据，计算另一个方向的应变并返回'''
    # 泊松比 v
    v = 0.3
    strain_axis_other_list = (strain_axis1_list + strain_axis2_list) * (- v / (1-v))
    return strain_axis_other_list


def get_stress_list_by_strain(strain_list):
    '''根据应变，计算应力：stress = E(弹性模量) * strain'''
    E = 1.2e+10 # pa
    stress_list = strain_list * E
    return stress_list


# mm换成m
# xyz_grid[:, :] /= 1000
# print(xyz_grid[0,:])


'''读取模板Excel中的监测点 坐标'''
def get_rtz_from_excel():
    # 现在写死  1               2           3           4(<-端面)     5           6          7          8（<-环面）
    # list = [(0, 0, 55), (16, 0, 55), (32, 0, 55), (48, 0, 55), (55, 0, 54), (55, 0, 36), (55, 0, 18), (55, 0, 0)]
    template_file_path = '../CylinderData/Template.xlsx'
    # 使用上下文管理器读取 Excel 文件
    with pd.ExcelFile(template_file_path) as file:
        points_df = pd.read_excel(file, sheet_name="监测点坐标")  # 要读取的工作表名
    points_df["theta/mm"] = 0
    points_df = points_df[["r/mm", "theta/mm", "z/mm"]]
    # points_list = np.array(points_df)
    # known_points_list = np.array(list)
    known_points_list = np.array(points_df)
    return known_points_list

'''读取Excel中的数据，根据传入的列名读取指定列'''
def get_data_from_excel(columns_name_list):
    data_df = pd.read_excel('../CylinderData/综合20231023150155_3-columns_reset.xlsx')
    my_data_df = data_df.loc[:, columns_name_list]
    return np.array(my_data_df)


'''
把拟合出的数据，设置为vtu文件中点的数据
vtuModel：vtu对象
known_points_list：已知的监测点位置（r,θ,z）
known_data_name：数据的名称（温度、应变、应力）
known_data_list：已知的监测点的数据值（温度、应变、应力值）
'''
def eFunFitting_to_vtuModel(vtuModel:VtuModel, known_points_list, known_data_name, known_data_list, number):
    # 把vtuModel中的节点的坐标进行整理，xyz -> rtz -> rz
    rtz_points_list = xyz_to_rtz(vtuModel.get_xyz_points_list())
    fitting_rtz_points_list = get_fitting_rtz(rtz_points_list)  # 整理rtz坐标点(下半圆柱点的z取绝对值)，用于计算拟合数据结果
    rz_points_list = fitting_rtz_points_list[:, [0, 2]]
    # 将rz 、 known_data_list 和 known_data_list传入  get_temperature_from_rz() -> fitting_data_list
    fitting_data_list = get_temperature_from_rz(known_points_list, known_data_list, rz_points_list.T)
    # 输出拟合后的温度数据
    print("拟合后的数据:", fitting_data_list)
    # vtuModel.point_dataDic[known_data_name] = fitting_data_list
    '''
    for i in range(len(fitting_data_list)):
        # print(i, fitting_data_list[i], vtuModel.get_xyz_points_list()[i], vtuModel.get_point_list_from_bdf()[i].nid)
        if(fitting_data_list[i]>0 and fitting_data_list[i] <30):
            pass
            # print(i,fitting_data_list[i],vtuModel.get_xyz_points_list()[i],rz_points_list[i])
    '''
    # fitting_data_list *= 10**16 # 扩大10**16 倍，目的是为了区分明显
    # 将fitting_data_list 设置为点 数据对象.set_points_data()，同时设置数据名称known_data_name
    vtuModel.set_points_data(known_data_name, fitting_data_list, number)
    return fitting_data_list


def strain_stress_to_vtu_1HZ(vtuModel, view_points_dic):
    top_strain_r_list = view_points_dic.get("r方向应变").data[-1, :]   # TODO 端面r方向应变
    print(f"top_strain_r_list=====>>>>>>{top_strain_r_list}")
    top_strain_theta_list = view_points_dic.get("top_theta方向应变").data[-1, :]  # TODO 端面θ方向应变
    print(f"top_strain_theta_list=====>>>>>>{top_strain_theta_list}")
    # 计算另一个方向的应变
    top_strain_z_list = get_strain_other_list(top_strain_r_list, top_strain_theta_list)   # TODO 计算 端面z方向应变
    print(f"top_strain_z_list=====>>>>>>{top_strain_z_list}")
    surface_strain_theta_list = view_points_dic.get("surface_theta方向应变").data[-1, :]  # TODO 环面θ方向应变
    print(surface_strain_theta_list)
    surface_strain_z_list = view_points_dic.get("z方向应变").data[-1, :]    # TODO 环面z方向应变
    print(surface_strain_z_list)
    # 计算另一个方向的应变
    surface_strain_r_list = get_strain_other_list(surface_strain_theta_list, surface_strain_z_list)  # TODO 计算  环面r方向应变
    print(surface_strain_r_list)
    # 合并 端面和环面的r方向应变
    strain_r_list = np.concatenate((top_strain_r_list, surface_strain_r_list))
    print('r方向  八个监测点的应变')
    print(strain_r_list)
    # 合并 端面和环面的坐标
    top_known_points = view_points_dic.get("r方向应变").coordinates_list
    surface_known_points = view_points_dic.get("z方向应变").coordinates_list
    known_points = np.concatenate((top_known_points, surface_known_points))
    # 把数据拟合并插值所有数据，设置到vtuModel的节点数据中
    fitting_strain_r = eFunFitting_to_vtuModel(vtuModel, known_points, 'r_strain', strain_r_list, number=1)

    strain_theta_list = np.concatenate((top_strain_theta_list, surface_strain_theta_list))
    print('θ方向  八个监测点的应变')
    print(strain_theta_list)
    # 把数据拟合并插值所有数据，设置到vtuModel的节点数据中
    fitting_strain_theta = eFunFitting_to_vtuModel(vtuModel, known_points, 'θ_strain', strain_theta_list, number=1)

    strain_z_list = np.concatenate((top_strain_z_list, surface_strain_z_list))
    print('z方向  八个监测点的应变')
    print(strain_z_list)
    # 把数据拟合并插值所有数据，设置到vtuModel的节点数据中
    fitting_strain_z = eFunFitting_to_vtuModel(vtuModel, known_points, 'z_strain', strain_z_list, number=1)

    # r-θ-z三个方向的应变同时设置
    strain_rtz_list = np.column_stack((fitting_strain_r.T, fitting_strain_theta.T, fitting_strain_z.T))
    # print('rθz三个方向 应变组合')
    # print(strain_rtz_list)
    vtuModel.set_points_data("r_θ_z_strain", strain_rtz_list, 3)

    # 根据应变strain 计算应力stress，并设置节点数据
    stress_r_list = get_stress_list_by_strain(fitting_strain_r)
    # print("r方向 应力")
    # print(stress_r_list)
    vtuModel.set_points_data("r_stress", stress_r_list, 1)

    stress_theta_list = get_stress_list_by_strain(fitting_strain_theta)
    # print("θ方向 应力")
    # print(stress_theta_list)
    vtuModel.set_points_data("θ_stress", stress_theta_list, 1)

    stress_z_list = get_stress_list_by_strain(fitting_strain_z)
    # print("r方向 应力")
    # print(stress_z_list)
    vtuModel.set_points_data("z_stress", stress_z_list, 1)

    # r-θ-z三个方向的应变同时设置
    stress_rtz_list = np.column_stack((stress_r_list.T, stress_theta_list.T, stress_z_list.T))
    # print('rθz三个方向 应力组合')
    # print(stress_rtz_list)
    vtuModel.set_points_data("r_θ_z_stress", stress_rtz_list, 3)


if __name__ == '__main__':
    # bdf_filename = "../Data/CylinderDemo2_matel.bdf"
    bdf_filename = "../Data/CylinderDemo5.bdf"
    # vtu_filename = "../Data/cylinderdemo2_matel_out.vtu"
    vtu_filename = "../CylinderData/cylinderdemo7_out.vtu"

    # 把bdf文件中的节点、单元信息全部设置到vtuModel对象中
    vtuModel = VtuModel(bdf_filename, vtu_filename)

    # 已知的温度 监测点的坐标和数据
    known_points = get_rtz_from_excel()
    columns_name_list = ['温度1(℃)', '温度2(℃)', '温度3(℃)', '温度4(℃)', '温度5(℃)', '温度6(℃)',
                         '温度7(℃)', '温度8(℃)']
    known_temperatures_list= get_data_from_excel(columns_name_list)[558]

    # 把数据拟合并插值所有数据，设置到vtuModel的节点数据中
    eFunFitting_to_vtuModel(vtuModel, known_points, 'Temperature', known_temperatures_list, number=1)


    # 应变
    # 8个监测点  坐标
    known_points = get_rtz_from_excel()
    strain_columns_name_list = ['应变1(um/m)', '应变2(um/m)', '应变3(um/m)', '应变4(um/m)',
                                '应变5(um/m)', '应变6(um/m)', '应变7(um/m)', '应变8(um/m)',
                                '应变9(um/m)', '应变10(um/m)', '应变11(um/m)', '应变12(um/m)',
                                '应变13(um/m)', '应变14(um/m)', '应变15(um/m)', '应变16(um/m)']

    known_strain_list = get_data_from_excel(strain_columns_name_list)[558]

    strain_stress_to_vtu_1HZ(vtuModel, known_points, known_strain_list)


    # 将vtuModel对象，保存为.vtu文件
    vtuModel.write_to_vtu()
