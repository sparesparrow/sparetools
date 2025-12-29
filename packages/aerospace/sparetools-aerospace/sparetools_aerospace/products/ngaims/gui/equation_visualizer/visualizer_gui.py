import signal

from NodeGraphQt import (
    NodeGraph,
    BaseNode, GroupNode, SubGraph
)
from Qt import QtCore, QtWidgets

from ngapy.bench.bench_manager import BenchManager
from sparetools_aerospace.products.ngaims.cmcf_bench_manager.cmcf_manager import CmcfManager
from sparetools_aerospace.products.ngaims.gui.equation_visualizer.cpp_interface import eq_type_map, get_input_name
from sparetools_aerospace.products.ngaims.gui.equation_visualizer.model_to_gui_interface import NodeDefinitionProvider


# All EQ nodes has out output (With some exceptions like Answer..)
class ImsEqNode(BaseNode):
    __identifier__ = 'nodes.ims_base'
    NODE_NAME = 'ims_base'

    def __init__(self):
        super(ImsEqNode, self).__init__()
        self.add_output('Out')


class ImsEqNodeWithInputs(ImsEqNode):
    # unique node identifier.
    __identifier__ = 'nodes.eq_node_with_inputs'

    # initial default node name.
    NODE_NAME = 'Arithmetic::Plus'

    def __init__(self, input_count, node_type):
        super(ImsEqNodeWithInputs, self).__init__()
        self.set_color(8, 60, 60)
        self.add_text_input('Value', 'Value')
        style = '''QLineEdit {
                          background:rgba(245,245,245,20);
                          border:1px solid rgb(45,45,45);
                          border-radius:3px;
                          color:rgba(255,255,255,255);
                          selection-background-color:rgba(255,255,255,100);
                        }'''
        self.widgets()['Value'].widget().setStyleSheet(style)
        for i in range(input_count):
            self.add_input(get_input_name(i, node_type))


class ImsEqGroupNode(GroupNode):
    # initial default node name.
    NODE_NAME = 'ImsEqGroupNode'

    def __init__(self, eq_model, edges, parent):
        self.eq_model = eq_model
        self.NODE_NAME = self.eq_model.name
        super(ImsEqGroupNode, self).__init__()
        self.edges = edges
        self.node_dict = {}
        sub_graph = SubGraph(parent, self, parent.node_factory)
        self.populate_sub_graph(sub_graph)

        # This is hidden in parent graph class and there is no other way to do it than accessing protected member.
        parent._sub_graphs[self.id] = sub_graph
        parent.widget.add_viewer(sub_graph.widget, self.name(), self.id)

        self.parent_widget = parent.widget
        self.sub_widget = sub_graph.widget
        sub_graph.auto_layout_nodes()
        sub_graph.fit_to_selection()

    def populate_sub_graph(self, sub_graph):
        # Create nodes
        for node_id, node_info in self.eq_model.nodes.items():
            new_node = ImsEqNodeWithInputs(node_info.input_count, node_info.type)
            sub_graph.add_node(new_node, selected=False, push_undo=False)
            if node_info.in_param:
                new_node.set_property('name', f'Param: {node_info.in_param} seq: {node_info.sequence}')
            else:
                new_node.set_property('name', f'{eq_type_map[node_info.type]} seq: {node_info.sequence}')
            self.node_dict[node_id] = new_node
        # Create edges
        for parent_index, child, sequence in self.edges:
            if child in self.node_dict and parent_index in self.node_dict:
                self.node_dict[parent_index].set_input(sequence, self.node_dict[child].output(0))


def get_eq_model():
    bench = BenchManager({'CMCF': CmcfManager(reset_dbs=False), })
    cmcf = bench.get_modules()['CMCF']
    bench.set_up()
    return cmcf.active_model.model.maintenance_model, cmcf.active_model.ate_cmcf


class AteUpdateWorker(QtCore.QRunnable):
    def __init__(self, ate_connection, eq_node_list):
        super(AteUpdateWorker, self).__init__()
        self.ate_connection = ate_connection
        self.eq_node_list = eq_node_list

    def run(self):
        for eq_node in self.eq_node_list:
            if self.is_sub_graph_visible(eq_node):
                updates = self.ate_connection.get_eq_node_values(eq_node.eq_model.ContId)
                if 'values' in updates.data:
                    for node_update in updates.data['values']:
                        eq_node.node_dict[node_update.dbId].set_property('Value', str(node_update.valFloat))
                    pass

    @staticmethod
    def is_sub_graph_visible(eq_node):
        return eq_node.parent_widget.currentIndex() == eq_node.parent_widget.indexOf(
            eq_node.sub_widget) and eq_node.is_expanded


class MainWindow(NodeGraph):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ate_model, self.ate = get_eq_model()
        model_provider = NodeDefinitionProvider(self.ate_model)
        eq_def, edge_def = model_provider.equations, model_provider.edges
        self.style_main_graph_widget()
        self.widget.show()
        self.threadpool = QtCore.QThreadPool()

        self.eq_node_list = []
        for equation in eq_def.values():
            eq_group_node = ImsEqGroupNode(equation, edge_def, self)
            self.eq_node_list.append(eq_group_node)
            self.add_node(eq_group_node)
            eq_group_node.set_property('name', f'{equation.name}')

        self.widget.setTabsClosable(False)
        self.auto_layout_nodes()
        self.fit_to_selection()
        self.periodic_job()

    def style_main_graph_widget(self):
        style = '''
            QTabBar::tab {
              background:rgb(29,29,29);
              border:0px solid black;
              color:rgba(255,255,255,255);
              min-width:10px;
              padding:10px 20px;
            }'''
        self.widget.setStyleSheet(style)

    def periodic_job(self):
        self.threadpool.start(AteUpdateWorker(self.ate, self.eq_node_list))
        QtCore.QTimer.singleShot(1000, self.periodic_job)


def run():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication()
    else:
        app = QtWidgets.QApplication.instance()
    MainWindow()
    app.exec_()


if __name__ == '__main__':
    run()
