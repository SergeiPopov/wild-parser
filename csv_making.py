from CSVMaker import *
import SQL


if __name__ == '__main__':
    lite_con = SQL.LiteConnector('test_auto_created.db')
    CSVMaker(lite_con, 'test.csv')