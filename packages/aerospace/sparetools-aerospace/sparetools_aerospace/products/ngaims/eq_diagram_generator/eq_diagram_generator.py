# **********************************************************************************************************************
# Generate EQ diagram form SLDB SQLite database
# author: Lukacovic, Peter H462543 refactoring stream_diagram_generator from Michele, H154382, 2020-01-16
# **********************************************************************************************************************
# input params:
# -d <filename> ... SQLite DB file...default AO_CS_SLDB.DB
# -o <path> ... output folder (folder must exist before execution)....default current directory
# -f <format> ... output format bmp/jpeg/png/pdf ... all supported formats from GraphViz ... default png
# -s <list_of_streams> ... user can select just several streams (empty list/no param = all streams
#
# **********************************************************************************************************************

import os
import sqlite3
import sys
from optparse import OptionParser

from graphviz import Digraph


class EquationDiagramGenerator:
    def __init__(self):
        self.processed = []

    def get_all_eqs(self, in_cursor, in_eqs):
        # ~ returns all/selected steams - in form on item with id, name and streamIdentifier
        print("... getting equations")
        sql = "SELECT Id, Name, RootNodeId FROM Eq"
        tmp_sql = '('
        if len(in_eqs) > 2:
            for item in in_eqs.split(','):
                tmp_sql = '{0}"{1}",'.format(tmp_sql, item.strip())
            tmp_sql = '{0})'.format(tmp_sql[:-1])
            sql = "{0} WHERE Name IN {1}".format(sql, tmp_sql)
                
        in_cursor.execute(sql)
        data = in_cursor.fetchall()
        return data
        
    def get_previous_nodes(self, in_cursor, in_diagram, parent_id):
        sql = '''Select EqType.Name, EqNode.Id, EqNode.Sequence   
                From EqEdge Join EqNode on EqEdge.ChildId = EqNode.Id 
                JOIN EqType ON EqNode.Type = EqType.Id
                where EqEdge.ParentId =  ?
                ORDER BY EqNode.Sequence'''

        # ~ print (47, SQL, targetObjectId)
        in_cursor.execute(sql, (parent_id, ))
        data_in = in_cursor.fetchall()
        data_out = []
        i = 0
        if len(data_in) > 0:
            for item in data_in:
                item_data = item[0]
                item_data = "{0}\nObjectId: {1}".format(item_data, item[1])
                item_data = "{0}\nSequence: {1}".format(item_data, item[2])

                detail = self.get_default_value(in_cursor, item[1])
                if detail is not None:
                    (data_type, val_int, val_float, val_text) = detail
                    if data_type == 1:
                        item_data = "{0}\nInt: {1}".format(item_data, val_int)
                    if data_type == 2:
                        item_data = "{0}\nFloat: {1}".format(item_data, val_float)
                    if data_type == 3:
                        item_data = "{0}\nText: {1}".format(item_data, val_text)

                in_diagram.node(str(item[1]), item_data, {'shape': 'box'})
                i = i + 1
                if [item[0], item[1], item[2]] not in self.processed:
                    self.processed.append([item[0], item[1], item[2]])
                    in_diagram.edge(str(item[1]), str(parent_id), label="InputNo: {0}".format(item[2]))
                
                    self.get_previous_nodes(in_cursor, in_diagram, item[1])

        else:
            return parent_id
            
        return data_out

    def get_default_value(self, in_cursor, node_id):
        sql = '''select EqDefault.DataType, EqDefault.ValInt, EqDefault.ValFloat, EqDefault.ValText 
            from EqDefault join EqLiteral on EqLiteral.EqDefaultId = EqDefault.Id
            where   EqLiteral.EqNodeId =   ?'''

        in_cursor.execute(sql, (node_id,))

        data = in_cursor.fetchone()
        return data

    def process_one_eq(self, in_cursor, eq, in_diagram):
        self.processed = []
        print("... processing equation: {0}".format(eq[1]))
        SQL = '''Select EqType.Name, EqNode.Id, EqNode.Sequence   
                    From EqNode JOIN EqType ON EqNode.Type = EqType.Id
                where EqNode.Id =  ?
                ORDER BY EqNode.Sequence'''

        in_cursor.execute(SQL, (eq[2], ))
        
        data = in_cursor.fetchone()
        if data is None:
            print('WARNING: Equation {0} does not associated any Node'.format(eq[0]))
            return -1
            
        (name, id_node, sequence) = data

        item_data = name
        item_data = "{0}\nObjectId: {1}".format(item_data, id_node)
        item_data = "{0}\nSequence: {1}".format(item_data, sequence)

        in_diagram.node(str(id_node), item_data, {'shape': 'box'})
                
        in_diagram.edge(str(id_node), 'END')
        
        self.get_previous_nodes(in_cursor,  in_diagram, str(id_node))
        
        return 0

    def process_data(self, in_db_path, in_eqs, in_output_format, in_output_path):

        db_connection = sqlite3.connect(in_db_path)
        db_cursor = db_connection.cursor()

        eqs = self.get_all_eqs(db_cursor, in_eqs)
        for eq in eqs:
            diagram = Digraph(comment=eq[1])
            diagram.graph_attr['rankdir'] = 'LR'
            diagram.node('END', eq[1], {'shape': 'box'})
            rst = self.process_one_eq(db_cursor, eq, diagram)
            
            if rst == 0:
                
                diagram.render('{2}{1}{0}'.format(eq[1], os.sep, in_output_path), format=in_output_format)
                os.remove('{2}{1}{0}'.format(eq[1], os.sep, in_output_path))
# ========================================== MAIN FUNCTION==============================================


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--dbFile", dest="dbfile", default="AO_CS_SLDB.DB", help="full path to SQLLite file")
    parser.add_option("-o", "--outputFolder", dest="outFolder", default=".", help="output folder for output files")
    parser.add_option("-f", "--outputFormat", dest="outFormat", default="png",
                      help="output format (bmp/jpeg/png/pdf), default: png")
    parser.add_option("-e", "--eqs", dest="eqs", default="",
                      help="list of equations (empty = get all equations), delimited by comma")
    (options, args) = parser.parse_args()

    if not os.path.exists(options.dbfile):
        print('SQLLite Database on path "{0}" does not exists'.format(options.dbfile))
        sys.exit(1)
        
    if not os.path.exists(options.outFolder):
        print('Output path "{0}" does not exists'.format(options.outFolder))
        sys.exit(2)    
        
    gen = EquationDiagramGenerator()
    gen.process_data(options.dbfile, options.eqs, options.outFormat, options.outFolder)
        