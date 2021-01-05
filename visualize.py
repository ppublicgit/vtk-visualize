import numpy as np
import vtkmodules.all as vtk
import os


class VtkPointCloud(object):
    """
    Class to manage a vtkPolyData object
    """

    def __init__(self, max_num_pts=1e24):
        self.max_num_pts = max_num_pts
        self.pd = vtk.vtkPolyData()
        self.clear_points()
        mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)

    def add_point(self, obj):
        """
        Add a point
        """
        if self.pts.GetNumberOfPoints() < self.max_num_pts:
            pt_id = self.pts.InsertNextPoint([obj.x, obj.y, obj.z])
            self.obj.InsertNextValue(obj.val)
            self.ca.InsertNextCell(1)
            self.ca.InsertCellPoint(pt_id)
        else:
            print("Too Many Points!")
        self.ca.Modified()
        self.pts.Modified()
        self.obj.Modified()

    def clear_points(self):
        """
        Remove alll points
        """
        self.pts = vtk.vtkPoints()
        self.ca = vtk.vtkCellArray()
        self.obj = vtk.vtkDoubleArray()
        self.obj.SetName("Obj")
        self.pd.SetPoints(self.pts)
        self.pd.SetVerts(self.ca)
        self.pd.GetPointData().SetScalars(self.obj)


class Obj:
    def __init__(self, x, y, z, val):
        self.x = x
        self.y = y
        self.z = z
        self.val = val

def create_vtk(xx, yy, zz, points, min_val, max_val, num_colors):
    point_cloud = VtkPointCloud()
    for point in points:
        point_cloud.add_point(point)

    mapper = point_cloud.actor.GetMapper()
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(min_val, max_val)
    lut.SetHueRange(0.6667, 0.0)
    lut.Build()
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(min_val, max_val)

    cube = vtk.vtkCubeSource()
    xlen = 0.1
    ylen = 0.1
    zlen = 0.1
    cube.SetXLength(xlen)
    cube.SetYLength(ylen)
    cube.SetZLength(zlen)

    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(point_cloud.pd)
    point_cloud.pd.GetPointData().SetActiveScalars("Obj")
    point_cloud.pd.GetPointData().SetScalars(point_cloud.obj)
    glyph.SetSourceConnection(cube.GetOutputPort())
    glyph.ScalingOff()

    cb_actor = vtk.vtkScalarBarActor()
    cb_actor.SetTitle("Obj")
    cb_actor.SetLookupTable(lut)
    cb_actor.SetWidth(0.05)
    cb_actor.SetPosition(0.92, 0.15)
    cb_actor.VisibilityOn()
    lut.SetNumberOfColors(num_colors)

    glyph.Update()
    mapper.SetInputConnection(glyph.GetOutputPort())

    axes_actor = vtk.vtkAxesActor()
    axes_actor.SetXAxisLabelText("x")
    axes_actor.SetYAxisLabelText("y")
    axes_actor.SetZAxisLabelText("z")
    axes_actor.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes_actor.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes_actor.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    label_size = 20
    axes_actor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(label_size)
    axes_actor.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(label_size)
    axes_actor.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(label_size)

    renderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    renderer.AddActor(point_cloud.actor)
    renderer.AddActor(cb_actor)
    renderer.AddActor(axes_actor)

    renWin.Render()
    camera = vtk.vtkCamera()

    renderer.SetActiveCamera(camera)

    camera.SetParallelProjection(True)
    camera.SetPosition(20, 0, 0)
    iren.Start()


if __name__ == "__main__":

    xx = np.linspace(-10, 10, 42)
    yy = np.linspace(-10, 10, 42)
    zz = np.linspace(-10, 10, 42)

    def get_val(x,y,z):
        if x <= 5 and x>=-5  and np.sqrt(y**2+z**2) <= 3:
            val = 9.9
        else:
            val = 1
        return val

    points = []

    for x in xx:
        for y in yy:
            for z in zz:
                obj = Obj(x,y,z,get_val(x,y,z))
                points.append(obj)

    create_vtk(xx, yy, zz, points, 1, 10, 2)
