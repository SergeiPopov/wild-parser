import SQL


class CSVMaker:
    def __init__(self, lite_connector: SQL.LiteConnector, csv_name=None, delimiter=';'):
        self.delimiter = delimiter
        self.lite_con = lite_connector
        if csv_name is not None:
            assert '.csv' in csv_name, "Имея файла должно содержать расширение .csv"
        self.csv_name = csv_name if csv_name else self.lite_con.db_name.replace('.db', '')
        self.save_rows()

    def get_selected_col(self):
        columns = {'card': ['card_catalog', 'card_url', 'card_name', 'card_brand'],
                   'certificate': ['certificate_url', 'certificate_number', 'certRegDate', 'certEndDate', 'FIO', 'org_name', 'org_email', 'org_mobile_number', 'org_other_contact', 'org_address']}
        selected_cols = list()
        for table, cols in columns.items():
            selected_cols_with_table = [table + '.' + col for col in cols]
            selected_cols.append(','.join(selected_cols_with_table))
        return ','.join(selected_cols)

    def get_all_certificate(self) -> list:
        all_cert_sql = f"""
        
        SELECT {self.get_selected_col()} FROM card
        INNER JOIN certificate ON card.card_id = certificate.card_id
        ORDER BY certificate.org_address DESC"""
        self.lite_con.cursor.execute(all_cert_sql)
        return self.lite_con.cursor.fetchall()

    def save_rows(self):
        rows = self.get_all_certificate()
        headers = self.delimiter.join(self.header_labels())
        with open(self.csv_name, 'w', encoding='utf8') as csv_file:
            csv_file.write(headers + '\n')
            for row in rows:
                csv_file.write(self.delimiter.join(list(map(str, row))) + '\n')

    def header_labels(self):
        return list(map(lambda x: x[0], self.lite_con.cursor.description))
