import munch

from ngapy.bench.bench_manager import BenchManager
from sparetools_aerospace.products.ngaims.cmcf_bench_manager.cmcf_manager import CmcfManager


# Interface for translating CMCF LDI maintenance model into GUI model. It is here to abstract different models for
# ACMF and TCRF, which are not yet created.
# TODO: Create this interface for ACMF and TCRF. There should not be much or any differences.
# Output structure:
# equations {Id: (name, type, ContI, nodes {Id: (type, input_count, ContId, sequence, in_param)}}
# edges [ParentId, ChildId, Sequence]
class NodeDefinitionProvider:
    def __init__(self, database_model):
        self.equations = {eq['Id']: munch.munchify({'name': eq['Name'], 'type': eq['Type'], 'ContId': eq['ContId']})
                          for eq in sorted(database_model['Eq'].values(), key=lambda x: x['Sequence'])}

        for eq_id, values in self.equations.items():
            nodes = {}
            for node in sorted(database_model['Eq'][eq_id]['EqNodeOwnerEqNodes'], key=lambda x: x[0]['Sequence']):
                nodes[node[0]['Id']] = munch.munchify(
                    {'type': node[0]['Type'], 'input_count': len(node[0]['EqEdges']), 'ContId': node[0]['ContId'],
                     'sequence': node[0]['Sequence']})
                nodes[node[0]['Id']].in_param = None
                if node[0]['EqParamInSrcSelects']:
                    nodes[node[0]['Id']].in_param = \
                        node[0]['EqParamInSrcSelects'][0][0]['SrcSelectInParamInParams'][0][0]['LogicalName']

            values.nodes = nodes

        self.edges = [(edge['ParentId'], edge['ChildId'], edge['Sequence']) for edge in
                      sorted(database_model['EqEdge'], key=lambda x: x['Sequence'])]


if __name__ == '__main__':
    bench = BenchManager({'CMCF': CmcfManager(), })
    cmcf = bench.get_modules()['CMCF']
    bench.set_up()
    nodes = NodeDefinitionProvider(cmcf.active_model.model.maintenance_model)
