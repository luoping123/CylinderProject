import numpy as np
import pyvista as pv
''' 圆柱尺寸及网格自定义工具类'''
class CylinderCustomTool:
    def __init__(self, mesh):
        self.output = mesh  # Expected PyVista mesh type
        # default parameters
        self.kwargs = {
            'radius': np.linspace(0, 55, 10),
            'height': 2.0,
            'theta_resolution': 30,
            'z_resolution': 30,
            'direction':(0.0, 0.0, 1.0)
        }
        self.radius_lenth = 55
        self.radius_resolution = 100

    def __call__(self, param, value):
        if param == 'radius_lenth':
            self.radius_lenth = int(value)
            self.kwargs['radius'] = np.linspace(0, self.radius_lenth, self.radius_resolution)
        elif param == 'radius_resolution':
            self.radius_resolution = int(value)
            self.kwargs['radius'] = np.linspace(0, self.radius_lenth, self.radius_resolution)
        elif param == 'theta_resolution':
            self.kwargs[param] = int(value)
        else:
            self.kwargs[param] = int(value)
        self.kwargs['direction'] = (0.0, 0.0, 1.0)
        self.update()

    def update(self):
        # 在这里调用你的模拟
        result = pv.CylinderStructured(**self.kwargs)

        # 如果self.output是UnstructuredGrid，则将result转换为UnstructuredGrid
        if isinstance(self.output, pv.UnstructuredGrid):
            result = result.triangulate()

        self.output.copy_from(result)
        return
    def getModel(self):
        return self.output

''' 使用示例
cylinderStructured = pv.CylinderStructured(radius=np.linspace(0, 55, 100), height=2.0,direction=(0.0, 0.0, 1.0), theta_resolution=30, z_resolution=30)
# 将结构化网格转换为非结构化四面体网格
tetra_mesh = cylinderStructured.triangulate()
engine = CylinderCustomTool(tetra_mesh)

p = pv.Plotter()
tetra_mesh_actor = p.add_mesh(tetra_mesh, show_edges=True,
           # style="points",
           )



p.add_slider_widget(
    callback=lambda value: engine('radius_lenth', value),
    rng=[30, 100],
    value=55,
    title="radius",
    pointa=(0.025, 0.1),
    pointb=(0.31, 0.1),
    # fmt='%d',  # 设置滑块的值为整数
    style='modern',
)
p.add_slider_widget(
    callback=lambda value: engine('height', value),
    rng=[30, 200],
    value=110,
    title="height",
    pointa=(0.35, 0.1),
    pointb=(0.64, 0.1),
    # fmt='%d',  # 设置滑块的值为整数
    style='modern',
)
p.add_slider_widget(
    callback=lambda value: engine('radius_resolution', value),
    rng=[3, 20],
    value=10,
    title="r_resolution",
    pointa=(0.025, 0.5),
    pointb=(0.31, 0.5),
    # fmt='%d',  # 设置滑块的值为整数
    style='modern',
)
p.add_slider_widget(
    callback=lambda value: engine('theta_resolution', int(value)),
    rng=[3, 60],
    value=30,
    title="theta_resolution",
    pointa=(0.67, 0.1),
    pointb=(0.98, 0.1),
    # fmt='%d',  # 设置滑块的值为整数
    style='modern',
)
p.add_slider_widget(
    callback=lambda value: engine('z_resolution', int(value)),
    rng=[3, 60],
    value=30,
    title="z_resolution",
    pointa=(0.025, 0.3),
    pointb=(0.31, 0.3),
    # fmt='%d',  # 设置滑块的值为整数
    style='modern',
)

p.add_axes(  # TODO 左下角坐标轴
    line_width=5,
    color='white',
    cone_radius=0.6,
    shaft_length=0.7,
    tip_length=0.3,
    ambient=0.5,
    label_size=(0.4, 0.16),
)
p.show()


'''